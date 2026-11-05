#!/usr/bin/env bash
set -euo pipefail
upload=${1:?upload directory}; commit=${2:?commit}; archive_sha=${3:?archive sha256}
[[ "$commit" =~ ^[a-f0-9]{40}$ && "$archive_sha" =~ ^[a-f0-9]{64}$ ]]
root=/root/spendgood-api
exec 9>"$root/.deploy.lock"
flock -n 9 || { echo '另一个部署正在执行' >&2; exit 1; }
cd "$upload"
printf '%s  release.tgz\n' "$archive_sha" | sha256sum -c -
test -f "$root/.env"
project=$(docker inspect --format='{{index .Config.Labels "com.docker.compose.project"}}' spendgood-api)
test -n "$project"
old_id=$(docker inspect --format='{{.Image}}' spendgood-api)
old_tag=spendgood-api:release-${old_id#sha256:}
docker tag "$old_id" "$old_tag"
new_tag=spendgood-api:release-$commit
old_size=$(docker image inspect --format='{{.Size}}' "$old_id")
# Every deployment has an isolated context; a failed build cannot change the live release.
release=$(mktemp -d "$root/release-$commit.XXXXXX")
tar xzf release.tgz -C "$release"
ln -s "$root/.env" "$release/services/api/.env"
ln -s "$root/secrets" "$release/services/api/secrets"
compose() { SPENDGOOD_IMAGE="$1" docker compose -p "$project" -f "$release/services/api/docker-compose.yml" "${@:2}"; }
changed=0
rollback() {
  rc=$?
  trap - EXIT
  if (( rc != 0 )); then
    echo "部署失败；上一镜像保留为 $old_tag"
    docker logs --tail 120 spendgood-api || true
    if (( changed )); then
      echo '正在自动回滚'
      compose "$old_tag" up -d --no-build --force-recreate
      echo "手动重试：SPENDGOOD_IMAGE=$old_tag docker compose -p $project -f $release/services/api/docker-compose.yml up -d --no-build --force-recreate"
    fi
  fi
  exit "$rc"
}
trap rollback EXIT
start=$SECONDS
# Build first, keeping the running container untouched until the new image exists.
compose "$new_tag" build api
new_size=$(docker image inspect --format='{{.Size}}' "$new_tag")
echo "BUILD_SECONDS=$((SECONDS-start)) OLD_IMAGE_BYTES=$old_size NEW_IMAGE_BYTES=$new_size"
# Verify native binaries before switching traffic.
docker run --rm --entrypoint node "$new_tag" --input-type=module -e 'import sharp from "sharp"; import {DatabaseSync} from "node:sqlite"; console.log(sharp.versions); new DatabaseSync(":memory:").close()'
docker run --rm --entrypoint /usr/bin/chromium "$new_tag" --version
changed=1
compose "$new_tag" up -d --build
sleep 60
for attempt in 1 2 3; do
  curl --retry 4 --retry-delay 3 --retry-all-errors -fsS --max-time 20 https://spend.snewbie.site/health.json > "$upload/health-$attempt.json"
  docker exec -i spendgood-api node --input-type=module -e 'let s="";for await(const c of process.stdin)s+=c;const h=JSON.parse(s);if(h.gitCommit!==process.argv[1])process.exit(1);console.log("HTTP 200 gitCommit="+h.gitCommit)' "$commit" < "$upload/health-$attempt.json"
  sleep 2
done
# Stable aliases retain the current and previous images. No prune of unrelated images.
docker tag "$old_tag" spendgood-api:previous
docker tag "$new_tag" spendgood-api:current
printf '%s\n' "$new_tag" > "$root/current-image"
printf '%s\n' "$old_tag" > "$root/previous-image"
ln -sfn "$release" "$root/current-release"
echo "DEPLOY_OK=$commit PREVIOUS_IMAGE=$old_tag"
