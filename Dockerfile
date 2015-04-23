# Using phusion baseimage as explained here:
#   https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.9.16
MAINTAINER Alexandre Andrade <ama@esss.com.br>

# Environment variables (this is needed by python-rq)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Update working directories
ADD . /gir

# . DEPRECATED: Update the docker container (apt-get update) - http://crosbymichael.com/dockerfile-best-practices-take-2.html
# . Install dependencies (apt-get install)
# . redis: No daemon since we're using supervisord
# . nginx: No daemon since we're using supervisord
# . nginx: Replace default site by nginx.conf
# . supervisord: Use our supervisor.conf
RUN \
    apt-get install -y nginx redis-server supervisor python3-pip git && \
    pip3 install -r /gir/config/requirements.txt && \
    sed -i 's/^\(daemonize\s*\)yes\s*$/\1no/g' /etc/redis/redis.conf && \
    echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
    rm /etc/nginx/sites-enabled/default && \
    ln -s /gir/config/nginx.conf /etc/nginx/sites-enabled/ && \
    ln -s /gir/config/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
ENTRYPOINT ["supervisord", "-n"]

