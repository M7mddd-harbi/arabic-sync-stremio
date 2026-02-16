FROM python:3.11-slim

# تثبيت أدوات النظام
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    gcc \
    nodejs \
    npm

# تحديث pip
RUN pip install --upgrade pip setuptools wheel

# تثبيت ffsubsync
RUN pip install ffsubsync

WORKDIR /app

# تثبيت Node dependencies
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 10000

CMD ["node", "index.js"]
