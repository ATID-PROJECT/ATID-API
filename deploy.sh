pipenv --rm
make packages
echo "start flask-app"
fuser -k 5000/tcp
pipenv run gunicorn -b 0.0.0.0:5000 --access-logfile - "run:create_app()" --daemon