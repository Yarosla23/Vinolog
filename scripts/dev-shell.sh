#!/bin/sh
set -eu

if grep -q '^-----BEGIN OPENSSH PRIVATE KEY-----$' /run/secrets/github_ssh_key 2>/dev/null; then
  if [ "$(id -u)" -eq 0 ] && [ -e /workspace/Vinolog/.git ]; then
    exec gosu node env HOME=/workspace/Vinolog/.docker-home \
      GIT_SSH_COMMAND='ssh -i /run/secrets/github_ssh_key -o IdentitiesOnly=yes' /bin/sh "$@"
  fi
  exec env GIT_SSH_COMMAND='ssh -i /run/secrets/github_ssh_key -o IdentitiesOnly=yes' /bin/sh "$@"
fi

if [ "$(id -u)" -eq 0 ] && [ -e /workspace/Vinolog/.git ]; then
  exec gosu node env HOME=/workspace/Vinolog/.docker-home /bin/sh "$@"
fi

exec /bin/sh "$@"
