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

def save_diary(diary_text, diary_date):
    diary_entry = {
        "date": diary_date,
        "content": diary_text
    }
    
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        diaries = json.load(f)
    diaries.append(diary_entry)
    
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(diaries, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        diary_text = request.form['diary']
        diary_date = request.form['date']
        save_diary(diary_text, diary_date)
        return redirect(url_for('feedback'))
    return render_template('diary.html')

@app.route('/list')
def diary_list():
    with open(DIARY_FILE, 'r', encoding='utf-8') as f:
        diaries = json.load(f)
    diaries = sorted(diaries, key=lambda x: x['date'], reverse=True)
    return render_template('list.html', diaries=diaries)

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
