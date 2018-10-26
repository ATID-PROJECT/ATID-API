# Use an official Python runtime as an image
FROM python:3.6.5

ENV INSTALL_PATH /app

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

RUN pip install --upgrade pip
RUN pip install pipenv

COPY . .

RUN pipenv lock && pipenv install --system --deploy --ignore-pipfile
CMD pipenv run gunicorn -b 0.0.0.0:5000 --access-logfile - "app:create_app()"