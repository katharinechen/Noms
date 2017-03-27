#!/bin/bash

# Do database initialization if config collection doesn't have data yet

set -euo pipefail
LFS=$'\t\n'

rest="$@"

while ! nc -z "$NOMS_DB_HOST" 27017; do sleep 1.5; done

if [ ! -e '/.boot' ]; then
    echo "First-time run: Installing fresh config and secret_pair"
    noms-sample "$NOMS_DB_HOST" && touch /.boot
fi

if [ -n "$rest" ]; then
    echo $rest
    exec $rest
fi

