#!/bin/bash

# Do database initialization if first-time boot

set -euo pipefail
LFS=$'\t\n'

rest="$@"

while ! nc -z "$NOMS_DB_HOST" 27017; do sleep 1.5; done

if [ ! -e '/.boot' ]; then
    echo "First-time run: Installing fresh users and recipes"
    whisk sample && touch /.boot
fi

if [ -n "$rest" ]; then
    echo $rest
    exec $rest
fi

