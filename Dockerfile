FROM python:3.11-slim

WORKDIR /usr/app
RUN pip cache purge
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD pytest
