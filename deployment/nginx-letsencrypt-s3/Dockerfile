# vim:set ft=dockerfile:
FROM alpine:3.5

RUN mkdir -p /usr/share/nginx/html /run/nginx

COPY ./deployment/get-pip.py \
     ./deployment/nginx-letsencrypt-s3/requirements-certbot.txt \
     ./deployment/nginx-letsencrypt-s3/*.sh \
     ./deployment/nginx-letsencrypt-s3/http.conf.in \
    /

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
        g++ \
        libffi-dev \
        openssl-dev \
        python-dev \
    && apk add --no-cache \
        bash \
        ca-certificates \
        net-tools \
        nginx \
        openssl \
        python \
    && python /get-pip.py \
    && pip install --no-cache-dir -U pip \
    && pip install -U --no-cache-dir -r /requirements-certbot.txt \
    && rm /get-pip.py \
    && apk del build-dependencies

COPY $buildd/* /

CMD ["bash", "/boot.sh"]
