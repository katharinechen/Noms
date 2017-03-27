# vim:set ft=dockerfile:
FROM alpine:3.5

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms

COPY ./Gemfile /
COPY ./deployment/get-pip.py ./requirements.txt /

RUN echo 'http://dl-3.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache --virtual build-dependencies \
        g++ \
        libffi-dev \
        make \
        openssl-dev \
        ruby-dev \
        python-dev \
    && apk add --no-cache \
        bash \
        ca-certificates \
        mongodb-tools \
        netcat-openbsd \
        python \
        ruby \
        ruby-bundler \
    && bundle install --path /vendor/bundle/ \
    && python /get-pip.py \
    && pip install --no-cache-dir -U pip \
    && pip install -U --no-cache-dir -r /requirements.txt \
    && rm /get-pip.py \
    && apk del build-dependencies

EXPOSE 8080

COPY ./deployment/noms-main/boot.sh /boot.sh
ENTRYPOINT ["bash", "/boot.sh"]
CMD ["noms"]

WORKDIR $noms
