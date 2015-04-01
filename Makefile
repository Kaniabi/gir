NAME = gir
VERSION = latest

.PHONY: build run bash rm

all: build

build:
	sudo docker build --rm -t $(NAME):$(VERSION) .

run: rm
	sudo docker run -p 80:80 -e SLACK_TOKEN=xoxb-3724390083-OaNvuxp0CbYdo0fiy5kPBcWE -e PORT=80 -e GIR_USER=gir -e GIR_HOST=docker -e DEBUG=true --name gir $(NAME)

bash:
	sudo docker exec -t -i $(NAME) /bin/bash

rm:
	sudo docker rm gir
