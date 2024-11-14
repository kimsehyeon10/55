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

DIARY_FILE = 'diaries.json'

if not os.path.exists(DIARY_FILE):
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def load_diaries():
    """diaries.json 파일에서 일기 데이터를 불러옴"""
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return []

def save_diaries(diaries):
    """일기 데이터를 diaries.json에 저장"""
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(diaries, f, ensure_ascii=False, indent=4)

def get_gpt_response(user_message):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

def save_message_to_json(message):
    """GPT의 응답을 JSON 파일에 저장하며, 최신 응답이 최상단에 위치하도록 저장"""
    chat_entry = {"sender": "GPT", "message": message}
    
    # 기존 메시지 불러오기
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as file:
            chat_history = json.load(file)
    else:
        chat_history = []
    
    # 최신 메시지를 0번째 위치에 추가
    chat_history.insert(0, chat_entry)
    
    # JSON 파일에 저장
    with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as file:
        json.dump(chat_history, file, ensure_ascii=False, indent=4)




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    date = request.args.get('date', '')
    diaries = load_diaries()
    
    if request.method == 'POST':
        diary_text = request.form['diary']
        
        # 같은 날짜의 기존 데이터를 삭제
        diaries = [entry for entry in diaries if entry['date'] != date]
        
        # 수정된 데이터를 최상단에 추가
        new_entry = {"date": date, "content": diary_text}
        diaries.insert(0, new_entry)
        
        # 저장
        save_diaries(diaries)
        
        return redirect(url_for('today_feedback', date=date))

    # GET 요청 시 현재 날짜에 해당하는 일기 데이터를 가져옴
    existing_diary = next((entry for entry in diaries if entry['date'] == date), None)
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


#openai.api_key = ''
# JSON 파일 경로 설정
CHAT_HISTORY_FILE = 'chat_history.json'

DIARY_FILE = 'diaries.json'

if not os.path.exists(DIARY_FILE):
    with open(DIARY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def load_all_diaries(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            diary_entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""
    return "\n".join([f"date: {entry['date']}\ncontent: {entry['content']}" for entry in diary_entries])

def start_chat_with_gpt(diary_content):
    messages = [
        {"role": "system", "content": "You are a therapist providing empathetic feedback based on diary entries."},
        {"role": "user", "content": f"사용자가 작성한 일기: {diary_content}"}
    ]
    
    @socketio.on('user_message')
    def handle_user_message(user_message):
        messages.append({"role": "user", "content": user_message})
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})
        
        emit('bot_response', assistant_response)  # 클라이언트에 assistant_response 전송

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@socketio.on('user_message')
def handle_user_message(user_message):
    gpt_response = get_gpt_response(user_message)
    # GPT 응답을 JSON 파일에 저장
    save_message_to_json(gpt_response)
    emit('bot_response', gpt_response)

if __name__ == '__main__':
    socketio.run(app, debug=True)
