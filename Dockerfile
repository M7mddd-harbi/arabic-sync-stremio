FROM node:18-slim

# تثبيت بايثون فقط بدون أدوات بناء ثقيلة
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --production

# تثبيت مكتبة معالجة الترجمة الخفيفة
RUN pip3 install pysubs2 --break-system-packages

COPY . .

EXPOSE 10000

CMD ["node", "server.js"]
