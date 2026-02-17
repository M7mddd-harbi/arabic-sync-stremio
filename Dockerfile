# نستخدم صورة بايثون خفيفة
FROM python:3.9-slim

# تثبيت الأدوات الضرورية (curl عشان نحمل alass)
RUN apt-get update && apt-get install -y curl

# إعداد مجلد العمل
WORKDIR /app

# تحميل أداة alass وتثبيتها
# نقوم بتحميل النسخة الجاهزة للينكس ونعطيها صلاحية التنفيذ
RUN curl -L https://github.com/kaegi/alass/releases/download/v2.0.0/alass-linux64 -o /usr/local/bin/alass && \
    chmod +x /usr/local/bin/alass

# نسخ ملفات المشروع
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# تشغيل التطبيق
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:80"]
