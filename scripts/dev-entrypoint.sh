#!/bin/sh
set -eu

workspace=/workspace/Vinolog
uid="${VINLOG_UID:-1000}"
gid="${VINLOG_GID:-1000}"

case "$uid" in *[!0-9]*|'') echo 'VINLOG_UID must be numeric.' >&2; exit 1 ;; esac
case "$gid" in *[!0-9]*|'') echo 'VINLOG_GID must be numeric.' >&2; exit 1 ;; esac

if ! getent group "$gid" >/dev/null; then
  groupadd -g "$gid" vinlog-host
fi
usermod -u "$uid" -g "$gid" -d "$HOME" node

mkdir -p "$HOME" "$workspace/node_modules" "$workspace/apps/web/.nuxt"
chown "$uid:$gid" "$HOME" "$workspace/node_modules"
chown -R "$uid:$gid" "$workspace/apps/web/.nuxt"

lock_hash="$(sha256sum "$workspace/package-lock.json" | cut -d ' ' -f 1)"
installed_hash="$(cat "$workspace/node_modules/.vinolog-lock-sha256" 2>/dev/null || true)"
if [ "$lock_hash" != "$installed_hash" ]; then
  chown -R "$uid:$gid" "$workspace/node_modules"
  echo 'Installing dependencies for the mounted workspace...'
  gosu "$uid:$gid" env HOME="$HOME" npm ci
  printf '%s\n' "$lock_hash" > "$workspace/node_modules/.vinolog-lock-sha256"
  chown "$uid:$gid" "$workspace/node_modules/.vinolog-lock-sha256"
fi

exec gosu "$uid:$gid" env HOME="$HOME" "$@"
