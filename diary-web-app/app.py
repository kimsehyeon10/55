from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import os
import random

app = Flask(__name__)

DIARY_FILE = 'diaries.json'

if not os.path.exists(DIARY_FILE):
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def load_diaries():
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_diaries(diaries):
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(diaries, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    date = request.args.get('date', '')
    diaries = load_diaries()
    existing_diary = next((entry for entry in diaries if entry['date'] == date), None)
    
    if request.method == 'POST':
        diary_text = request.form['diary']
        if existing_diary:
            existing_diary['content'] = diary_text  # 기존 일기 수정
        else:
            new_diary = {"date": date, "content": diary_text}
            diaries.insert(0, new_diary)  # 새 일기를 최상단에 추가
        save_diaries(diaries)
        return redirect(url_for('today_feedback', date=date))

    return render_template('diary.html', diary=existing_diary, date=date)

@app.route('/list')
def diary_list():
    diaries = load_diaries()
    # 날짜순으로 정렬 (최신 날짜가 상단에 오도록)
    sorted_diaries = sorted(diaries, key=lambda x: x['date'], reverse=True)
    return render_template('list.html', diaries=sorted_diaries)

@app.route('/today_feedback')
def today_feedback():
    selected_date = request.args.get('date', '')
    diaries = load_diaries()
    selected_diary = next((diary for diary in diaries if diary['date'] == selected_date), None)
    feedback_quotes = [
        "오늘 하루도 고생했어요!",
        "마음이 가벼워질 거예요.",
        "하루하루가 더 나아질 거예요."
    ]
    return render_template('today_feedback.html', diary=selected_diary, quote=random.choice(feedback_quotes))

@app.route('/feedback')
def feedback():
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        diaries = json.load(f)
    feedback_quotes = [
        "오늘 하루도 고생했어요!",
        "마음이 가벼워질 거예요.",
        "하루하루가 더 나아질 거예요."
    ]
    return render_template('feedback.html', diaries=diaries, quote=random.choice(feedback_quotes))


if __name__ == '__main__':
    app.run(debug=True)
