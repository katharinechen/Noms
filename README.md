# Noms

Noms is a recipe app.

## Running noms

  1. Run `noms`

## Maintaining noms

- Run noms with noms-docker

- If you want to rebuild the docker images, you should do both of the
   following:

  1. Install https://github.com/sameersbn/docker-apt-cacher-ng

```
  docker pull sameersbn/apt-cacher-ng:latest 
  docker run --name apt-cacher-ng -d --restart=always \
    --publish 3142:3142 \
    --volume /srv/docker/apt-cacher-ng:/var/cache/apt-cacher-ng \
    sameersbn/apt-cacher-ng:latest
```

  Note that `apt-cacher-ng` is now a requirement to building the
  corydodt/noms-main image, which contains this implied dependency on
  apt-cacher-ng:

```
  RUN echo 'Acquire::HTTP::Proxy "http://172.17.0.1:3142";'$'\n''Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy
```
