import os
import requests
import subprocess
import shutil
import zipfile
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from fuzzywuzzy import fuzz

app = Flask(__name__)

# --- تفعيل التصاريح الشاملة (CORS) ---
CORS(app, resources={r"/*": {"origins": "*"}})

# --- منطقة المفاتيح (عبئها جميعاً) ---
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
        headers = {"User-Agent": "MddsAddon/V10"}
        r = requests.get(url, headers=headers, stream=True, timeout=15)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except: pass
    return False

def extract_srt(archive_path, output_dir):
    """استخراج SRT من Zip بذكاء"""
    try:
        if not zipfile.is_zipfile(archive_path):
            return archive_path # قد يكون ملف srt مباشرة
            
        with zipfile.ZipFile(archive_path, 'r') as z:
            # نبحث عن أكبر ملف srt داخل الأرشيف (غالباً هو الفيلم)
            srt_files = [f for f in z.namelist() if f.lower().endswith('.srt')]
            if not srt_files: return None
            
            best_srt = max(srt_files, key=lambda x: z.getinfo(x).file_size)
            
            source = z.open(best_srt)
            target_name = os.path.basename(archive_path).replace('.zip', '.srt')
            target_path = os.path.join(output_dir, target_name)
            
            with open(target_path, "wb") as f:
                shutil.copyfileobj(source, f)
            return target_path
    except: pass
    return None

# --- المصدر 1: OpenSubtitles (الذكاء + الهاش) ---

def search_opensubtitles(imdb_id, moviehash=None):
    url = "https://api.opensubtitles.com/api/v1/subtitles"
    headers = {"Api-Key": OPENSUBTITLES_API_KEY, "User-Agent": "MddsAddon/V10"}
    
    # 1. محاولة الهاش (الذهبية)
    if moviehash:
        try:
            params = {"moviehash": moviehash, "languages": "en,ar"}
            r = requests.get(url, headers=headers, params=params)
            data = r.json().get('data', [])
            en = next((x for x in data if x['attributes']['language'] == 'en'), None)
            ar = next((x for x in data if x['attributes']['language'] == 'ar'), None)
            if en and ar: return en, ar # وجدنا التوأم المتطابق
        except: pass

    # 2. محاولة الاسم (الفضية)
    try:
        params = {"imdb_id": imdb_id, "languages": "en,ar", "order_by": "download_count"}
        r = requests.get(url, headers=headers, params=params)
        data = r.json().get('data', [])
        
        en_list = [x for x in data if x['attributes']['language'] == 'en']
        ar_list = [x for x in data if x['attributes']['language'] == 'ar']
        
        if not en_list or not ar_list: return None, None

        # مطابقة الأسماء
        best_ar = ar_list[0]
        ar_name = best_ar['attributes']['files'][0]['file_name'].lower()
        best_en = en_list[0]
        high_score = 0
        keywords = ['bluray', 'web-dl', 'hdtv', 'yts', 'rarbg']

        for en in en_list[:10]:
            en_name = en['attributes']['files'][0]['file_name'].lower()
            score = fuzz.ratio(ar_name, en_name)
            for k in keywords:
                if k in ar_name and k in en_name: score += 20
            if score > high_score:
                high_score = score
                best_en = en
        
        return best_en, best_ar
    except: return None, None

def get_os_link(file_id):
    url = "https://api.opensubtitles.com/api/v1/download"
    headers = {"Api-Key": OPENSUBTITLES_API_KEY, "User-Agent": "MddsAddon/V10"}
    try:
        r = requests.post(url, headers=headers, json={"file_id": file_id})
        return r.json().get('link')
    except: return None

# --- المصدر 2: SubDL ---

def search_subdl(imdb_id):
    url = "https://api.subdl.com/api/v1/subtitles"
    params = {"api_key": SUBDL_API_KEY, "imdb_id": f"tt{imdb_id}", "type": "movie", "languages": "ar,en"}
    
    link_en, link_ar = None, None
    try:
        r = requests.get(url, params=params)
        for sub in r.json().get('subtitles', []):
            lang = sub.get('language')
            dl = sub.get('url')
            full_dl = f"https://dl.subdl.com{dl}" if dl and not dl.startswith('http') else dl
            
            if lang == 'EN' and not link_en: link_en = full_dl
            if lang == 'AR' and not link_ar: link_ar = full_dl
            if link_en and link_ar: break
    except: pass
    return link_en, link_ar

# --- المصدر 3: SubSource ---

def search_subsource(imdb_id):
    url = "https://api.subsource.net/api/getSub"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {SUBSOURCE_API_KEY}"}
    payload = {"imdb": f"tt{imdb_id}"}
    
    link_en, link_ar = None, None
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            for sub in r.json().get('subs', []):
                lang = sub.get('lang', '').lower()
                token = sub.get('downloadToken')
                dl_link = f"https://api.subsource.net/api/downloadSub/{token}"
                
                if 'english' in lang and not link_en: link_en = dl_link
                if ('arabic' in lang or 'farsi' in lang) and not link_ar: link_ar = dl_link
    except: pass
    return link_en, link_ar

# --- المحرك الرئيسي ---

@app.route('/manifest.json')
@cross_origin()
def manifest():
    return jsonify({
        "id": "org.mdds.ultimate",
        "version": "10.0.0",
        "name": "Mdds", # الاسم الخاص في القائمة
        "description": "Ultimate Sync (OS+SubDL+SubSource)",
        "logo": "https://raw.githubusercontent.com/M7mddd-harbi/arabic-sync-stremio/main/mdds.jpg",
        "resources": ["subtitles"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"],
        "catalogs": []
    })

@app.route('/subtitles/<type>/<id>/<extra>.json')
@cross_origin()
def get_subtitles(type, id, extra):
    imdb_id = id.split(":")[0].replace("tt", "")
    moviehash = None
    if extra:
        try: 
            from urllib.parse import parse_qs
            moviehash = parse_qs(extra).get('videoHash', [None])[0]
        except: pass

    print(f"Mdds V10 Request: {imdb_id}")

    en_url, ar_url = None, None

    # 1. المصدر الأول: OpenSubtitles
    en_obj, ar_obj = search_opensubtitles(imdb_id, moviehash)
    if en_obj and ar_obj:
        en_url = get_os_link(en_obj['attributes']['files'][0]['file_id'])
        ar_url = get_os_link(ar_obj['attributes']['files'][0]['file_id'])

    # 2. المصدر الثاني: SubDL (إذا فشل الأول)
    if not en_url or not ar_url:
        en_url, ar_url = search_subdl(imdb_id)

    # 3. المصدر الثالث: SubSource (الطوارئ)
    if not en_url or not ar_url:
        en_url, ar_url = search_subsource(imdb_id)

    # إذا فشل الجميع
    if not en_url or not ar_url:
        return jsonify({"subtitles": []})

    # التحميل والمعالجة
    # نستخدم صيغة zip احتياطاً لأن SubDL و SubSource يرسلون zip
    temp_en_zip = os.path.join(TEMP_DIR, f"ref_{imdb_id}.zip")
    temp_ar_zip = os.path.join(TEMP_DIR, f"target_{imdb_id}.zip")
    
    if not download_file(en_url, temp_en_zip) or not download_file(ar_url, temp_ar_zip):
        return jsonify({"subtitles": []})

    # فك الضغط (أو استخدام الملف مباشرة إذا لم يكن zip)
    ref_path = extract_srt(temp_en_zip, TEMP_DIR)
    target_path = extract_srt(temp_ar_zip, TEMP_DIR)

    if not ref_path or not target_path:
        return jsonify({"subtitles": []})

    # المزامنة
    fixed_path = os.path.join(TEMP_DIR, f"fixed_{imdb_id}.srt")
    cmd = [ALASS_PATH, ref_path, target_path, fixed_path]
    
    try:
        subprocess.run(cmd, check=True, timeout=30)
        host = request.host_url.rstrip('/')
        
        return jsonify({
            "subtitles": [{
                "id": "mdds_ultimate",
                "url": f"{host}/download/{os.path.basename(fixed_path)}",
                "lang": "mdds", # <--- قسم خاص Mdds
                "label": "Mdds"
            }]
        })
    except: return jsonify({"subtitles": []})

@app.route('/download/<filename>')
@cross_origin()
def download(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
