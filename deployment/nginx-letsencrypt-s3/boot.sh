#!/bin/bash

set -euo pipefail
LFS=$'\t\n'


nginx_pidfile=/run/nginx/nginx.pid

bucket=s3://cert.$public_hostname

bucketMissing() {
    ! aws s3 ls $bucket
}

pemMissing() {
    ! echo $pems | grep cert.pem
}

execNginx() {
    # generate https+proxy .conf
    export https_conf=1
    python /jentemplate /http.conf.in > /etc/nginx/conf.d/default.conf

    # install certbot cron job
    echo '4 1,13 * * *  certbot $certbot_flags renew --quiet' | crontab -u root -
    crond -l 2

    # exec nginx
    nginx -T
    exec nginx -g "daemon off;"
}

fetchCert() {
    aws s3 cp $bucket/letsencrypt /etc/letsencrypt --recursive
}

runCertbotAndPushCert() {
    # generate http .conf
    unset https_conf
    python /jentemplate /http.conf.in > /etc/nginx/conf.d/default.conf

    # run nginx in the background
    nginx

    # wait for nginx start
    sleep 8

    # run certbot
    certbot $certbot_flags certonly --webroot -w /usr/share/nginx/html \
        -n --agree-tos -m $certbot_email \
        --preferred-challenges http-01 \
        -d $public_hostname | grep Congratulations

    # copy certs to s3
    aws s3 cp /etc/letsencrypt $bucket/letsencrypt --recursive

    # kill nginx
    kill $(cat $nginx_pidfile)
}

if bucketMissing; then
    aws s3 mb $bucket
fi

# list bucket
pems=`aws s3 ls $bucket/letsencrypt/live/$public_hostname/ || true`

# has cert?
if pemMissing; then
    runCertbotAndPushCert
else
    # copy pems from s3
    fetchCert
fi

execNginx

# RUNNING.
