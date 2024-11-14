import json
import openai

# GPT API 키 설정
openai.api_key = ""

def load_diary(filename):
    """JSON 형식의 일기 파일을 로드하고 반환"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            diary_entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        diary_entries = []
    return diary_entries

def save_diary(filename, diary_entries):
    """일기 파일을 JSON 형식으로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(diary_entries, f, ensure_ascii=False, indent=4)

def get_feedback_for_entry(content):
    """GPT API를 사용해 최신 일기 content에 대한 feedback 생성"""
    prompt = (
        f"당신은 심리 상담가입니다. 아래는 사용자가 작성한 일기입니다.\n\n"
        f"content: {content}\n\n"
        "사용자가 기분을 더 좋게 느낄 수 있도록 공감과 조언을 담은 feedback을 제공해주세요."
    )
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a therapist providing empathetic feedback on diary entries."},
            {"role": "user", "content": prompt}
        ]
    )
    feedback = response.choices[0].message.content
    return feedback

def update_latest_entry_with_feedback(filename):
    """JSON 파일에서 최신 일기를 불러와 feedback을 추가한 후 저장"""
    # 기존 일기 파일 로드
    diary_entries = load_diary(filename)
    
    # 최신 일기 확인 및 feedback 추가
    if diary_entries:
        latest_entry = diary_entries[0]
        feedback = get_feedback_for_entry(latest_entry["content"])
        latest_entry["feedback"] = feedback
        save_diary(filename, diary_entries)
        
        print("최신 일기에 feedback이 추가되었습니다.")
        print(f"date: {latest_entry['date']}")
        print(f"content: {latest_entry['content']}")
        print(f"GPT feedback: {feedback}\n")
    else:
        print("최신 일기에 이미 feedback이 있거나, 일기 content이 없습니다.")

# 파일명 지정 후 최신 일기 feedback 업데이트 함수 호출
# update_latest_entry_with_feedback("diary.json")
