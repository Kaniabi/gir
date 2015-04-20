NAME = gir
VERSION = latest

.PHONY: build run bash rm

all: build

build:
	sudo docker build --rm -t $(NAME):$(VERSION) .

run:
	sudo docker run -p 80:80 -e SLACK_ROOM=#bos-ama -e SLACK_TOKEN=xoxb-3724390083-OaNvuxp0CbYdo0fiy5kPBcWE -e PORT=80 -e GIR_USER=gir -e GIR_HOST=docker GIR_STATIC_URL=http://188.226.245.90/static/ -e DEBUG=true --rm=true --name gir $(NAME)

bash:
	sudo docker exec -t -i $(NAME) /bin/bash

rm:
	sudo docker rm gir
