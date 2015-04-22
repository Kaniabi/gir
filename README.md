[![Travis](https://img.shields.io/travis/Kaniabi/gir.svg)](https://circleci.com/gh/Kaniabi/gir)
[![Coveralls](https://img.shields.io/coveralls/Kaniabi/gir.svg)](https://coveralls.io/r/Kaniabi/gir)
[![Gemnasium](https://img.shields.io/gemnasium/Kaniabi/gir.svg)](https://gemnasium.com/Kaniabi/gir)
[![Docker Repository on Quay.io](https://quay.io/repository/kaniabi/gir/status "Docker Repository on Quay.io")](https://quay.io/repository/kaniabi/gir)

# gir
Customized slack (www.slack.com) messages from "any" (jenkins, stash, jira) web-hooks.

## Learning...

I'm trying to implement the workflow described at the following page:
* [Docker in Action - Development to Delivery, Part 1](https://blog.rainforestqa.com/2014-11-19-docker-in-action-from-deployment-to-delivery-part-1-local-docker-setup/)
* [Docker in Action - Development to Delivery, Part 2](https://blog.rainforestqa.com/2014-12-08-docker-in-action-from-deployment-to-delivery-part-2-continuous-integration/)
* [Docker in Action - Development to Delivery, Part 3](https://blog.rainforestqa.com/2015-01-15-docker-in-action-from-deployment-to-delivery-part-3-continuous-delivery/)

The idea is to build a flask application inside an docker container and implement the continuous delivery processs based on that.

This project initial layout was inspired in the Real Python Tutorial:
* [realpython/flask-docker-workflow](https://github.com/realpython/flask-docker-workflow)


## Technologies

This project is a experiment on many "new" (for me) technologies, including but not limited:

* vagrant
* docker
* nginx
* uwsgi
* supervisord
* flask

## Services

Some related services.

* github.com - Host the source code.
* quay.co - Builds the docker image.
* www.tutum.co - Deploys the docker image.
* www.digitalocean.com - Hosts the site.

* hub.docker.com (deprecated)
* circleci.com (deprecated)


