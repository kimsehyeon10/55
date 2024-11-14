from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, send,emit
from datetime import datetime
import json
import os
import random
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

openai.api_key = ''

system_prompt = """
You are a compassionate and insightful friend providing personalized feedback based on the user's diary entries. Speak in a warm, friendly, and conversational tone, offering advice and support as a close friend would. 
Go beyond general or typical advice by tailoring your words closely to the unique details and emotions in the user's entries. 
Your feedback should:
- Celebrate the user's positive experiences with genuine joy and personal remarks, encouraging them to savor these moments.
- Offer focused guidance and specific advice that acknowledges the nuances of their challenges, as a supportive friend would.
- Provide comforting words and understanding during difficult times, speaking to them in a way that feels relatable and reassuring.
- Suggest practical stress-relief techniques or coping strategies directly relevant to their shared struggles and daily life, as if sharing helpful tips from your own experience.

Make the user feel genuinely understood, speaking in a friendly, non-judgmental way, as though you are a friend who truly cares about their well-being. Let each response feel like it’s crafted just for them, providing warm, thoughtful support on their personal journey. Keep responses concise and limit them to 4 sentences.
Please make sure to say it in Korean.
"""


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

def load_all_diaries(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            diary_entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""
    return "\n".join([f"date: {entry['date']}\ncontent: {entry['content']}" for entry in diary_entries])

def get_gpt_response(user_message):
    all_diaries = load_all_diaries(DIARY_FILE)
    # if count == 0:
    #     user_prompt = f"Here are all the previous diary entries:\n{all_diaries}\n\nUser's Questions:\n{user_message}"
    # else:
    #     user_prompt = f"Here are all the previous diary entries:\n{all_diaries}\n\nUser's Questions:\n{user_message}"
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"{system_prompt}\n\nFull diary content:\n{all_diaries}"},
            {"role": "user", "content": f"{user_message}"}
        ]
    )
    return response.choices[0].message.content


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
            existing_diary['content'] = diary_text
        else:
            new_diary = {"date": date, "content": diary_text}
            diaries.insert(0, new_diary)
        save_diaries(diaries)
        return redirect(url_for('today_feedback', date=date))

    return render_template('diary.html', diary=existing_diary, date=date)

@app.route('/list')
def diary_list():
    diaries = load_diaries()
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

def load_all_diaries(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            diary_entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""
    return "\n".join([f"date: {entry['date']}\ncontent: {entry['content']}" for entry in diary_entries])

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@socketio.on('user_message')
def handle_user_message(user_message):
    gpt_response = get_gpt_response(user_message)
    emit('bot_response', gpt_response)

if __name__ == '__main__':
    socketio.run(app, debug=True)
