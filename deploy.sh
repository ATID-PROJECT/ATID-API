git pull origin master
pipenv --rm
pipenv lock && pipenv install
echo "start flask-app"
sudo systemctl restart api