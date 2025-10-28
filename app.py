# -*- coding: utf-8 -*-
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="한신 초등 은유 이야기 기계", page_icon="✨")
st.image("logo.PNG", width=120)
st.title("✨ 한신 초등학교 친구들의 이야기 실력을 볼까요?")
st.caption("좋아하는 단어로 주인공을 먼저 만들고, 그 다음에 이야기를 이어가요!")

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", "")
client = None
if not OPENAI_KEY:
    st.warning("⚠️ OPENAI_API_KEY가 설정되지 않았어요. Streamlit Cloud의 Secrets에 `OPENAI_API_KEY = \"sk-...\"` 형태로 추가해 주세요.")
else:
    client = OpenAI(api_key=OPENAI_KEY)

st.subheader("👧 학생 정보 입력")
col1, col2, col3 = st.columns(3)
cls = col1.text_input("학급 (예: 3-2)")
num = col2.text_input("번호")
name = col3.text_input("이름")

BANNED_PATTERNS = [
    r"살인", r"죽이", r"폭력", r"피바다", r"학대", r"총", r"칼", r"폭탄",
    r"kill", r"murder", r"gun", r"knife", r"blood", r"assault", r"bomb",
    r"성\\s*행위", r"야동", r"포르노", r"음란", r"가슴", r"성기", r"자위",
    r"porn", r"sex", r"xxx", r"nude", r"naked",
]
BAN_RE = re.compile("|".join(BANNED_PATTERNS), re.IGNORECASE)

def words_valid(words):
    for w in words:
        if not w:
            return False, "단어 3개를 모두 입력해 주세요."
        if BAN_RE.search(w):
            return False, "적절하지 않은 단어입니다. 다시 입력해 주세요."
    return True, "OK"

st.subheader("1️⃣ 좋아하는 단어 3개로 주인공 만들기")
c1, c2, c3 = st.columns(3)
w1 = c1.text_input("단어 1", max_chars=12)
w2 = c2.text_input("단어 2", max_chars=12)
w3 = c3.text_input("단어 3", max_chars=12)

st.session_state.setdefault("character_desc", "")

if st.button("주인공 만들기 👤✨"):
    words = [w1.strip(), w2.strip(), w3.strip()]
    ok, msg = words_valid(words)
    if not ok:
        st.error(msg)
    elif client is None:
        st.error("OPENAI_API_KEY가 없어요. Secrets에 추가해 주세요.")
    else:
        prompt = (
            "초등학교 3학년 어린이들이 읽기 쉬운 한국어로, "
            f"'{words[0]}', '{words[1]}', '{words[2]}' 세 단어를 모두 사용해서 "
            "주인공의 이름, 성격, 좋아하는 일, 사는 곳을 소개하는 3~4문장을 써 주세요. "
            "예: '이름은 루비예요. 밝고 용감한 성격이에요. ...'처럼 친근한 말투로 작성해 주세요."
        )
        try:
            resp = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                max_output_tokens=300,
            )
            desc = resp.output_text.strip()
            st.session_state["character_desc"] = desc
            st.success("💫 주인공이 완성되었어요!")
        except Exception as e:
            st.error(f"주인공 생성 중 문제가 발생했어요: {e}")

if st.session_state["character_desc"]:
    st.markdown("### 👤 주인공 소개")
    st.write(st.session_state["character_desc"])

if st.session_state["character_desc"]:
    st.divider()
    st.subheader("2️⃣ 주인공의 이야기를 써 볼까요? ✍️")

    TITLES = [
        "옛날에", "그리고 매일", "그러던 어느 날",
        "그래서", "그래서", "그래서",
        "마침내", "그날 이후",
    ]

    for i in range(8):
        st.session_state.setdefault(f"story_{i}", "")
        st.session_state.setdefault(f"auto_{i}", False)

    for i, title in enumerate(TITLES):
        st.markdown(f"#### {title}")
        if i in [0, 2, 4, 6, 7]:
            st.session_state[f"story_{i}"] = st.text_area(
                f"{title} 내용을 적어보세요",
                value=st.session_state[f"story_{i}"],
                height=80,
                key=f"story_input_{i}",
            )
        else:
            if st.button(f"{title} 자동 이어쓰기 🪄", key=f"auto_btn_{i}"):
                prev_all = " ".join(
                    [st.session_state[f"story_{j}"] for j in range(i) if st.session_state[f"story_{j}"]]
                )
                if not prev_all.strip():
                    st.warning("이전까지의 이야기를 먼저 적어 주세요!")
                elif client is None:
                    st.error("OPENAI_API_KEY가 없어요. Secrets에 추가해 주세요.")
                else:
                    character = st.session_state.get("character_desc", "")
                    prompt = (
                        "초등학교 3학년 어린이가 쓴 이야기를 이어서 써 주세요. "
                        "지금까지의 이야기 내용을 읽고 자연스럽게 이어지게 200~300자로 써 주세요. "
                        "어려운 말은 피하고 따뜻한 문체로 작성해 주세요.\n\n"
                        f"지금까지의 이야기:\n'''{prev_all}'''\n"
                        f"주인공 정보:\n{character}"
                    )
                    try:
resp = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    max_output_tokens=300,
)
# 안전하게 텍스트 추출
try:
    desc = resp.output_text.strip()
except AttributeError:
    desc = resp.output[0].content[0].text.strip() if resp.output else ""

                        st.session_state[f"story_{i}"] = auto_text
                        st.session_state[f"auto_{i}"] = True
                        st.info("자동으로 이어썼어요 ✨")
                    except Exception as e:
                        st.error(f"이어쓰기 중 문제가 발생했어요: {e}")

            st.text_area(
                f"{title} 자동 생성된 내용",
                value=st.session_state[f"story_{i}"],
                height=120,
                disabled=True,
                key=f"auto_output_{i}",
            )

    if all(st.session_state[f"story_{i}"].strip() for i in range(8)):
        st.divider()
        st.subheader("🎉 완성된 이야기")
        parts = []
        for i in range(8):
            key_story = f"story_{i}"
            parts.append(f"**{TITLES[i]}**\n{st.session_state[key_story]}")
        story_text = "\n\n".join(parts)

        if client is None:
            st.write(story_text)
        else:
            summary_prompt = (
                "다음은 초등학생이 쓴 8단 이야기입니다. 자연스럽게 이어지는 하나의 이야기로 정리해 주세요. "
                "너무 딱딱하지 않게, 아이가 쓴 것처럼 부드럽고 따뜻한 문체로 써 주세요.\n\n" + story_text
            )
            try:
                resp = client.responses.create(
                    model="gpt-4o-mini",
                    input=summary_prompt,
                    max_output_tokens=700,
                )
                final_story = resp.output_text.strip()
                st.write(final_story)
                st.download_button(
                    "📥 완성된 이야기 저장하기 (txt)",
                    data=final_story,
                    file_name=f"{cls}_{num}_{name}_story.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"완성 이야기 정리 중 문제가 발생했어요: {e}")
else:
    st.info("먼저 단어 3개로 주인공을 만들어 주세요. 그 다음에 이야기 칸이 열려요!")
