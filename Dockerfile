# Using phusion baseimage as explained here:
#   https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.9.16
MAINTAINER Alexandre Andrade <ama@esss.com.br>

# Install dependencies
RUN apt-get update
RUN apt-get install -y nginx redis-server supervisor python3-pip git

# Update working directories
ADD ./config /config

# Configure python-rq
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install application requirements (python3)
RUN pip3 install -r /config/requirements.txt

# Configure redis-server
# . No daemon since we're using supervisord
RUN sed -i 's/^\(daemonize\s*\)yes\s*$/\1no/g' /etc/redis/redis.conf

# Configure nginx
# . No daemon since we're using supervisord
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf
# . Replace default site by nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /config/nginx.conf /etc/nginx/sites-enabled/

# Configure supervisor
RUN ln -s /config/supervisor.conf /etc/supervisor/conf.d/

# Add app last to easy changes in the code
ADD ./app /app

EXPOSE 80
CMD ["supervisord", "-n"]

