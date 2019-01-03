FROM python:alpine3.8

RUN apk add --no-cache  \
    musl-dev \
    gcc \
    git \
    python3-dev

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

CMD sleep 9999999
