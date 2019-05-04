# vim:set ft=dockerfile:
############################################################
## Begin multi-stage build
FROM corydodt/circus-base:0.6.1 as nomsmainstage1

ENV s1 /nomsmainstage1
ENV noms /opt/Noms

RUN apt update \
    && apt -y install \
        build-essential \
        libffi-dev \
        libssl-dev \
        python3.7-dev

COPY ./package.json ./requirements.txt $s1/

RUN pip install -U httpie

RUN http get https://deb.nodesource.com/gpgkey/nodesource.gpg.key > $s1/nodesource.gpg.key

RUN pip install wheel \
    && pip wheel --wheel-dir $s1/wheels -r $s1/requirements.txt


############################################################
## Stage 2
FROM corydodt/circus-base:0.6.1
ENV s1 /nomsmainstage1 

COPY --from=nomsmainstage1 $s1 $s1

ENV noms /opt/Noms

RUN apt-key add $s1/nodesource.gpg.key \
  && echo "deb https://deb.nodesource.com/node_9.x xenial main" | \
    tee /etc/apt/sources.list.d/nodesource.list \
  && echo "deb-src https://deb.nodesource.com/node_9.x xenial main" | \
    tee -a /etc/apt/sources.list.d/nodesource.list

RUN apt update \
    && apt -y install \
        ca-certificates \
        git \
        mongodb \
        netcat-openbsd \
        nodejs \
        libssl1.0.0 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt clean \
    && apt autoclean

# install noms pip requirements
RUN pip install --no-index --find-links=$s1/wheels -r $s1/requirements.txt

ENV PATH ${noms}/node_modules/.bin:${noms}/bin:${PATH}
WORKDIR $noms

RUN cp $s1/package.json . && npm install

COPY ./00-noms.ini /etc/circus.d/

EXPOSE 8080

# install all source
COPY . .

RUN pylib=$(python -c 'from distutils.sysconfig import get_python_lib as p; print(p())') \
    && echo "/opt/Noms" > "$pylib/noms.pth"

RUN node-sass static/scss/base.scss -o static/css
