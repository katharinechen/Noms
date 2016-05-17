FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    python python-dev python-pip \
    libffi-dev libssl-dev \
    mongodb-clients
ENV noms /opt/Noms
ENV PATH $PATH:$noms/bin
ENV PYTHONPATH $noms
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8080

ENTRYPOINT ["bin/docker-init"]
CMD ["noms"]

WORKDIR $noms
ADD . $noms
