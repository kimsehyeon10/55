import json
import openai

openai.api_key = ""

def load_all_diaries(filename):
    """JSON 형식의 일기 파일을 로드하여 모든 일기 내용을 하나의 텍스트로 반환"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            diary_entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("일기 파일을 찾을 수 없거나 손상되었습니다.")
        return ""
    
    return "\n".join([f"날짜: {entry['날짜']}\n내용: {entry['내용']}" for entry in diary_entries])

def summarize_chat(messages):
    """메시지 요약 생성"""
    summary_prompt = (
        "다음은 사용자와 상담가의 대화 내용입니다. 중요한 내용을 요약해 주세요:\n\n"
        + "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-10:]])
    )
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant summarizing the conversation."},
            {"role": "user", "content": summary_prompt}
        ]
    )
    
    summary = response.choices[0].message.content
    return summary

def start_chat_with_gpt(diary_content):
    """GPT와 대화할 수 있는 상담 기능"""
    print("=== GPT와의 상담을 시작합니다 ===")
    print("이전 일기 내용에 대해 질문을 입력하세요. '종료'라고 입력하면 대화가 종료됩니다.\n")
    
    initial_prompt = (
        "당신은 심리 상담가입니다. 사용자가 작성한 여러 일기 내용을 읽고, 이 내용을 바탕으로 상담을 해주세요. "
        "사용자가 질문을 할 때마다 이에 맞는 공감과 조언을 제공하세요. "
        "다음은 사용자가 작성한 일기 전체 내용입니다.\n\n"
        f"{diary_content}\n\n"
        "이제 사용자가 질문을 입력할 것입니다. 사용자 질문에 상담가로서 응답해 주세요."
    )
    
    messages = [
        {"role": "system", "content": "You are a therapist providing empathetic and thoughtful feedback based on diary entries."},
        {"role": "user", "content": initial_prompt}
    ]
    
    while True:
        user_input = input("사용자: ")
        if user_input.lower() == "종료":
            print("=== 상담을 종료합니다 ===")
            break
        
        messages.append({"role": "user", "content": user_input})
        
        # 토큰 수가 많아질 경우 요약 처리
        if len(messages) > 15:
            summary = summarize_chat(messages)
            messages = messages[:2] + [{"role": "system", "content": f"대화 요약: {summary}"}]
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        print(f"GPT 상담가: {assistant_response}\n")
        
        messages.append({"role": "assistant", "content": assistant_response})

# 파일명 지정 후 GPT와의 상담 시작
diary_content = load_all_diaries("diary.json")
if diary_content:
    start_chat_with_gpt(diary_content)
