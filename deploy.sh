docker stop flask-atid
docker rm flask-atid
docker build -t flask-atid .
docker run -d --name app flask-atid