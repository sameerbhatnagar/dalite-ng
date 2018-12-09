from alpine

run mkdir /app
workdir /app

run apk update && \
    apk add --no-cache python2 \
                       py-setuptools \
                       nodejs \
                       yarn

run ln -sf /usr/bin/python2.7 /usr/bin/python && \
    ln -sf /usr/bin/easy_install-2.7 /usr/bin/easy_install

run easy_install pip && \
    pip install --upgrade pip && \
    pip install virtualenv

run virtualenv .venv && \
    source .venv/bin/activate

run mkdir /app/requirements

run ls /app

run pip install -r requirements/dev-requirements.txt

add . /app/
