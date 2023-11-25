FROM python:3.12.0-slim-bullseye
ARG directory

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY ${directory} /

WORKDIR /${directory}

CMD ${directory}/Main.py

