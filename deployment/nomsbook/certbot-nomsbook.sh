#!/bin/bash

set -e 

. $noms/env


first () {
    # schedule certbot to run, and exec off to nginx

    conf="server_name $NOMS_HOSTNAME;"
    echo $conf > /hostname.conf

    cron
    atd
    echo 'bash /certbot-nomsbook.sh second' | at now + 1min
    exec nginx -g "daemon off;"
}


second () {
    # get a new cert with certbot, install the ssl config file, install the
    # renewal cron job

    certbot $NOMS_CERTBOT_FLAGS certonly --webroot -w /usr/share/nginx/html \
        -n --agree-tos -m corydodt@gmail.com \
        --preferred-challenges http-01 \
        -d $NOMS_HOSTNAME | grep Congratulations

    conf2="ssl_certificate /etc/letsencrypt/live/$NOMS_HOSTNAME/fullchain.pem; 
           ssl_certificate_key /etc/letsencrypt/live/$NOMS_HOSTNAME/privkey.pem;
           if (\$scheme != "https") { return 301 https://\$host\$request_uri; }
           listen 443 ssl;
           "
    echo $conf2 >> /hostname.conf
    kill -HUP 1; nginx -T

    echo '1,13 * * * *  . $noms/env && certbot $NOMS_CERTBOT_FLAGS renew' > /etc/cron.d/01certbot
}


"$@"
