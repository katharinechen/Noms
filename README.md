# Noms

Noms is a recipe app.

## Running noms

  1. Run `noms`

## Maintaining noms

  1. Install `docker-apt-cacher-ng` (see below)

  2. Run noms with `noms-docker up`

  3. If you want to rebuild the docker images, run: `noms-docker up --build`

### Docker apt-cacher-ng

This service greatly speeds up repeated builds of noms, and is required to
build noms.

From https://github.com/sameersbn/docker-apt-cacher-ng:

```
  docker pull sameersbn/apt-cacher-ng:latest 
  docker run --name apt-cacher-ng -d --restart=always \
    --publish 3142:3142 \
    --volume /srv/docker/apt-cacher-ng:/var/cache/apt-cacher-ng \
    sameersbn/apt-cacher-ng:latest
```

