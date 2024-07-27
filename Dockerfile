FROM python:3.11-alpine

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN mkdir /app
COPY ./project/requirements.txt /app

# Install required package
RUN apk update && \
    apk add --no-cache mariadb-dev build-base pkgconfig \
    # apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    git bash

# Install requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the script wait-for-it.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY ./project/ /app
WORKDIR /app

CMD [ "/wait-for-it.sh", "db:3306", "--", "python", "manage.py", "runserver", "0.0.0.0:9001" ]
# CMD ["cd", "/app"]