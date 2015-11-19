#!/usr/bin/env bash

set -e

SSH_HOST="54.154.20.84"
SSH_PORT="22"
SSH_USER="ubuntu"

while [[ $# > 1 ]]
do
  key="$1"

  case $key in 
    --private-key)
      PRIVATE_KEY="$2"
      shift
      ;;
    --ssh-user)
      SSH_USER="$2"
      shift
      ;;
    --ssh-host)
      SSH_HOST="$2"
      shift
      ;;
    --ssh-port)
      SSH_PORT="$2"
      shift
      ;;
    *)
  esac

shift
done

if [ -z "$PRIVATE_KEY" ]; then
  echo "--private-key is required"
  exit 1
fi

echo "Open ssh connection"
ssh -tt -o 'IdentitiesOnly yes' -i $PRIVATE_KEY -p$SSH_PORT "${SSH_USER}@${SSH_HOST}" 'bash -s' <<'ENDSSH'

  cd /home/ubuntu/removeme/foo/
  git pull origin debug
  buildozer -v android debug

  exit
ENDSSH

scp -o 'IdentitiesOnly yes' -i $PRIVATE_KEY -p$SSH_PORT "${SSH_USER}@${SSH_HOST}:/home/ubuntu/removeme/foo/bin/MyApplication-1.0-debug.apk" ~/Downloads
adb install -r ~/Downloads/MyApplication-1.0-debug.apk