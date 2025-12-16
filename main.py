import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="프롬프트 개선 테스트",
    page_icon="🤑",
    layout="wide"
)

# Blockquote 제거 유틸 (코드블록 출력 시 '>' 접두어 제거)
def strip_blockquote_prefix(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.startswith("> "):
            cleaned.append(line[2:])
        elif line.startswith(">"):
            cleaned.append(line[1:])
        else:
            cleaned.append(line)
    return "\n".join(cleaned)

# CSS 스타일 적용
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 5px solid #9c27b0;
    }
    .main-title {
        color: #6a1b9a;
        text-align: center;
        padding: 2rem 0;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .description {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 제목과 설명
st.markdown('<h1 class="main-title">프롬프트 개선 테스트</h1>', unsafe_allow_html=True)
st.markdown('<p class="description">프롬프트 개선 테스트용 페이지입니다.</p>', unsafe_allow_html=True)

# Gemini API 설정을 위한 사이드바 (사용자별 API 키 입력)
with st.sidebar:
    st.header("⚙️ Gemini API 설정")
    user_api_key = st.text_input(
        "Gemini API Key를 입력하세요",
        type="password",
        help="Google AI Studio에서 발급받은 본인의 Gemini API 키를 입력하면 됩니다."
    )

# 키가 없으면 진행 중단 (모든 사용자가 자기 키를 넣어야 사용 가능)
if not user_api_key:
    st.warning("왼쪽 사이드바에 **Gemini API Key**를 입력해야 챗봇을 사용할 수 있습니다.")
    st.stop()

# Gemini API 설정 (사용자가 입력한 키로 설정)
try:
    genai.configure(api_key=user_api_key)
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
    st.stop()

# 모델 설정
model = genai.GenerativeModel('gemini-2.5-flash')

# 세션 상태 초기화
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    # 초기 메시지 추가
    initial_message = "프롬프트를 입력해주세요"
    st.session_state.messages.append({"role": "assistant", "content": initial_message})

# 사용자 입력 (chat_input으로 말풍선 UX)
user_input = st.chat_input("문제나 답변을 입력해주세요")

if user_input:
    # 새 질문이 들어오면 즉시 이전 대화/맥락 삭제 후 새 세션으로 시작
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

    # 사용자 메시지 즉시 표시
    with st.chat_message("user"):
        st.markdown(user_input)

    # 챗봇 프롬프트 설정
    prompt = """
## Role & Objective
당신은 Google Gemini API 및 LLM 활용에 통달한 **'수석 프롬프트 엔지니어(Chief Prompt Engineer)'**입니다. 
당신의 목표는 사용자의 요청을 분석하여, 상황에 맞춰 내용을 갈아 끼울 수 있는 **'최적화된 프롬프트 템플릿'**을 설계해 주는 것입니다.

## Optimization Guidelines (Critical for Template Creation)
1. **변수 분리 (Variable Isolation):** 사용자의 입력이 구체적이지 않거나(예: "여행 블로그 써줘"), 범용적인 요청일 경우 **절대로 특정 주제를 임의로 확정하지 마십시오.** 대신 사용자가 나중에 입력해야 할 정보(주제, 타겟, 톤앤매너 등)를 `# Input Data` 섹션에 변수 형태로 비워두십시오.
2. **명확한 지시 (Clear Instructions):** 모델이 수행해야 할 작업의 본질적인 논리 구조를 설계하십시오.
3. **페르소나 부여 (Adopt a Persona):** 작업에 가장 적합한 전문가 페르소나를 정의하십시오.
4. **구분자 사용 (Use Delimiters):** 섹션을 명확히 구분하십시오.
5. **형식 지정 (Output Formatting):** 결과물의 구조를 미리 정의하십시오.

## Operational Process
1. **의도 파악:** 사용자가 원하는 작업이 '일회성 실행'인지 '반복 가능한 템플릿'인지 파악합니다. (대부분 프롬프트 요청은 템플릿을 원합니다.)
2. **변수 식별:** 프롬프트가 작동하기 위해 꼭 필요한 데이터(예: 여행지 이름, 제품명, 수신자 등)가 무엇인지 파악합니다.
3. **템플릿 작성:** 변수를 `# Input Data` 섹션으로 몰아넣고, 본문에서는 해당 변수를 참조하도록 작성합니다.
4. **출력:** 인용구(>) 스타일을 적용하여 출력합니다.

## Output Format
**중요: 답변 출력 시 Markdown Code Block(```)을 사용하지 말고, 인용구(>)를 사용하여 시각적으로 구분하십시오.**
`# Input Data` 섹션은 사용자가 복사 후 내용을 채워 넣을 수 있도록 안내 문구로 작성해야 합니다.

---
### 🔍 분석 및 개선 포인트
* **적용된 전략:** (예: 변수 분리, 구조화 등)
* **개선 이유:** (주제를 고정하지 않고 사용자가 입력할 수 있도록 템플릿화 함)

### ✨ 최적화된 프롬프트
> # Role
> [역할 정의]
>
> # Context
> [배경 설명 - 변수 부분을 포괄적으로 서술]
>
> # Task
> [구체적인 작업 지시]
>
> # Constraints
> [제약 조건]
>
> # Output Format
> [출력 형식]
>
> # Input Data
> - **주제/소재:** [여기에 원하시는 주제를 입력하세요]
> - **타겟 독자:** [글을 읽을 대상을 입력하세요]
> - **강조할 점:** [포함하고 싶은 핵심 내용을 입력하세요]
---

## Initialization
지금부터 사용자의 입력을 분석하여, 사용자가 원하는 데이터를 나중에 채워 넣을 수 있는 **'재사용 가능한 프롬프트 양식'**을 작성하십시오. 임의로 예시를 채워 넣어 템플릿의 범용성을 해치지 마십시오.

"""

    with st.spinner("생각 중..."):
        try:
            # Gemini 모델에 메시지 전송
            response = st.session_state.chat.send_message(f"{prompt}\n\n사용자: {user_input}")
            assistant_message = response.text

            # 챗봇 메시지 상태에 저장
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})

            # 응답이 준비되면 새 상태로 다시 렌더링
            st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

# 채팅 히스토리 표시 (말풍선 형태로 교차 출력)
for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        if message["role"] == "assistant":
            marker = "### ✨ 최적화된 프롬프트"
            if marker in message["content"]:
                pre, post = message["content"].split(marker, 1)
                if pre.strip():
                    st.markdown(pre)
                block = strip_blockquote_prefix(f"{marker}{post}")
                st.code(block, language="markdown")
            else:
                st.code(strip_blockquote_prefix(message["content"]), language="markdown")
        else:
            st.markdown(message["content"])
