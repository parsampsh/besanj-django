FROM nginxinc/nginx-unprivileged:1-alpine

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params

USER nginx
