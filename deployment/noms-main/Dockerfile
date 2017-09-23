# vim:set ft=dockerfile:
FROM corydodt/circus-base:0.1

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms

COPY ./Gemfile ./requirements.txt /

WORKDIR $noms

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
        make \
        libffi-dev \
        openssl-dev \
        ruby-dev \
        python-dev \
        linux-headers \
    && apk add --no-cache \
        bash \
        ca-certificates \
        git \
        mongodb \
        netcat-openbsd \
        python \
        ruby \
        ruby-bundler \
    && bundle install \
    && pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -U -r /requirements.txt \
    && apk del build-dependencies

COPY ./00-noms.ini /etc/circus.d/

EXPOSE 8080
