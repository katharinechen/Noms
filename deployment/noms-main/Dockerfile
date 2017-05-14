# vim:set ft=dockerfile:
FROM alpine:edge

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms

COPY ./Gemfile /
COPY ./deployment/get-pip.py ./requirements.txt /

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
        g++ \
        libffi-dev \
        make \
        openssl-dev \
        ruby-dev \
        python-dev \
        linux-vanilla-dev \
        linux-headers \
    && apk add --no-cache \
        bash \
        ca-certificates \
        mongodb \
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

ENTRYPOINT ["circusd"]
CMD ["noms.circus.ini"]

WORKDIR $noms
