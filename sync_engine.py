import sys
import os
import subprocess
import json
import unicodedata
import re

def normalize_arabic(text):
    """
    Normalizes Arabic text by removing diacritics and unifying certain characters.
    """
    # Remove diacritics (Tashkeel)
    tashkeel_re = re.compile(r'[\u064B-\u0652]')
    text = tashkeel_re.sub('', text)
    
    # Normalize Alef
    text = re.sub(r'[إأآ]', 'ا', text)
    
    # Normalize Yeh/Alef Maksura
    text = re.sub(r'ى', 'ي', text)
    
    # Normalize Te Marbuta
    text = re.sub(r'ة', 'ه', text)
    
    return text

def sync_subtitles(video_url, srt_input_path, srt_output_path):
    """
    Uses ffsubsync to align SRT with video audio.
    """
    try:
        print(f"Syncing {srt_input_path} with {video_url}...")
        # We use ffsubsync via subprocess for reliability
        result = subprocess.run([
            'ffs', 
            video_url, 
            '-i', srt_input_path, 
            '-o', srt_output_path,
            '--overwrite-input'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFsubsync error: {result.stderr}")
            return False
            
        print("Sync completed successfully.")
        return True
    except Exception as e:
        print(f"Exception during sync: {e}")
        return False

def process_arabic_text(srt_path):
    """
    Reads an SRT file and applies Arabic normalization to each line.
    """
    if not os.path.exists(srt_path):
        return
        
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    normalized_lines = []
    for line in lines:
        # We only normalize lines that are not timestamps or numbers
        if not re.match(r'^\d+$', line.strip()) and '-->' not in line:
            normalized_lines.append(normalize_arabic(line))
        else:
            normalized_lines.append(line)
            
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.writelines(normalized_lines)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 sync_engine.py <video_url> <input_srt> <output_srt>")
        sys.exit(1)
        
    video_url = sys.argv[1]
    input_srt = sys.argv[2]
    output_srt = sys.argv[3]
    
    success = sync_subtitles(video_url, input_srt, output_srt)
    if success:
        process_arabic_text(output_srt)
        print("Final processing done.")
    else:
        sys.exit(1)
