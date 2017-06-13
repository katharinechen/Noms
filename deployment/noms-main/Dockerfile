# vim:set ft=dockerfile:
FROM corydodt/circus-base:0.1

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms

COPY ./Gemfile /
COPY ./requirements.txt /

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
        make \
        libffi-dev \
        openssl-dev \
        ruby-dev \
        python-dev \
    && apk add --no-cache \
        bash \
        ca-certificates \
        git \
        mongodb \
        netcat-openbsd \
        python \
        ruby \
        ruby-bundler \
    && bundle install --path /vendor/bundle/ \
    && pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -U -r /requirements.txt \
    && apk del build-dependencies

EXPOSE 8080

WORKDIR $noms
