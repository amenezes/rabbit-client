FROM python:3.6.9-slim

RUN apt-get update && \
    apt-get install -y netcat \
                       gcc \
                       postgresql \
                       libpq-dev \
                       postgresql-client \
                       postgresql-client-common && \
    rm -rf /var/cache/apt/*

WORKDIR myapp

COPY requirements-dev.txt .

RUN pip install -r requirements-dev.txt
RUN pip install aiohttp==3.5.4

COPY . .

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["test_client_single.py"]
