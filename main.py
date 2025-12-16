import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="프롬프트 개선 테스트",
    page_icon="⚡",
    layout="wide"
)

# --- 2. 스타일 및 유틸리티 ---
st.markdown("""
<style>
    .stApp { background-color: #f5f5f5; }
    .main-title {
        color: #6a1b9a; text-align: center; padding: 2rem 0;
        font-size: 2.5rem; font-weight: bold;
    }
    .description { text-align: center; color: #666; margin-bottom: 2rem; }
    /* 코드 블록 스타일 조정 */
    .stCodeBlock { background-color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

def strip_blockquote_prefix(text: str) -> str:
    """인용구 포맷(>)을 제거하여 순수 마크다운/코드로 변환"""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.startswith("> "): cleaned.append(line[2:])
        elif line.startswith(">"): cleaned.append(line[1:])
        else: cleaned.append(line)
    return "\n".join(cleaned)

# --- 3. 사이드바 및 API 설정 ---
with st.sidebar:
    st.header("⚙️ 설정")
    user_api_key = st.text_input("Gemini API Key", type="password")

if not user_api_key:
    st.info("👈 사이드바에 API Key를 입력해주세요.")
    st.stop()

# 리소스 캐싱: API 설정은 키가 바뀔 때만 다시 실행
@st.cache_resource
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

try:
    model = configure_genai(user_api_key)
except Exception as e:
    st.error(f"API 설정 오류: {e}")
    st.stop()

# --- 4. 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "어떤 프롬프트를 개선해 드릴까요?"}
    ]

# --- 5. UI 렌더링 (순서 중요: 과거 메시지 먼저 출력) ---
st.markdown('<h1 class="main-title">프롬프트 개선 테스트</h1>', unsafe_allow_html=True)

# 기존 대화 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Assistant 메시지 중 특정 마커가 있으면 코드 블록으로 변환 표시
        if message["role"] == "assistant" and "### ✨ 최적화된 프롬프트" in message["content"]:
            marker = "### ✨ 최적화된 프롬프트"
            parts = message["content"].split(marker, 1)
            st.markdown(parts[0]) # 분석 내용
            if len(parts) > 1:
                st.markdown(marker)
                # 코드 블록으로 깔끔하게 보여주기
                code_content = strip_blockquote_prefix(parts[1])
                st.code(code_content, language="markdown")
        else:
            st.markdown(message["content"])

# --- 6. 사용자 입력 처리 ---
if user_input := st.chat_input("개선할 프롬프트 내용을 입력하세요"):
    # 1) 사용자 메시지 즉시 표시 및 저장
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2) 봇 응답 생성
    prompt_template = """
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
    
    with st.chat_message("assistant"):
        with st.spinner("프롬프트 최적화 중..."):
            try:
                # 챗 세션을 매번 초기화하는 로직이므로 generate_content 사용이 더 안정적
                response = model.generate_content(f"{prompt_template}\n\n사용자 요청: {user_input}")
                assistant_message = response.text
                
                # 3) 화면 출력 로직 (위의 렌더링 로직과 동일하게 적용)
                marker = "### ✨ 최적화된 프롬프트"
                if marker in assistant_message:
                    pre, post = assistant_message.split(marker, 1)
                    st.markdown(pre)
                    st.markdown(marker)
                    st.code(strip_blockquote_prefix(post), language="markdown")
                else:
                    st.markdown(assistant_message)

                # 4) 대화 기록에 저장
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            
            except Exception as e:
                st.error(f"오류 발생: {e}")

# (중요) 여기에 st.rerun()을 쓰지 않습니다. 
# Streamlit은 위 코드가 끝나는 순간, 사용자가 다시 입력할 때까지 대기 상태가 됩니다.
