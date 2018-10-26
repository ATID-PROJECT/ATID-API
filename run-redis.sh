#!/bin/bash
#Thanks to https://blog.miguelgrinberg.com/post/using-celery-with-flask
if [ ! -d redis-stable/src ]; then
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
fi
cd redis-stable
make
src/redis-server --requirepass mypassword