import os
import requests
import subprocess
import zipfile
import shutil
import json
from flask import Flask, jsonify, request, send_from_directory
from urllib.parse import parse_qs

app = Flask(__name__)

# --- منطقة المفاتيح (عبئها هنا) ---
OPENSUBTITLES_API_KEY = "3AkRuLHqFhPeLUHu6gkjmwQPyIAKN3ZM"
SUBDL_API_KEY = "9a5ehIGoPIfo8EDNEVpRpnf8hLBGh4hl"
SUBSOURCE_API_KEY = "sk_7f34f11898460d628fc297e4912ebc6cadd635ae3c651a26fe8658e406def17f"

# إعدادات النظام
TEMP_DIR = "/tmp"
ALASS_PATH = "/usr/local/bin/alass"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- دوال مساعدة (تحميل وفك ضغط) ---

def download_file(url, save_path):
    """تحميل الملفات (srt أو zip)"""
    try:
        headers = {"User-Agent": "StremioAutoSync/4.0"}
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Download Error: {e}")
    return False

def extract_srt(archive_path, output_dir):
    """استخراج SRT من Zip"""
    try:
        if not zipfile.is_zipfile(archive_path):
            return archive_path # قد يكون ملف srt مباشرة
            
        with zipfile.ZipFile(archive_path, 'r') as z:
            for filename in z.namelist():
                if filename.lower().endswith('.srt'):
                    # استخراج وتغيير الاسم
                    source = z.open(filename)
                    target_name = os.path.basename(archive_path).replace('.zip', '.srt')
                    target_path = os.path.join(output_dir, target_name)
                    with open(target_path, "wb") as f:
                        shutil.copyfileobj(source, f)
                    return target_path
    except Exception as e:
        print(f"Extraction Error: {e}")
    return None

# --- المصدر 1: OpenSubtitles ---

def search_opensubtitles(imdb_id, moviehash=None):
    print("Checking OpenSubtitles...")
    url = "https://api.opensubtitles.com/api/v1/subtitles"
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "StremioAutoSync v4.0"
    }
    
    en_id, ar_id = None, None
    
    # محاولة بالهاش أولاً (الأدق)
    if moviehash:
        try:
            r = requests.get(url, headers=headers, params={"moviehash": moviehash, "languages": "en,ar"})
            for item in r.json().get('data', []):
                lang = item['attributes']['language']
                fid = item['attributes']['files'][0]['file_id']
                if lang == 'en' and not en_id: en_id = fid
                if lang == 'ar' and not ar_id: ar_id = fid
        except: pass

    # محاولة بالـ IMDB
    if not en_id or not ar_id:
        try:
            r = requests.get(url, headers=headers, params={"imdb_id": imdb_id, "languages": "en,ar", "order_by": "download_count"})
            for item in r.json().get('data', []):
                lang = item['attributes']['language']
                fid = item['attributes']['files'][0]['file_id']
                if lang == 'en' and not en_id: en_id = fid
                if lang == 'ar' and not ar_id: ar_id = fid
        except: pass

    # جلب الروابط
    link_en, link_ar = None, None
    if en_id:
        try:
            r = requests.post("https://api.opensubtitles.com/api/v1/download", headers=headers, json={"file_id": en_id})
            link_en = r.json().get('link')
        except: pass
    if ar_id:
        try:
            r = requests.post("https://api.opensubtitles.com/api/v1/download", headers=headers, json={"file_id": ar_id})
            link_ar = r.json().get('link')
        except: pass
        
    return link_en, link_ar

# --- المصدر 2: SubDL ---

def search_subdl(imdb_id):
    print("Checking SubDL...")
    url = "https://api.subdl.com/api/v1/subtitles"
    params = {"api_key": SUBDL_API_KEY, "imdb_id": f"tt{imdb_id}", "type": "movie", "languages": "ar,en"}
    
    link_en, link_ar = None, None
    try:
        r = requests.get(url, params=params)
        for sub in r.json().get('subtitles', []):
            lang = sub.get('language')
            url = sub.get('url')
            full_url = f"https://dl.subdl.com{url}" if url and not url.startswith('http') else url
            if lang == 'EN' and not link_en: link_en = full_url
            if lang == 'AR' and not link_ar: link_ar = full_url
    except: pass
    return link_en, link_ar

# --- المصدر 3: SubSource (الجديد) ---

def search_subsource(imdb_id):
    """
    ملاحظة: SubSource API يتطلب توثيق دقيق للمعاملات.
    بناءً على التوثيق المتوفر، نستخدم نقطة النهاية getSub.
    """
    print("Checking SubSource...")
    search_url = "https://api.subsource.net/api/getSub" #
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUBSOURCE_API_KEY}" # أو X-API-Key حسب التوثيق
    }
    
    # Payload قد يختلف قليلاً حسب التوثيق الرسمي، جرب imdb أو query
    payload = {"imdb": f"tt{imdb_id}"} 
    
    link_en, link_ar = None, None
    try:
        r = requests.post(search_url, json=payload, headers=headers)
        if r.status_code == 200:
            data = r.json()
            # هنا نفترض هيكلة الاستجابة (تحتاج مراجعة json الناتج)
            # عادة تكون قائمة subs تحتوي على lang و downloadToken
            for sub in data.get('subs', []):
                lang = sub.get('lang', '').lower()
                token = sub.get('downloadToken')
                if token:
                    dl_link = f"https://api.subsource.net/api/downloadSub/{token}"
                    if 'english' in lang and not link_en: link_en = dl_link
                    if ('arabic' in lang or 'farsi_persian' in lang) and not link_ar: link_ar = dl_link #
    except Exception as e:
        print(f"SubSource Error: {e}")
        
    return link_en, link_ar

# --- المحرك الرئيسي ---

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "id": "org.mohammed.ultimate",
        "version": "4.0.0",
        "name": "Ultimate Auto-Sync (OS+SubDL+SubSource)",
        "description": "Syncs subtitles from 3 major sources.",
        "resources": ["subtitles"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"],
        "catalogs": []
    })

@app.route('/subtitles/<type>/<id>/<extra>.json')
def get_subtitles(type, id, extra):
    imdb_id = id.split(":")[0].replace("tt", "")
    moviehash = None
    if extra:
        try:
            moviehash = parse_qs(extra)['videoHash'][0]
        except: pass

    print(f"Request: {imdb_id} Hash: {moviehash}")
    
    # المتغيرات النهائية للملفات
    ref_path = None
    target_path = None

    # 1. البحث في المصادر بالترتيب
    
    # محاولة OpenSubtitles
    en_url, ar_url = search_opensubtitles(imdb_id, moviehash)
    
    # إذا فشل، محاولة SubDL
    if not en_url or not ar_url:
        en_subdl, ar_subdl = search_subdl(imdb_id)
        if not en_url: en_url = en_subdl
        if not ar_url: ar_url = ar_subdl
        
    # إذا فشل، محاولة SubSource
    if not en_url or not ar_url:
        en_ss, ar_ss = search_subsource(imdb_id)
        if not en_url: en_url = en_ss
        if not ar_url: ar_url = ar_ss

    # 2. التحميل والمعالجة
    if en_url and ar_url:
        # تحميل المرجع (الإنجليزي)
        temp_en = os.path.join(TEMP_DIR, f"ref_{imdb_id}.zip") # نفترض أنه zip احتياطاً
        download_file(en_url, temp_en)
        ref_path = extract_srt(temp_en, TEMP_DIR)
        
        # تحميل الهدف (العربي)
        temp_ar = os.path.join(TEMP_DIR, f"target_{imdb_id}.zip")
        download_file(ar_url, temp_ar)
        target_path = extract_srt(temp_ar, TEMP_DIR)

    # 3. المزامنة
    if ref_path and target_path:
        fixed_path = os.path.join(TEMP_DIR, f"fixed_{imdb_id}.srt")
        cmd = [ALASS_PATH, ref_path, target_path, fixed_path]
        try:
            subprocess.run(cmd, check=True)
            host = request.host_url.rstrip('/')
            return jsonify({
                "subtitles": [{
                    "id": "autosync_ultimate",
                    "url": f"{host}/download/{os.path.basename(fixed_path)}",
                    "lang": "ara",
                    "label": "Arabic (Ultimate Sync) 🌟"
                }]
            })
        except: pass

    return jsonify({"subtitles": []})

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
