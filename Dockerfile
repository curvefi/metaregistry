FROM python:3.11-slim as base

WORKDIR /usr/app
RUN pip cache purge
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM base as pre-commit
RUN apt-get update && apt-get install -y git
COPY . .
CMD git add . && pre-commit run --all-files

FROM base as test
COPY . .
CMD pytest
