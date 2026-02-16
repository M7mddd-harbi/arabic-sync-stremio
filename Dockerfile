FROM node:18

RUN apt-get update && apt-get install -y ffmpeg python3 python3-venv curl

# إنشاء بيئة بايثون منفصلة
RUN python3 -m venv /opt/venv

# تفعيل البيئة
ENV PATH="/opt/venv/bin:$PATH"

# تثبيت ffsubsync داخل البيئة
RUN pip install --upgrade pip
RUN pip install ffsubsync

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 10000

CMD ["node", "index.js"]
