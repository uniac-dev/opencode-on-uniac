#!/bin/sh
set -eu
umask 077

mkdir -p /data/workspace /data/config/opencode /data/data /data/state /data/cache
if [ ! -f /data/config/opencode/opencode.json ]; then
  cp /etc/uniac-opencode.json /data/config/opencode/opencode.json
fi
if [ ! -s /data/server-password ]; then
  head -c 36 /dev/urandom | base64 > /data/server-password
fi
chmod 600 /data/server-password
OPENCODE_PASSWORD="$(cat /data/server-password)"
export OPENCODE_PASSWORD

export XDG_CONFIG_HOME=/data/config
export XDG_DATA_HOME=/data/data
export XDG_STATE_HOME=/data/state
export XDG_CACHE_HOME=/data/cache
cd /data/workspace
exec opencode serve --hostname 0.0.0.0 --port 4096
