import os
import requests
import subprocess
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# --- إعدادات هامة ---
# ضع مفتاح OpenSubtitles هنا
OPENSUBTITLES_API_KEY = "3AkRuLHqFhPeLUHu6gkjmwQPyIAKN3ZM"  # <--- تأكد أنك وضعت المفتاح هنا
TEMP_DIR = "/tmp"
ALASS_PATH = "/usr/local/bin/alass"

# التأكد من وجود المجلد المؤقت
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def get_download_link(file_id):
    """جلب رابط التحميل المباشر من OpenSubtitles"""
    url = "https://api.opensubtitles.com/api/v1/download"
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "StremioAutoSync v1.0"
    }
    payload = {"file_id": file_id}
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            return r.json().get('link')
        else:
            print(f"Failed to get link for {file_id}: {r.text}")
    except Exception as e:
        print(f"Error getting download link: {e}")
    return None

def download_file(url, save_path):
    """تحميل الملف وحفظه"""
    try:
        r = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def search_subtitles(imdb_id):
    """البحث عن ترجمة عربية وإنجليزية"""
    url = "https://api.opensubtitles.com/api/v1/subtitles"
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "StremioAutoSync v1.0"
    }
    # نبحث عن العربية والإنجليزية لنفس الـ IMDB ID
    params = {
        "imdb_id": imdb_id,
        "languages": "ar,en",
        "order_by": "download_count",
        "sort": "desc"
    }
    
    en_sub = None
    ar_sub = None
    
    try:
        r = requests.get(url, headers=headers, params=params)
        data = r.json().get('data', [])
        
        # تصنيف النتائج
        for item in data:
            attrs = item.get('attributes', {})
            lang = attrs.get('language')
            file_id = attrs.get('files')[0].get('file_id')
            
            if lang == 'en' and en_sub is None:
                en_sub = file_id # نأخذ أول (أشهر) ملف إنجليزي كمرجع
            elif lang == 'ar' and ar_sub is None:
                ar_sub = file_id # نأخذ أول ملف عربي
            
            if en_sub and ar_sub:
                break
                
    except Exception as e:
        print(f"Search error: {e}")
        
    return en_sub, ar_sub

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "id": "org.mohammed.autosync",
        "version": "1.0.2",
        "name": "Auto-Sync Arabic",
        "description": "Automatically syncs Arabic subtitles using English reference.",
        "resources": ["subtitles"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"],
        "catalogs": []
    })

@app.route('/subtitles/<type>/<id>/<extra>.json')
def get_subtitles(type, id, extra):
    # ID يأتي عادة بصيغة tt1234567:1:1 نحتاج فقط الجزء الأول
    imdb_id = id.split(":")[0].replace("tt", "")
    
    print(f"Processing request for IMDB: {imdb_id}")

    # 1. البحث في OpenSubtitles
    en_id, ar_id = search_subtitles(imdb_id)
    
    if not en_id or not ar_id:
        print("Could not find both Arabic and English subtitles.")
        return jsonify({"subtitles": []})

    # 2. جلب روابط التحميل
    en_link = get_download_link(en_id)
    ar_link = get_download_link(ar_id)
    
    if not en_link or not ar_link:
        return jsonify({"subtitles": []})

    # 3. تحميل الملفات
    en_path = os.path.join(TEMP_DIR, f"{imdb_id}_en.srt")
    ar_path = os.path.join(TEMP_DIR, f"{imdb_id}_ar.srt")
    fixed_path = os.path.join(TEMP_DIR, f"{imdb_id}_fixed.srt")
    
    download_file(en_link, en_path)
    download_file(ar_link, ar_path)

    # 4. تشغيل alass للمزامنة
    # الأمر: alass reference.srt input.srt output.srt
    print("Running alass sync...")
    cmd = [ALASS_PATH, en_path, ar_path, fixed_path]
    try:
        subprocess.run(cmd, check=True)
        print("Sync successful!")
        
        # إنشاء رابط للتحميل
        host = request.host_url.rstrip('/')
        subtitle_url = f"{host}/download/{imdb_id}_fixed.srt"
        
        return jsonify({
            "subtitles": [{
                "id": "autosync_ar",
                "url": subtitle_url,
                "lang": "ara",
                "label": "Arabic (Auto-Synced) ✅"
            }]
        })
        
    except subprocess.CalledProcessError:
        print("Alass failed to sync.")
        return jsonify({"subtitles": []})

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
