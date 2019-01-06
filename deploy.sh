export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

pipenv --rm
make install
echo "start flask-app"
pipenv run gunicorn -b 0.0.0.0:5000 --access-logfile - "run:create_app()"