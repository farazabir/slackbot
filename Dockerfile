FROM alpine:3.18

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache python3 py3-pip

WORKDIR /app


COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

CMD python manage.py runserver 0.0.0.0:8000