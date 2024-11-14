import json
import openai

# GPT API 키 설정 (환경 변수로 설정하거나 직접 키를 입력)
openai.api_key = ""

def load_diary(filename):
    """JSON 형식의 일기 파일을 로드하고 반환"""
    with open(filename, 'r', encoding='utf-8') as f:
        diary_entries = json.load(f)
    return diary_entries

def get_therapeutic_feedback(diary_entries):
    """GPT API를 사용해 여러 일기에 대해 상담 피드백 생성"""
    # 일기 내용을 날짜 순서대로 합치기
    diary_text = "\n".join([f"날짜: {entry.get('날짜', '알 수 없음')}\n내용: {entry.get('내용', '')}" for entry in diary_entries])
    
    # GPT에 전달할 프롬프트 작성
    prompt = (
        "당신은 심리 상담가입니다. 사용자가 작성한 여러 일기의 내용을 읽고, 사용자에게 공감과 위로를 줄 수 있는 피드백을 제공하세요. "
        "사용자가 겪고 있는 고민이나 스트레스에 대해 이해하고 도움이 될 조언을 해주세요. 기쁜 일에 대해서는 함께 기뻐해주세요.\n\n"
        f"일기 내용:\n{diary_text}\n\n"
        "상담가로서 사용자에게 줄 피드백:"
    )
    
    # GPT API 호출
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a therapist providing thoughtful, empathetic feedback on a series of diary entries."},
            {"role": "user", "content": prompt}
        ]
    )
    feedback = response.choices[0].message.content
    return feedback

def provide_feedback(filename):
    """일기 파일을 읽어 전체 일기에 대한 피드백 제공"""
    diary_entries = load_diary(filename)
    
    if diary_entries:
        feedback = get_therapeutic_feedback(diary_entries)
        print("GPT 상담 피드백:")
        print(feedback)
    else:
        print("일기 내용이 없습니다.")

# 파일명 지정 후 피드백 제공 함수 호출
provide_feedback("diary.json")
