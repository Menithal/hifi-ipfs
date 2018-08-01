# Using Nginx + Python combo
# https://github.com/tiangolo/uwsgi-nginx-flask-docker
FROM tiangolo/uwsgi-nginx:python3.6

# originally amde by tiangolo, but this version is maintained by
LABEL maintainer="Matti Lahtinen <menithal@norteclabs.com>"

COPY ./app /app
WORKDIR /app
ENV PYTHONPATH=/app

# This next part is based on the flask-docker docker file, but modded to just refer to local nginx configs.
RUN pip install flask ipfsapi==0.4.3 flask_sqlalchemy==2.3.2 flask-marshmallow==0.9.0 Flask-Migrate==2.2.1 psycopg2-binary==2.7.5 python-dotenv==0.8.2

ENTRYPOINT ["/entrypoint.sh"]
# By default, allow unlimited file sizes, modify it to limit the file sizes
# To have a maximum of 1 MB (Nginx's default) change the line to:
# ENV NGINX_MAX_UPLOAD 1m
ENV NGINX_MAX_UPLOAD 0

# Which uWSGI .ini file should be used, to make it customizable
ENV UWSGI_INI /app/uwsgi.ini

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
# ENV STATIC_INDEX 1
ENV STATIC_INDEX 0

COPY nginx/conf.d/ /etc/nginx/conf.d/

COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy configuration scripts
COPY docker_scripts/start.sh /start.sh
RUN chmod +x /start.sh

COPY docker_scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/start.sh"]
