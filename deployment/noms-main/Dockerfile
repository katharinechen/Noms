# vim:set ft=dockerfile:
############################################################
## Begin multi-stage build
FROM corydodt/circus-base:0.4 as nomsmainstage1

ENV s1 /nomsmainstage1
ENV WORKON_HOME $s1/virtualenvs
ENV VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
ENV noms /opt/Noms

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

# use virutalenvwrapper to create our python3 virtualenv
RUN pip3 install -U pip wheel virtualenvwrapper
RUN bash -c ". /usr/local/bin/virtualenvwrapper.sh \
    && mkdir -vp $noms \
    && mkvirtualenv -a $noms -r $s1/requirements.txt noms \
    && add2virtualenv $noms /opt/Circusbase \
    && pip install -U pip"
RUN bundle install --gemfile $s1/Gemfile --path $s1/vendor/bundle


############################################################
## Stage 2
FROM corydodt/circus-base:0.4
ENV s1 /nomsmainstage1
COPY --from=nomsmainstage1 $s1 $s1

ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms
ENV WORKON_HOME $s1/virtualenvs
ENV VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3

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

RUN pip3 install virtualenvwrapper

RUN bash -c ". /usr/local/bin/virtualenvwrapper.sh \
    && mkdir -p $noms \
    && workon noms \
    && pip install --no-cache-dir -U circus"

RUN mkdir -p $noms

COPY ./00-noms.ini /etc/circus.d/

ENTRYPOINT [ "/bin/bash", "-c", ". /usr/local/bin/virtualenvwrapper.sh && workon --cd noms && circusd /etc/circus.ini" ]

CMD [ ]

EXPOSE 8080

# install all source
COPY . .

RUN node-sass static/scss/base.scss -o static/css
