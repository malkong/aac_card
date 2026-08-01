import io
import os
from gtts import gTTS
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 0. Gemini 클라이언트 설정 (.env 또는 환경변수의 GEMINI_API_KEY 사용)
# ---------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# ---------------------------------------------------------
# 1. 팀원 모듈 영역 (예: 의도 분석)
# ---------------------------------------------------------
def analyze_intent_mock(speech_text: str) -> str:
    """
    팀원의 llm.py 역할을 시뮬레이션하는 함수입니다.
    실제 팀원 파일이 있다면 해당 함수를 직접 불러와 사용하면 됩니다.
    """
    # 실제로는 팀원의 analyze_intent(speech_text)를 호출하여 intent를 얻음
    print(f"[팀원 모듈] 입력된 발화: '{speech_text}'")
    return "제안"  # 예시 반환값


# ---------------------------------------------------------
# 2. 내 모듈 영역 (LLM 문장 생성)
# ---------------------------------------------------------
def generate_sentence_from_cards(
    selected_cards: list[str], intent: str, speech_text: str = None
) -> str:
    """선택된 카드들과 intent를 바탕으로 Gemini를 사용해 자연스러운 문장을 생성합니다."""
    if not client:
        # API 키가 설정되어 있지 않을 때 기본 폴백
        return " ".join(selected_cards) + " 입니다."

    cards_str = ", ".join(f"'{card}'" for card in selected_cards)
    context_str = f"상대방 발화: \"{speech_text}\"\n" if speech_text else ""

    prompt = f"""
당신은 언어 및 의사소통 보조(AAC) AI 시스템입니다.
사용자가 선택한 단어 카드들과 대화 상대방의 의도(intent)를 고려하여, 상대방에게 전달할 자연스럽고 매끄러운 한 문장을 완성해 주세요.

[조건]
1. 입력받은 단어 카드의 의미를 반드시 모두 포함해야 합니다.
2. 상대방의 의도({intent})에 알맞은 자연스러운 어조(존댓말)로 완성하세요.
3. 부연 설명이나 인삿말 없이, 오직 최종 생성된 문장 하나만 반환하세요.

[상황]
{context_str}상대방의 의도: {intent}
선택된 단어 카드: [{cards_str}]

생성된 문장:
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] LLM 문장 생성 실패: {e}")
        return " ".join(selected_cards) + " 입니다."


# ---------------------------------------------------------
# 3. 내 모듈 영역 (gTTS 음성 변환 및 파일 저장)
# ---------------------------------------------------------
def save_tts_audio(text: str, output_filename: str = "output.mp3"):
    """생성된 문장을 gTTS로 MP3 파일로 저장합니다."""
    tts = gTTS(text=text, lang="ko", slow=False)
    tts.save(output_filename)
    print(f"[gTTS] '{output_filename}' 파일로 음성이 저장되었습니다.")


# ---------------------------------------------------------
# 4. 전체 실행 파이프라인 (메인 로직)
# ---------------------------------------------------------
if __name__ == "__main__":
    # [1단계] 상대방 발화 입력 및 팀원 모듈(의도 분석) 호출
    partner_speech = "오늘 수업 끝나고 같이 카페 갈래?"
    intent = analyze_intent_mock(partner_speech)
    print(f"-> 추출된 의도(intent): {intent}\n")

    # [2단계] 사용자가 화면에서 고른 카드 목록 (가정)
    user_selected_cards = ["오늘", "좋아", "카페"]
    print(f"[사용자] 선택한 카드: {user_selected_cards}")

    # [3단계] 카드 + intent -> LLM 문장 생성
    generated_sentence = generate_sentence_from_cards(
        selected_cards=user_selected_cards,
        intent=intent,
        speech_text=partner_speech,
    )
    print(f"-> 최종 생성된 문장: \"{generated_sentence}\"\n")

    # [4단계] gTTS로 음성 변환하여 mp3 파일로 저장
    save_tts_audio(generated_sentence, "output.mp3")