FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

CMD [ "/bin/sh", "-c", "python3 app.py migrate && gunicorn -w 4 -b $API_HOST:$API_PORT app:app"]
