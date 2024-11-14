from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

# JSON 파일 경로
DIARY_FILE = 'diaries.json'

# 기존에 파일이 없다면 빈 리스트로 초기화
if not os.path.exists(DIARY_FILE):
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# 일기를 JSON 파일에 저장하는 함수
def save_diary(diary_text):
    # 현재 날짜와 일기 내용 생성
    diary_entry = {
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "content": diary_text
    }
    
    # 기존 파일에서 데이터를 읽어와서 새로운 일기를 추가한 후 다시 저장
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        diaries = json.load(f)
    diaries.append(diary_entry)
    
    # 업데이트된 데이터를 UTF-8 인코딩으로 파일에 저장
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(diaries, f, ensure_ascii=False, indent=4)

# 일기 데이터를 저장하는 간단한 리스트 (DB 대체용)
diaries = []

# 홈 페이지 - 일기 작성 페이지
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        diary_text = request.form['diary']
        feedback = generate_feedback(diary_text)
        diaries.append({"text": diary_text, "feedback": feedback})
        save_diary(diary_text)  # 일기 내용을 JSON 파일에 저장
        return redirect(url_for('feedback'))
    return render_template('index.html')

# 피드백 페이지
@app.route('/feedback')
def feedback():
    last_diary = diaries[-1] if diaries else None
    return render_template('feedback.html', diary=last_diary)

# 피드백 생성 함수 (간단한 감정 피드백 예시)
def generate_feedback(diary_text):
    if "행복" in diary_text:
        return "오늘 정말 좋은 날이었군요! 계속해서 긍정적인 에너지를 유지하세요."
    elif "슬픔" in diary_text:
        return "힘든 시간을 보내고 있군요. 슬픔을 충분히 느끼고 스스로를 위로해주세요."
    else:
        return "일상을 기록하는 것만으로도 마음이 치유될 수 있어요. 계속해서 써보세요!"

if __name__ == '__main__':
    app.run(debug=True)
