import os
import requests
import subprocess
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# إعدادات المجلدات
TEMP_DIR = "/tmp"
TOOLS_DIR = "./tools"
ALASS_PATH = "alass-linux64"  # اسم الأداة داخل بيئة اللينكس

# مفتاح API الخاص بـ OpenSubtitles (سجل واحصل عليه مجاناً من موقعهم)
OPENSUBTITLES_API_KEY = "3AkRuLHqFhPeLUHu6gkjmwQPyIAKN3ZM"

def download_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def get_english_reference(imdb_id):
    """جلب أفضل ترجمة إنجليزية لتكون هي المرجع"""
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "YourAppName v1.0"
    }
    url = f"https://api.opensubtitles.com/api/v1/subtitles?imdb_id={imdb_id}&languages=en&order_by=download_count&sort=desc"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if data['data']:
            # نحتاج رابط التحميل
            file_id = data['data'][0]['attributes']['files'][0]['file_id']
            # طلب رابط التحميل الحقيقي (يتطلب خطوة إضافية في API opensubtitles)
            # للتبسيط هنا سنفترض أننا حصلنا على الرابط
            # ملاحظة: في الكود الفعلي تحتاج implement download endpoint
            return "LINK_TO_ENGLISH_SUB" 
    except Exception as e:
        print(f"Error fetching English ref: {e}")
    return None

def sync_subtitles(ref_path, target_path, output_path):
    """تشغيل أداة alass للمزامنة"""
    command = [
        f"alass", 
        ref_path, 
        target_path, 
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except Exception as e:
        print(f"Sync failed: {e}")
        return False

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "id": "org.mohammed.autosync",
        "version": "1.0.0",
        "name": "Auto-Sync Arabic",
        "description": "Fixes Arabic subtitles timing using English reference",
        "resources": ["subtitles"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt", "kitsu"],
        "catalogs": []
    })

@app.route('/subtitles/<type>/<id>/<extra>.json')
def get_subtitles(type, id, extra):
    # نستخرج الـ IMDB ID
    imdb_id = id.split(":")[0]
    
    # 1. تحميل المرجع الإنجليزي (وهمي حالياً للشرح)
    ref_sub_path = os.path.join(TEMP_DIR, f"{imdb_id}_ref.srt")
    # download_file(ENGLISH_URL, ref_sub_path) <-- فعل هذا لاحقاً

    # 2. تحميل الهدف العربي (من OpenSubtitles, SubDL, etc)
    ar_sub_path = os.path.join(TEMP_DIR, f"{imdb_id}_ar.srt")
    # download_file(ARABIC_URL, ar_sub_path) <-- فعل هذا لاحقاً

    # 3. المزامنة
    final_sub_path = os.path.join(TEMP_DIR, f"{imdb_id}_fixed.srt")
    
    # هنا نفترض أننا قمنا بالمزامنة
    # success = sync_subtitles(ref_sub_path, ar_sub_path, final_sub_path)
    
    # في حال النجاح نرجع الرابط
    return jsonify({
        "subtitles": [
            {
                "id": "autosync",
                "url": f"{request.host_url}download/{imdb_id}_fixed.srt",
                "lang": "ara",
                "label": "Arabic (Auto-Synced) 🟢"
            }
        ]
    })

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
