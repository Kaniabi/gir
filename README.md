# gir
Customized slack (www.slack.com) messages from "any" (jenkins, stash, jira) web-hooks.

## Learning...

I'm trying to implement the workflow described at the following page:
>https://blog.rainforestqa.com/2014-11-19-docker-in-action-from-deployment-to-delivery-part-1-local-docker-setup/

The idea is to build a flask application inside an docker container and implement the continuous delivery processs based on that.

This project initial layout was inspired in the Real Python Tutorial:
>https://github.com/realpython/flask-docker-workflow

## Usage

```
$ git clone https://github.com/Kaniabi/gir.git
$ cd gir
$ vagrant up
```

## Technologies

This project is a experiment on many "new" (for me) technologies, including but not limited:

* vagrant
* docker
* nginx
* uwsgi
* supervisord
* flask

