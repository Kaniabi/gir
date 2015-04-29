FROM quay.io/kaniabi/baseimage:v1.1
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

VOLUME ["/var/log/gir"]

EXPOSE 80
ENTRYPOINT ["supervisord", "-n"]
