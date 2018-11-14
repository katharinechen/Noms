# vim:set ft=dockerfile:
############################################################
## Begin multi-stage build
FROM corydodt/circus-base:0.5 as nomsmainstage1

ENV s1 /nomsmainstage1
ENV WORKON_HOME $s1/virtualenvs
ENV VIRTUALENVWRAPPER_PYTHON /usr/bin/python3
ENV noms /opt/Noms

# xxx - set VIRTUALENVWRAPPER_PYTHON to python3 or python as desired
# xxx - change WORKON_HOME if desired (e.g. to put envs somewhere that stage1 can copy them to stage2)

## once you have the virtual environment:
## - set PYTHONUSERBASE to WORKON_HOME/$env
## - invoke commands directly with PYTHONUSERBASE/bin/python (or set a VEPYTHON variable)
## - set PATH to include PYTHONUSERBASE/$env/bin
## - encourage the use of add2virtualenv or create pth files
## - encourage the use of cpvirtualenv to keep circus+circusbase and pth additions

RUN apt update \
    && apt -y install \
        build-essential \
        libffi-dev \
        libssl-dev \
        ruby-dev \
        python3-dev \
        python3-pip \
        ruby-bundler

COPY ./Gemfile ./requirements.txt $s1/

# use virutalenvwrapper to create our python3 virtualenv
RUN pip3 install -U pip virtualenvwrapper
RUN mkdir -vp $noms \
    && bash -c ". /usr/local/bin/virtualenvwrapper.sh \
    && mkvirtualenv -a $noms -r $s1/requirements.txt noms \
    && add2virtualenv $noms /opt/Circusbase \
    && pip install -U pip circus"
RUN bundle install --gemfile $s1/Gemfile --path $s1/vendor/bundle


############################################################
## Stage 2
FROM corydodt/circus-base:0.5
ENV s1 /nomsmainstage1
COPY --from=nomsmainstage1 $s1 $s1

ENV noms /opt/Noms
ENV WORKON_HOME $s1/virtualenvs

RUN apt update \
    && apt -y install \
        ca-certificates \
        git \
        mongodb \
        netcat-openbsd \
        python3 \
        python3-pip \
        ruby \
        ruby-bundler \
        libssl1.0.0 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
    && apt clean \
    && apt autoclean

ENV PYTHONUSERBASE ${WORKON_HOME}/noms
ENV PATH ${PYTHONUSERBASE}/bin:${PATH}:${noms}/bin
WORKDIR $noms

COPY ./00-noms.ini /etc/circus.d/

EXPOSE 8080
