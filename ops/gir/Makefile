CONTAINER_NAME = quay.io/kaniabi/gir
NAME = gir
VERSION = v0.2.3

.PHONY: build run bash rm

all: build

build:
	sudo docker build --rm -t latest -t $(CONTAINER_NAME):$(VERSION) .

run:
	sudo docker run -p 80:80
	    -v /vagrant/gir/log:/gir/log
	    -e GIR_REDIS_URL=redis://:enderman@45.55.243.17:5102/0
	    -e GIR_SLACK_ROOM=#bos-ama
	    -e GIR_SLACK_TOKEN=xoxb-3724390083-OaNvuxp0CbYdo0fiy5kPBcWE
	    -e GIR_FLASK_PORT=80
	    -e GIR_SLACK_USER=gir
	    -e GIR_SLACK_HOST=docker
	    -e GIR_STATIC_URL=http://188.226.245.90/static/
	    -e GIR_DEBUG=true
	    -e DEBUG=true
	    --rm=true
	    --name $(NAME)
	    $(CONTAINER_NAME):$(VERSION)

bash:
	sudo docker exec -t -i $(NAME) /bin/bash

rm:
	sudo docker rm $(NAME)
