#!/usr/bin/env bash
# Retry the already built and native-module-verified immutable CI image.
set -euo pipefail
root=/root/spendgood-api
commit=aac48fdb47e7cdc8f717397e24055b2ce1ef4707
release=/root/spendgood-api/release-aac48fdb47e7cdc8f717397e24055b2ce1ef4707.NVB61k
new_tag=spendgood-api:release-$commit
exec 9>"$root/.deploy.lock"
flock -n 9
old_id=$(docker inspect --format='{{.Image}}' spendgood-api)
old_tag=spendgood-api:release-${old_id#sha256:}
docker tag "$old_id" "$old_tag"
project=$(docker inspect --format='{{index .Config.Labels "com.docker.compose.project"}}' spendgood-api)
compose() { SPENDGOOD_IMAGE="$1" docker compose -p "$project" -f "$release/services/api/docker-compose.yml" "${@:2}"; }
changed=0
rollback() {
  rc=$?; trap - EXIT
  if (( rc != 0 && changed )); then
    echo "READINESS_FAILED; rolling back to $old_tag"
    compose "$old_tag" up -d --no-build --force-recreate
  fi
  exit "$rc"
}
trap rollback EXIT
compose "$new_tag" build api
docker run --rm --entrypoint node "$new_tag" --input-type=module -e 'import sharp from "sharp"; import {DatabaseSync} from "node:sqlite"; console.log(sharp.versions.vips);new DatabaseSync(":memory:").close()'
docker run --rm --entrypoint /usr/bin/chromium "$new_tag" --version
docker image inspect "$new_tag" >/dev/null
changed=1
compose "$new_tag" up -d --no-build --force-recreate
ready=0
for attempt in $(seq 1 60); do
  if docker exec spendgood-api node --input-type=module -e 'const r=await fetch("http://127.0.0.1:8080/health.json",{signal:AbortSignal.timeout(1500)});const h=await r.json();if(!r.ok||!h.ok||h.gitCommit!==process.argv[1])process.exit(1)' "$commit" >/dev/null 2>&1; then
    ready=1; echo "READY_AFTER_ATTEMPT=$attempt"; break
  fi
  sleep 5
done
test "$ready" = 1
for attempt in 1 2 3; do
  curl --retry 4 --retry-delay 3 --retry-all-errors -fsS --max-time 20 https://spend.snewbie.site/health.json > "$release/lineage-health-$attempt.json"
  docker exec -i spendgood-api node --input-type=module -e 'let s="";for await(const c of process.stdin)s+=c;const h=JSON.parse(s);if(!h.ok||h.gitCommit!==process.argv[1])process.exit(1);console.log("HTTP 200 gitCommit="+h.gitCommit)' "$commit" < "$release/lineage-health-$attempt.json"
  sleep 2
done
docker tag "$old_tag" spendgood-api:previous
docker tag "$new_tag" spendgood-api:current
printf '%s\n' "$new_tag" > "$root/current-image"
printf '%s\n' "$old_tag" > "$root/previous-image"
ln -sfn "$release" "$root/current-release"
echo "DEPLOY_OK=$commit PREVIOUS_IMAGE=$old_tag"
