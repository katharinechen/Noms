# vim:set ft=dockerfile:
FROM corydodt/circus-base:0.3-ubuntu

ENV noms /opt/Noms

WORKDIR $noms

COPY ./package.json ./Gemfile ./requirements.txt /

RUN pip install httpie

## # Ubuntu's node is too old so we install a newer version
## RUN apt update \
##   && apt -y install apt-transport-https \
##   && http get https://deb.nodesource.com/gpgkey/nodesource.gpg.key | \
##     apt-key add - \
##   && echo "deb https://deb.nodesource.com/node_9.x xenial main" | \
##     tee /etc/apt/sources.list.d/nodesource.list \
##   && echo "deb-src https://deb.nodesource.com/node_9.x xenial main" | \
##     tee -a /etc/apt/sources.list.d/nodesource.list \
##   && apt clean \
##   && apt autoclean

# install deb (OS) packages - required files at runtime
RUN apt -y update \
    && apt -y install \
       git \
       mongodb-clients \
       netcat \
##        nodejs \
       python-pip \
       rlwrap \
       vim \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt clean \
    && apt autoclean

# install dev-only packages in a separate layer while we install pip software
RUN apt update && apt -y install \
       libffi-dev \
       libssl-dev \
       python-dev \
       ruby-dev \
    && gem install bundler \
    && bundle install \
    && pip install -U pip \
    && /usr/local/bin/pip --no-cache-dir install -r /requirements.txt \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt -y remove \
       libffi-dev \
       libssl-dev \
       python-dev \
       ruby-dev \
    && apt clean \
    && apt autoclean

# shell environment
ENV PATH $PATH:$noms/bin:/opt/node_modules/.bin
ENV PYTHONPATH=$noms

COPY ./00-noms.ini /etc/circus.d/

EXPOSE 8080

# install all source
COPY . .
