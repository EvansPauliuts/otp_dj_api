FROM python:3.12.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev netcat libzmq3-dev git

COPY ./app/requirements ./requirements

COPY ./app/requirements ./requirements
RUN pip install --upgrade pip
RUN pip install -r ./requirements/prod.txt

COPY ./docker/prod/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./app /app

ENTRYPOINT ["/entrypoint.sh"]