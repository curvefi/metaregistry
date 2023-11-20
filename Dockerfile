FROM python:3.11-slim

WORKDIR /usr/app
RUN pip cache purge
COPY requirements.in ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.in

COPY . .
CMD pytest
