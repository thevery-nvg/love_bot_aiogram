FROM python:alpine

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements/ requirements/

RUN pip install --upgrade pip \
        && pip install poetry \
        && poetry install

COPY . .

CMD ["python", "./run.py"]