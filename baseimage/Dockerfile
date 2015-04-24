# Using phusion baseimage as explained here:
#   https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.9.16
MAINTAINER Alexandre Andrade <ama@esss.com.br>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# . nginx: No daemon since we're using supervisord;
# . nginx: Delete default sites.
RUN \
    apt-get update && \
    apt-get install -y nginx supervisor python3-pip git && \
    apt-get clean && \
    echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
    rm /etc/nginx/sites-enabled/default
