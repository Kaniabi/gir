CONTAINER_NAME = quay.io/kaniabi/baseimage
NAME = baseimage
VERSION = v1.1

.PHONY: build 

all: build

build:
	sudo docker login quay.io
	sudo docker build --rm -t latest -t latest -t $(CONTAINER_NAME):$(VERSION) .
	sudo docker pull
