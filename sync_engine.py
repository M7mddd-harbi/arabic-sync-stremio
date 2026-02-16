import sys
import os
import re

def normalize_arabic(text):
    tashkeel_re = re.compile(r'[\u064B-\u0652]')
    text = tashkeel_re.sub('', text)
    text = re.sub(r'[إأآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text

def process_srt(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # هنا نقوم بمعالجة النص العربي فقط (المزامنة ستعتمد على الملف الأصلي)
        normalized_content = normalize_arabic(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(normalized_content)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)
    
    input_srt = sys.argv[2]
    output_srt = sys.argv[3]
    
    if process_srt(input_srt, output_srt):
        print("Success")
    else:
        sys.exit(1)

