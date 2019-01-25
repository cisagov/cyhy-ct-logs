
# Cyber Hygiene Distributed

This project is a distributed implementation of the NCATS Cyber Hygiene system.

## Status

This project is currently under initial development.  The current focus is the implementation of certificate transparency monitoring.  

## Requirements

This project requires a [Docker](https://www.docker.com) installation.

## Installation and Execution

- Build the docker image:
  - `docker-compose build`
- Change the credentials in the following configuration files:
  - `secrets/admiral.yml`
  - `secrets/redis.conf`
  - `docker-compose.yml`
- Start the composition:
  - `docker-compose up`
  - alternately it can be started in [swarm mode](https://docs.docker.com/engine/swarm/): `docker stack deploy admiral --compose-file docker-compose.yml`
- Monitor the system:
  - http://localhost:5555
- Optional: Run the code tests
  - `docker-compose -f docker-compose-dev.yml run test`


## Development and Debugging

A separate `docker-compose-dev.yml` file is provided to support development and
testing.  Using this composition, a container can be started in a few different modes:

To start up an IPython session with a configured Celery app:

`docker-compose -f docker-compose-dev.yml run celery-shell`

To start up a development container with a bash shell:

`docker-compose -f docker-compose-dev.yml run bash`

To run all unit and system tests:

`docker-compose -f docker-compose-dev.yml run test`

Additional arguments can be passed to `pytest` when creating the container:

`docker-compose -f docker-compose-dev.yml run test -vs tests/scan_test.py`

To get a shell in a stopped or crashed container:

`docker run -it --rm --entrypoint=sh admiral`

## Monitoring
The following web services are started for monitoring the underlying components:

- CyHy API:        http://localhost:5000
- Celery Flower:   http://localhost:5555
- Mongo Express:   http://localhost:8081
- Redis Commander: http://localhost:8082
