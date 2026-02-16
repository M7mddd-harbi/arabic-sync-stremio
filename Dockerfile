# استخدام نسخة Node.js مستقرة
FROM node:18-slim

# تثبيت الأدوات اللازمة (Python و FFmpeg)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات فقط وتثبيتها
COPY package.json ./
RUN npm install

# تثبيت أداة المزامنة (ffsubsync)
RUN pip3 install ffsubsync --break-system-packages

# نسخ بقية الملفات
COPY . .

# تحديد المنفذ (Render يستخدم 10000)
EXPOSE 10000

# تشغيل الإضافة
CMD ["node", "server.js"]
