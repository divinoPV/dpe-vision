SHELL := /bin/bash
.DEFAULT_GOAL = help

COMPOSE = docker compose
FILE = -f docker-compose.yml
EXEC = ${COMPOSE} exec
RUN = ${COMPOSE} run

.PHONY: help
# Show this help message
help:
	@cat $(MAKEFILE_LIST) | docker run --rm -i xanders/make-help

.PHONY: up
# Kill all containers, rebuild and up them
up: kill
	${COMPOSE} ${FILE} up -d --build

.PHONY: kill
# Kill all containers
kill:
	${COMPOSE} kill $$(docker ps -q) || true

.PHONY: stop
# Stop all containers
stop:
	${COMPOSE} stop

.PHONY: rm
# Remove all containers
rm:
	${COMPOSE} rm -f

.PHONY: sr
# Stop and remove all containers
sr: stop rm

.PHONY: purge
# Stop and remove all containers and prune volumes, networks, containers and images
purge:
	docker stop $$(docker ps -aq)
	docker rm $$(docker ps -aq)
	docker volume prune -f
	docker network prune -f
	docker container prune -f
	docker image prune -f

.PHONY: logs-client
# Prompt logs of container
logs-client:
	docker logs --follow dpe_vision-client-container

.PHONY: logs-api
# Prompt logs of container
logs-api:
	docker logs --follow dpe_vision-api-container

.PHONY: ps
# List active containers
ps:
	${COMPOSE} ps -a

.PHONY: perm
# Fix permissions of all files
perm:
	sudo chown -R www-data:$(USER) .
	sudo chmod -R g+rwx .

.PHONY: restart
# Restart all containers correctly
restart:
	clear
	make perm sr up logs

# Container internal execution

.PHONY: client
# Enter in client container
client:
	${EXEC} dpe_vision-client-service ${SHELL}

.PHONY: mlops
# Enter in mlops container
mlops:
	${EXEC} dpe_vision-mlops-service ${SHELL}

.PHONY: api
# Enter in api container
api:
	${EXEC} dpe_vision-api-service ${SHELL}

# MLOPS - commands

.PHONY: mlops-install
# Install mlops package
mlops-install:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "pip install -e .

.PHONY: mlops-requirements
# Install mlops requirements
mlops-requirements:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "pip install -r requirements.txt"

.PHONY: mlops-train
# Run mlops train
mlops-train:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "python src/zenml_train.py"

.PHONY: mlops-predict
# Run mlops predict
mlops-predict:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "python src/zenml_predict.py"

.PHONY: mlops-full
# Run mlops full
mlops-full:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "python src/zenml_full.py"

.PHONY: mlops-up
# Run mlops up
mlops-up:
	${EXEC} dpe_vision-mlops-service /bin/bash -c "zenml up --ip-address 0.0.0.0 --port 8237"
