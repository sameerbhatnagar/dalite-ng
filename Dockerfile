# Resources
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
# https://mherman.org/presentations/dockercon-2018

FROM node:12.18.2 AS static
RUN mkdir /code
WORKDIR /code
COPY package*.json ./
RUN npm i
COPY . /code/
RUN node_modules/gulp/bin/gulp.js build

FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN mkdir log
RUN mkdir static
COPY requirements/requirements-prod-aws.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY --from=static /code/analytics ./analytics
COPY --from=static /code/dalite ./dalite
COPY --from=static /code/locale ./locale
COPY --from=static /code/peerinst ./peerinst
COPY --from=static /code/quality ./quality
COPY --from=static /code/reputation ./reputation
COPY --from=static /code/REST ./REST
COPY --from=static /code/templates ./templates
COPY --from=static /code/tos ./tos
COPY --from=static /code/manage.py .
RUN python3 manage.py collectstatic --clear --noinput
RUN python3 manage.py compress

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
RUN groupadd -r container_user && useradd --no-log-init -r -g container_user container_user
RUN chown -R container_user:container_user /code
USER container_user
