FROM quay.io/kaniabi/baseimage:v1.1
MAINTAINER Alexandre Andrade <ama@esss.com.br>

VOLUME ["/home/gir"]

# . Install python requirements;
# . nginx: Place our nginx.conf;
# . supervisord: Use our supervisor.conf.
RUN \
    pip3 install -r /home/gir/requirements.txt && \
    ln -s /home/gir/config/nginx.conf /etc/nginx/sites-enabled/ && \
    ln -s /home/gir/config/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
ENTRYPOINT ["supervisord", "-n"]
