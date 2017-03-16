#!/bin/bash

set -e 

bucket=s3://letsencrypt.$public_hostname

bucketExists() {
    aws s3 ls $bucket
}

pemExists() {
    echo $pems | grep cert.pem
}

execNginx() {
    # generate https+proxy .conf
    export https_conf=1
    python /j2.py /http.conf.in > /$public_hostname.conf

    # install certbot cron job
    echo '4 1,13 * * *  certbot $certbot_flags renew --quiet' > /etc/cron.d/01certbot

    # exec nginx
    nginx -T
    exec nginx -g "daemon off;"
}

fetchCert() {
    aws s3 cp $bucket/letsencrypt /etc/ --recursive
}

runCertbotAndPushCert() {
    # generate http .conf
    unset https_conf
    python /j2.py /http.conf.in > /$public_hostname.conf

    # run nginx in the background
    nginx
    nginx_pid=$?

    # wait for nginx start
    sleep 8

    # run certbot
    certbot $certbot_flags certonly --webroot -w /usr/share/nginx/html \
        -n --agree-tos -m corydodt@gmail.com \
        --preferred-challenges http-01 \
        -d $public_hostname | grep Congratulations

    # copy certs to s3
    aws s3 cp /etc/letsencrypt $bucket/ --recursive

    # kill nginx
    kill $nginx_pid

}

if ! bucketExists; then
    aws s3 mb $bucket
fi

# list bucket
pems=`aws s3 ls $bucket/letsencrypt/live/$public_hostname/`

# has cert?
if ! pemExists; then
    runCertbotAndPushCert
else
    # copy pems from s3
    fetchCert
fi

execNginx

# RUNNING.
