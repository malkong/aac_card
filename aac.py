import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

# --------------------------------------------------
# 0. 환경 변수 로드 (.env 파일 읽기)
# --------------------------------------------------
load_dotenv()

# client 초기화 (GEMINI_API_KEY 자동 인식)
client = genai.Client()


# --------------------------------------------------
# 1. 스키마 정의
# --------------------------------------------------
class UserContextInput(BaseModel):
    intent: str
    intent_detail: str
    response_type: str
    context: Dict[str, Any]

class RecommendedCardIDs(BaseModel):
    card_ids: List[str]


# --------------------------------------------------
# 2. 보유 중인 AAC 카드 데이터셋 (샘플)
# --------------------------------------------------
AAC_DATASET = [
    {"card_id": "c101", "word": "아메리카노", "category": "음료", "intent": "기타", "place": "카페", "image_url": "https://.../americano.png"},
    {"card_id": "c102", "word": "따뜻한 것", "category": "옵션", "intent": "기타", "place": "카페", "image_url": "https://.../hot.png"},
    {"card_id": "c103", "word": "얼음", "category": "옵션", "intent": "기타", "place": "카페", "image_url": "https://.../ice.png"},
    {"card_id": "c104", "word": "주세요", "category": "요청", "intent": "요청", "place": "공통", "image_url": "https://.../please.png"},
    {"card_id": "c105", "word": "화장실", "category": "위치", "intent": "기타", "place": "공통", "image_url": "https://.../toilet.png"},
    {"card_id": "c106", "word": "어디", "category": "질문", "intent": "질문", "place": "공통", "image_url": "https://.../where.png"}
]


# --------------------------------------------------
# 3. 핵심 기능 함수들
# --------------------------------------------------

# [기능 1] AAC 카드 추천
def recommend_cards(user_input: UserContextInput) -> List[dict]:
    req_place = user_input.context.get("place", "공통")
    req_intent = user_input.intent

    candidate_pool = [
        card for card in AAC_DATASET
        if (card.get("place") == req_place or card.get("place") == "공통")
        and (card.get("intent") == req_intent or card.get("intent") == "기타")
    ]

    if not candidate_pool:
        candidate_pool = AAC_DATASET

    prompt = f"""
당신은 AAC 카드 추천 전문가입니다. 사용자의 맥락과 의도를 보고 [후보 카드 목록] 중 가장 적절한 카드 ID 3~5개를 추천하세요.

[사용자 입력]
- 의도: {user_input.intent}
- 의도 상세: {user_input.intent_detail}
- 응답 타입: {user_input.response_type}
- 맥락: {json.dumps(user_input.context, ensure_ascii=False)}

[후보 카드 목록]
{json.dumps(candidate_pool, ensure_ascii=False, indent=2)}

[조건]
후보 목록에 있는 card_id만 선택하여 추천 순서대로 card_ids에 담아주세요.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',  # 접두사 없이 깔끔하게 지정
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecommendedCardIDs,
            ),
        )
        
        parsed_res = RecommendedCardIDs.model_validate_json(response.text)
        
        if not parsed_res or not parsed_res.card_ids:
            return candidate_pool[:4]

        dataset_map = {c["card_id"]: c for c in candidate_pool}
        return [dataset_map[cid] for cid in parsed_res.card_ids if cid in dataset_map]

    except Exception as e:
        print(f"⚠️ 카드 추천 중 오류 발생: {e}. 기본 후보군을 반환합니다.")
        return candidate_pool[:4]


# [기능 2] 카드 조합 ➔ LLM 문장 변환
def generate_sentence(selected_words: List[str], intent_detail: str) -> str:
    prompt = f"""
다음 AAC 카드 단어 조합을 자연스러운 한국어 구어체 문장 한 줄로 다듬어주세요.
- 단어 목록: {', '.join(selected_words)}
- 의도: {intent_detail}

출력은 다른 설명 없이 완성된 문장 하나만 작성하세요.
예시: "따뜻한 아메리카노 한 잔 주세요."
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ 문장 생성 중 오류 발생: {e}. 기본 선택 단어 조합을 반환합니다.")
        # LLM 실패 시 든든한 폴백(Fallback): 선택된 단어를 띄어쓰기로 이어붙임
        return " ".join(selected_words)


# ==========================================
# 4. 실행 흐름
# ==========================================
if __name__ == "__main__":
    # 1. 사용자 입력 조건 설정
    user_input_data = UserContextInput(
        intent="요청",
        intent_detail="따뜻한 아메리카노 주문",
        response_type="문장형",
        context={"place": "카페"}
    )

    # 2. 1단계: AAC 카드 추천받기
    recommended = recommend_cards(user_input_data)
    print("=== 1. 추천된 AAC 카드 목록 ===")
    for card in recommended:
        print(f"- [{card['card_id']}] {card['word']} ({card['category']})")

    # 3. 2단계: 카드를 선택했다고 가정
    selected_ids = ["c101", "c102", "c104"]
    card_map = {c["card_id"]: c["word"] for c in AAC_DATASET}
    selected_words = [card_map[cid] for cid in selected_ids if cid in card_map]

    # 4. 3단계: LLM으로 매끄러운 문장 생성
    final_sentence = generate_sentence(selected_words, user_input_data.intent_detail)
    print("\n=== 2. LLM이 생성한 완성 문장 ===")
    print(f"최종 문장: {final_sentence}")

    # 5. 4단계: gTTS로 음성 파일(.mp3) 생성
    print("\n=== 3. 음성 파일(.mp3) 생성 중... ===")
    tts = gTTS(text=final_sentence, lang='ko')
    output_file = "aac_result.mp3"
    tts.save(output_file)

    print(f"✅ 음성 생성 완료! 프로젝트 폴더에 '{output_file}' 파일이 저장되었습니다.")