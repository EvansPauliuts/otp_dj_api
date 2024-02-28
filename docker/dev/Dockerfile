FROM python:3.12.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev netcat-traditional \
    && pip install Pillow

COPY ./requirements/ ./requirements
RUN pip install --upgrade pip
RUN pip install -r ./requirements/dev.txt

COPY ./docker/dev/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./src /app

ENTRYPOINT ["/entrypoint.sh"]
