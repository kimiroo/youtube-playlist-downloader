import re

def clean_title(title: str):
    new_str = re.sub(r"^(블루 아카이브 |블아 )", "", title).strip() # Azi
    new_str = re.sub(r"^【 블루아카이브 】 ", "", new_str).strip() # 7uck2
    return new_str

def clean_filename(filename: str):
    new_str = re.sub(r'[\\/:*?"<>|]', "_", filename) # Windows restricted characters
    new_str = re.sub(r'/', "_", new_str) # Unix restricted character
    return new_str

def clean_channel_name(name: str):
    new_str = re.sub(r"^중년게이머 ", "", name).strip()  # memolkim
    new_str = re.sub(r" 다시보기$", "", new_str).strip() # Azi
    new_str = re.sub(r"의 수면교실$", "", new_str).strip() # 7uck2
    return new_str

def special_processing_7ucky(title: str):
    if '-' in title:
        parts = title.rsplit('-', 1)  # 마지막 '-' 기준으로 나눔
        suffix = parts[1].strip()  # 뒤쪽 부분만 가져오고 공백 제거
        return suffix if suffix else title  # 빈 문자열이 되면 원래 제목 유지
    return title