#!/bin/bash

set -e 

first () {
    # schedule certbot to run, and exec off to nginx

    cron
    atd
    echo 'bash /certbot-nomsbook.sh second' | at now + 1min
    exec nginx -g "daemon off;"
}

second () {
    # get a new cert with certbot, install the ssl config file, install the
    # renewal cron job

    certbot renew || certbot certonly --webroot -w /usr/share/nginx/html \
        -n --agree-tos -m corydodt@gmail.com \
        --preferred-challenges http-01 \
        -d nomsbook.com

    mv /etc/nginx/conf.d/nomsbook.conf.ssl /etc/nginx/conf.d/nomsbook.conf
    kill -HUP 1; nginx -T
    echo '1,13 * * * *  certbot renew' > /etc/cron.d/01certbot
}

"$@"
