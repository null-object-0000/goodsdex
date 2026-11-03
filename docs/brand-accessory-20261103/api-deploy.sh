#!/usr/bin/env bash
set -euo pipefail
cd /root/spendgood-api
exec 9>/tmp/spendgood-api-brand-deploy.lock
flock -n 9
old_hash=bb325dc7a4e695fbfd2ec3c6cd1da9481711017343407b5ef1b008aa7a8c15ac
new_hash=c3a7254bd04945fe25a32e1ecfaacda339babe637e0b76419fea3877d7e12695
old_image=sha256:d94a0de680aef1465918f0b3a2d5fbb21d57aa336f495808850f8f04c8c61509
[[ "$(docker inspect --format='{{.Image}}' spendgood-api)" = "$old_image" ]]
[[ "$(sha256sum src/catalog-files.mjs | cut -d' ' -f1)" = "$old_hash" ]]
[[ "$(docker exec spendgood-api sha256sum src/catalog-files.mjs | cut -d' ' -f1)" = "$old_hash" ]]
backup=$(mktemp -d /root/spendgood-api/.brand-api-compat.XXXXXX)
cp src/catalog-files.mjs "$backup/original.mjs"
base64 -d > "$backup/catalog-files.mjs" <<'MODULE'
aW1wb3J0IHtjcmVhdGVIYXNofSBmcm9tICdub2RlOmNyeXB0byc7CmltcG9ydCB7cmVhZEZpbGUsd3JpdGVGaWxlLG1rZGlyLHJlbmFtZX0gZnJvbSAnbm9kZTpmcy9wcm9taXNlcyc7CmltcG9ydCBwYXRoIGZyb20gJ25vZGU6cGF0aCc7CmNvbnN0IHBlbmRpbmc9bmV3IE1hcCgpOwpleHBvcnQgY29uc3QgZGlnZXN0PWJ1Zj0+Y3JlYXRlSGFzaCgnc2hhMjU2JykudXBkYXRlKGJ1ZikuZGlnZXN0KCdoZXgnKTsKZXhwb3J0IGZ1bmN0aW9uIHZhbGlkRGVzY3JpcHRvcihuYW1lLGQpIHsKICBpZighL14oPzppbmRleFwvW2EtejAtOV8tXSt8ZGV0YWlsXC9bYS1mMC05XXsyfXxnb29kc3xzb3VyY2VzLXN0YXR1cylcLmpzb24kLy50ZXN0KG5hbWUpfHwhZHx8IS9eW2EtZjAtOV17NjR9JC8udGVzdChkLnNoYTI1Nil8fCFOdW1iZXIuaXNTYWZlSW50ZWdlcihkLmNvdW50KXx8ZC5jb3VudDwwfHwhTnVtYmVyLmlzU2FmZUludGVnZXIoZC5ieXRlcyl8fGQuYnl0ZXM8MSl0aHJvdyBFcnJvcign5peg5pWI55qE5ZWG5ZOB5paH5Lu25riF5Y2VJyk7CiAgcmV0dXJuIGQ7Cn0KZXhwb3J0IGFzeW5jIGZ1bmN0aW9uIGRvd25sb2FkQ2F0YWxvZ0ZpbGUoc291cmNlcyxuYW1lLGRlc2NyaXB0b3IsZmV0Y2hJbXBsPWdsb2JhbFRoaXMuZmV0Y2gpIHsKICB2YWxpZERlc2NyaXB0b3IobmFtZSxkZXNjcmlwdG9yKTsKICBsZXQgZXJyb3I7CiAgZm9yKGNvbnN0IHNvdXJjZSBvZiBzb3VyY2VzKXRyeSB7CiAgICBjb25zdCByZXM9YXdhaXQgZmV0Y2hJbXBsKGAke3NvdXJjZS5yZXBsYWNlKC9cLyQvLCcnKX0vYmxvYnMvJHtkZXNjcmlwdG9yLnNoYTI1Nn0uanNvbmAse3NpZ25hbDpBYm9ydFNpZ25hbC50aW1lb3V0KDI1MDAwKX0pOwogICAgaWYoIXJlcy5vayl0aHJvdyBFcnJvcihgSFRUUCAke3Jlcy5zdGF0dXN9YCk7CiAgICBjb25zdCBidWY9QnVmZmVyLmZyb20oYXdhaXQgcmVzLmFycmF5QnVmZmVyKCkpOwogICAgaWYoYnVmLmxlbmd0aCE9PWRlc2NyaXB0b3IuYnl0ZXN8fGRpZ2VzdChidWYpIT09ZGVzY3JpcHRvci5zaGEyNTYpdGhyb3cgRXJyb3IoJ+WVhuWTgeaWh+S7tiBTSEEtMjU2IOS4jeespicpOwogICAgcmV0dXJuIGJ1ZjsKICB9Y2F0Y2goZSl7ZXJyb3I9ZTt9CiAgdGhyb3cgZXJyb3J8fEVycm9yKCfmsqHmnInllYblk4HmlbDmja7mupAnKTsKfQpleHBvcnQgYXN5bmMgZnVuY3Rpb24gcmVhZENhdGFsb2dGaWxlKHJvb3QsbmFtZSxkZXNjcmlwdG9yKSB7CiAgdmFsaWREZXNjcmlwdG9yKG5hbWUsZGVzY3JpcHRvcik7CiAgY29uc3QgdGFyZ2V0PXBhdGguam9pbihyb290LG5hbWUpOwogIHRyeSB7Y29uc3QgYnVmPWF3YWl0IHJlYWRGaWxlKHRhcmdldCk7aWYoZGlnZXN0KGJ1Zik9PT1kZXNjcmlwdG9yLnNoYTI1NilyZXR1cm4gYnVmO31jYXRjaChlKXtpZihlLmNvZGUhPT0nRU5PRU5UJyl0aHJvdyBlO30KICBpZihwZW5kaW5nLmhhcyh0YXJnZXQpKXJldHVybiBwZW5kaW5nLmdldCh0YXJnZXQpOwogIGNvbnN0IHRhc2s9KGFzeW5jKCk9PnsKICAgIGNvbnN0IHNvdXJjZXM9SlNPTi5wYXJzZShhd2FpdCByZWFkRmlsZShwYXRoLmpvaW4ocm9vdCwnc291cmNlcy5qc29uJyksJ3V0ZjgnKSk7CiAgICBjb25zdCBidWY9YXdhaXQgZG93bmxvYWRDYXRhbG9nRmlsZShzb3VyY2VzLG5hbWUsZGVzY3JpcHRvcik7CiAgICBhd2FpdCBta2RpcihwYXRoLmRpcm5hbWUodGFyZ2V0KSx7cmVjdXJzaXZlOnRydWV9KTthd2FpdCB3cml0ZUZpbGUodGFyZ2V0KycudG1wJyxidWYpO2F3YWl0IHJlbmFtZSh0YXJnZXQrJy50bXAnLHRhcmdldCk7cmV0dXJuIGJ1ZjsKICB9KSgpLmZpbmFsbHkoKCk9PnBlbmRpbmcuZGVsZXRlKHRhcmdldCkpOwogIHBlbmRpbmcuc2V0KHRhcmdldCx0YXNrKTtyZXR1cm4gdGFzazsKfQo=
MODULE
[[ "$(sha256sum "$backup/catalog-files.mjs" | cut -d' ' -f1)" = "$new_hash" ]]
docker tag "$old_image" spendgood-api:brand-base-20261103
cat > "$backup/Dockerfile" <<DOCKERFILE
FROM spendgood-api:brand-base-20261103
COPY catalog-files.mjs /app/src/catalog-files.mjs
DOCKERFILE
docker build -t spendgood-api:brand-compat "$backup"
docker run --rm --entrypoint node spendgood-api:brand-compat --check src/catalog-files.mjs
rollback(){
 cp "$backup/original.mjs" src/catalog-files.mjs
 docker tag "$old_image" spendgood-api:local
 docker compose up -d --no-build --force-recreate api
}
trap 'rc=$?; if [ "$rc" -ne 0 ]; then rollback; fi; exit "$rc"' EXIT
cp "$backup/catalog-files.mjs" src/catalog-files.mjs
docker tag spendgood-api:brand-compat spendgood-api:local
docker compose up -d --no-build --force-recreate api
for attempt in $(seq 1 15); do
 if docker exec spendgood-api node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"; then
  docker exec spendgood-api sha256sum src/catalog-files.mjs
  printf 'backup=%s\n' "$backup"
  exit 0
 fi
 sleep 2
done
exit 1
