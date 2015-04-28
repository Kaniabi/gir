# Using phusion baseimage as explained here:
#   https://github.com/phusion/baseimage-docker
FROM quay.io/kaniabi/baseimage:v1.2
MAINTAINER Alexandre Andrade <ama@esss.com.br>

# Update working directories
ADD . /gir

# . Install python requirements;
# . nginx: Place our nginx.conf;
# . supervisord: Use our supervisor.conf.
RUN \
    pip3 install -r /gir/requirements.txt && \
    ln -s /gir/config/nginx.conf /etc/nginx/sites-enabled/ && \
    ln -s /gir/config/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
#ENTRYPOINT ["supervisord", "-n"]
CMD ["supervisord", "-n"]
