FROM nikolaik/python-nodejs:python3.10-nodejs20

WORKDIR /usr/app
COPY package*.json ./
RUN npm ci \
    && npm cache clean --force

COPY requirements.in ./
RUN pip install -r requirements.in

COPY . .
CMD ape test
