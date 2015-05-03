CONTAINER_NAME = quay.io/kaniabi/baseimage
NAME = baseimage
VERSION = v1.2

.PHONY: build, publish

all: build

build:
	sudo docker build --rm -t latest -t latest -t $(CONTAINER_NAME):$(VERSION) .

publish:
	sudo docker login quay.io
	sudo docker pull
