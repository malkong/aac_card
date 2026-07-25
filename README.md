# 📱 Context-Aware AAC Local Backend System
사용자의 현재 상황(장소)과 의도를 분석하여 최적의 AAC(대안언어소통) 카드를 추천하고, 선택된 카드 조합을 자연스러운 한국어 구어체 문장으로 변환 및 음성(TTS)으로 출력하는 파이썬 기반 AAC 백엔드 파이프라인입니다.

✨ 주요 특징 (Key Features)
상황 기반 AAC 카드 필터링: 입력된 장소(place) 및 의도(intent) 데이터에 맞춰 1차 후보군을 빠르게 추출합니다.

LLM 기반 카드 추천 (Structured Output): 구글 Gemini 2.0 모델과 Pydantic 스키마를 결합하여, 상황에 가장 어울리는 카드를 JSON 형태로 정확히 추천받습니다.

자연스러운 문장 합성 (Text Style Transfer): 단어 위주의 AAC 카드 조합("아메리카노", "따뜻한 것", "주세요")을 완벽한 한국어 문장("따뜻한 아메리카노 한 잔 주세요.")으로 다듬습니다.

음성 출력 (Text-to-Speech): 완성된 문장을 gTTS를 통해 MP3 파일로 즉시 변환하여 보완대체 소통을 완결합니다.

안정적인 예외 처리 (Fallback System): API 요청 제한이나 네트워크 오류 발생 시에도 기본 카드군 및 단어 조합 문장을 반환하여 서비스 중단을 방지합니다.

🔄 전체 시스템 흐름 (Workflow)
코드 스니펫
graph TD
    A[사용자 입력: 맥락 & 의도] --> B[1차 Rule-based 카드 필터링]
    B --> C[Gemini 2.0 카드 추천 Engine]
    C --> D[사용자 카드 선택]
    D --> E[Gemini 2.0 구어체 문장 변환]
    E --> F[gTTS 음성 합성 .mp3]

    
User Context Input: 사용자의 장소(예: 카페), 의도(예: 요청) 입력

Card Recommendation: Rule-based 필터링 ➔ Gemini AI가 최선의 카드 ID 세트 반환

Sentence Generation: 선택된 AAC 단어들을 Natural Korean 문장으로 변환

Audio Output: aac_result.mp3 음성 파일 생성

🛠 Tech Stack
Language: Python 3.13

AI Model: Google Gemini API (google-genai SDK, gemini-2.0-flash)

Data Validation: Pydantic v2

TTS Engine: gTTS (Google Text-to-Speech)

Environment: python-dotenv



설치 패키지:pip install google-genai pydantic gtts python-dotenv
