#!/bin/bash

# run the image's command, then wait 10 minutes

set -euo pipefail
LFS=$'\t\n'

"$@"

sleep 600
