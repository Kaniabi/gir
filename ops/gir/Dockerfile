FROM quay.io/kaniabi/baseimage:v1.2
MAINTAINER Alexandre Andrade <ama@esss.com.br>

ADD . /gir

RUN \
    pip3 install \
        flask-rq \
        rq-dashboard \
        couchdb \
        git+https://github.com/slackhq/python-slackclient.git@39de60050e \
        jsonpath-rw && \
    ln -s /gir/nginx.conf /etc/nginx/sites-enabled/ && \
    ln -s /gir/supervisor.conf /etc/supervisor/conf.d/

RUN git clone -b ama https://github.com/Kaniabi/gir.git /gir/app

EXPOSE 80
ENTRYPOINT ["supervisord", "-n"]
