FROM python:3.8-alpine
MAINTAINER Harmon Herring <harmonherring@gmail.com>

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

RUN mkdir -p /opt/ctf-api/uploads
RUN chmod 777 /opt/ctf-api/uploads
WORKDIR /opt/ctf-api

RUN apk update && apk add --no-cache gcc make musl-dev libffi-dev postgresql-dev libmagic
RUN pip install --upgrade pip setuptools wheel
RUN pip install gunicorn[gevent] 

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD ["gunicorn", "--workers=4", "app:app", "--bind=0.0.0.0:8080", "-k gevent",  "--access-logfile=-"]
