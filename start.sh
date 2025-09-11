#!/bin/bash

set -euo pipefail

printf "\n🔥 unzip-bot 🔥\n\n» Copyright (c) 2022 - present EDM115\n» MIT License\n\n»» Join @EDM115bots on Telegram\n»» Follow EDM115 on GitHub\n\n"

if [ -f .env ] && [[ ! "$DYNO" =~ ^worker.* ]]; then
  if grep -qE '^[^#]*=\s*("|'\''?)\s*\1\s*$' .env; then
    printf "❗ Some required vars are empty, please fill them unless you're filling them somewhere else (ex : Heroku, Docker Desktop)"
  else
    while IFS='=' read -r key value; do
      if [[ ! $key =~ ^# && -n $key ]]; then
        export "$key=$value"
      fi
    done <.env
  fi
fi

exec python -m unzipbot
