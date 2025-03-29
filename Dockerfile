FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install poetry

COPY . /app

WORKDIR /app

ENV PYTHONPATH=/app

RUN poetry config virtualenvs.create false && poetry install

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]

