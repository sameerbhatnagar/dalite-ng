FROM nginx:1.19-perl

# Overwrite default config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# https://www.rockyourcode.com/run-docker-nginx-as-non-root-user/
# Drop user directive (second line)
RUN sed -i '1,2d' /etc/nginx/nginx.conf

# Assign permissions
RUN groupadd -r container_user && useradd --no-log-init -r -g container_user container_user
RUN chown -R container_user:container_user /var/cache/nginx && \
    chown -R container_user:container_user /var/log/nginx && \
    chown -R container_user:container_user /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
    chown -R container_user:container_user /var/run/nginx.pid
USER container_user
