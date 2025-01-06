FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -e .

CMD ["run-app"]