FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN mkdir log
RUN mkdir snapshots
RUN mkdir static
COPY requirements/requirements-dev.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./analytics analytics
COPY ./dalite dalite
COPY ./functional_tests functional_tests
COPY ./locale locale
COPY ./peerinst peerinst
COPY ./quality quality
COPY ./reputation reputation
COPY ./REST REST
COPY ./templates templates
COPY ./tos tos
COPY ./manage.py .

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
RUN groupadd -r container_user && useradd --no-log-init -r -g container_user container_user
RUN chown -R container_user:container_user /code
USER container_user
