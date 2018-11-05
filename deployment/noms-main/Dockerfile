# vim:set ft=dockerfile:
############################################################
## Begin multi-stage build
FROM corydodt/circus-base:0.4 as nomsmainstage1

ENV s1 /nomsmainstage1

RUN apt update \
    && apt -y install \
        build-essential \
        libffi-dev \
        libssl-dev \
        ruby-dev \
        python3-dev \
        python3-pip \
        bundler

COPY ./Gemfile ./requirements.txt $s1/

RUN pip3 install -U pip wheel
RUN /usr/local/bin/pip3 wheel --wheel-dir $s1/wheels -r $s1/requirements.txt
RUN bundle install --gemfile $s1/Gemfile --path $s1/vendor/bundle


############################################################
## Stage 2
FROM corydodt/circus-base:0.4
ENV s1 /nomsmainstage1
COPY --from=nomsmainstage1 $s1 $s1

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms

WORKDIR $noms

RUN apt update \
    && apt -y install \
        ca-certificates \
        git \
        mongodb \
        netcat-openbsd \
        python3 \
        python3-pip \
        ruby \
        libssl1.0.0 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt clean \
    && apt autoclean

RUN pip3 install --no-cache-dir -U pip \
    && /usr/local/bin/pip3 install --force-reinstall --no-index --find-links=$s1/wheels $s1/wheels/*.whl

COPY ./00-noms.ini /etc/circus.d/

EXPOSE 8080

# install all source
COPY . .

RUN node-sass static/scss/base.scss -o static/css
