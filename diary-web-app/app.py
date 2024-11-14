from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 일기 데이터를 저장하는 간단한 리스트 (DB 대체용)
diaries = []

# 홈 페이지 - 일기 작성 페이지
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        diary_text = request.form['diary']
        feedback = generate_feedback(diary_text)
        diaries.append({"text": diary_text, "feedback": feedback})
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
