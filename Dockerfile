FROM python:3.8-alpine
MAINTAINER Harmon Herring <harmonherring@gmail.com>

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

RUN mkdir /opt/ctf-api
WORKDIR /opt/ctf-api

RUN apk update && apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
ADD . .

CMD ["gunicorn", "app:app", "--bind=0.0.0.0:8080", "--access-logfile=-"]
