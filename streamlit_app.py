import streamlit as st
from openai import OpenAI
import random

# Title and brief description
st.title("💬 Chatbot & 덧셈 연습")
st.write("사이드바에서 `앱 모드`를 선택하세요: 챗봇 테스트 또는 덧셈 연습.")

# 앱 모드 선택
mode = st.sidebar.selectbox("앱 모드", ["Chatbot", "덧셈 연습"])

# ===== 덧셈 연습 모드 초기화 =====
if "practice_active" not in st.session_state:
    st.session_state.practice_active = False
if "practice_questions" not in st.session_state:
    st.session_state.practice_questions = []
if "practice_idx" not in st.session_state:
    st.session_state.practice_idx = 0
if "practice_score" not in st.session_state:
    st.session_state.practice_score = 0
if "practice_num" not in st.session_state:
    st.session_state.practice_num = 5
if "practice_max_operand" not in st.session_state:
    st.session_state.practice_max_operand = 10
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""

def start_practice(num_questions: int, max_operand: int):
    st.session_state.practice_questions = [
        (random.randint(0, max_operand), random.randint(0, max_operand))
        for _ in range(num_questions)
    ]
    st.session_state.practice_idx = 0
    st.session_state.practice_score = 0
    st.session_state.practice_num = num_questions
    st.session_state.practice_max_operand = max_operand
    st.session_state.practice_active = True
    st.session_state.last_feedback = ""

def reset_practice():
    st.session_state.practice_active = False
    st.session_state.practice_questions = []
    st.session_state.practice_idx = 0
    st.session_state.practice_score = 0
    st.session_state.last_feedback = ""

if mode == "덧셈 연습":
    with st.sidebar.expander("덧셈 설정", expanded=True):
        num_q = st.number_input("문제 수", min_value=1, max_value=100, value=int(st.session_state.practice_num), step=1)
        max_op = st.number_input("최대 피연산자 (0~)", min_value=1, max_value=10000, value=int(st.session_state.practice_max_operand), step=1)
        if st.button("연습 시작"):
            start_practice(int(num_q), int(max_op))
        if st.button("초기화/리셋"):
            reset_practice()

    st.header("덧셈 문제 연습")

    if not st.session_state.practice_active:
        st.info("사이드바에서 문제 수와 최대 피연산자를 설정한 뒤 '연습 시작'을 누르세요.")
    else:
        idx = st.session_state.practice_idx
        total = st.session_state.practice_num
        a, b = st.session_state.practice_questions[idx]
        st.markdown(f"**문제 {idx+1} / {total}**")
        st.markdown(f"### {a} + {b} = ?")

        answer = st.number_input("정답을 입력하세요", key=f"answer_{idx}", step=1)
        if st.button("제출", key=f"submit_{idx}"):
            correct = (int(answer) == (a + b))
            if correct:
                st.session_state.practice_score += 1
                st.session_state.last_feedback = "정답입니다! 🎉"
            else:
                st.session_state.last_feedback = f"틀렸습니다. 정답은 {a + b} 입니다."

            # 진행
            if st.session_state.practice_idx + 1 < total:
                st.session_state.practice_idx += 1
            else:
                st.session_state.practice_active = False

        if st.session_state.last_feedback:
            st.info(st.session_state.last_feedback)

        if not st.session_state.practice_active:
            st.success(f"연습 종료! 점수: {st.session_state.practice_score} / {total}")
            if st.button("다시 시작"):
                start_practice(total, st.session_state.practice_max_operand)

# ===== Chatbot 모드 =====
else:
    # Chatbot 모드에서는 API 키를 입력해야 작동합니다.
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("OpenAI API 키를 입력해야 챗봇 기능을 사용할 수 있습니다.", icon="🗝️")
    else:
        client = OpenAI(api_key=openai_api_key)

        # Initialize session state variables for chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = ""
        if "model" not in st.session_state:
            st.session_state.model = "gpt-3.5-turbo"
        if "temperature" not in st.session_state:
            st.session_state.temperature = 0.7
        if "max_tokens" not in st.session_state:
            st.session_state.max_tokens = 512

        # Sidebar model settings expander
        with st.sidebar.expander("Model settings", expanded=False):
            st.markdown("**모델 설정 (접었다 펼치기 가능)**")
            model_options = [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4o",
                "gpt-4o-mini",
            ]
            st.session_state.model = st.selectbox("Model", model_options, index=model_options.index(st.session_state.model) if st.session_state.model in model_options else 0)
            st.session_state.system_prompt = st.text_area("System prompt (시스템 프롬프트)", value=st.session_state.system_prompt, help="Assistant 동작을 제어하는 시스템 레벨 프롬프트를 입력하세요.")
            st.session_state.temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(st.session_state.temperature), step=0.01, help="응답의 창의성 (0.0-1.0)")
            st.session_state.max_tokens = st.number_input("Max Tokens", min_value=1, max_value=32768, value=int(st.session_state.max_tokens), step=1, help="생성될 최대 토큰 수")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("메시지를 입력하세요..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Build messages list including system prompt
            messages_to_send = []
            if st.session_state.system_prompt.strip():
                messages_to_send.append({"role": "system", "content": st.session_state.system_prompt})
            messages_to_send.extend([
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ])

            try:
                stream = client.chat.completions.create(
                    model=st.session_state.model,
                    messages=messages_to_send,
                    temperature=float(st.session_state.temperature),
                    max_tokens=int(st.session_state.max_tokens),
                    stream=True,
                )

                with st.chat_message("assistant"):
                    response = st.write_stream(stream)

                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"API 호출 중 오류가 발생했습니다: {e}")
