import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ChatMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import load_prompt
import glob

# prompt-maker 
# https://smith.langchain.com/hub/hardkothari/prompt-maker?organizationId=88007055-284e-585d-8633-daa8efb5ee48


st.set_page_config(page_title="나만의 ChatGPT 💬", page_icon="💬")
st.title("나만의 ChatGPT 💬")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 사이드바 생성 
with st.sidebar:
    clear_btn = st.button("대화내용 초기화")
    prompt_files = glob.glob("prompts/*.yaml")
    selected_prompt = st.selectbox("프롬프트를 선택해 주세요.", prompt_files, index=0)
    task_input = st.text_input("Task 입력 예시: 블로그 글 작성", "")


def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)

def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


# 체인을 생성합니다.
def create_chain(prompt_file_path, task=""):
    prompt = load_prompt(prompt_file_path, encoding="utf-8")
    
    if task:
        prompt = prompt.partial(task=task)
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    chain = prompt | llm | StrOutputParser()
    return chain


# 초기화 버튼 
if clear_btn:
    retriever = st.session_state["messages"].clear()

# 이전 대화 기록 출력 
print_messages()

# 경고 메시지를 띄우기 위한 빈 영역
warning_msg = st.empty()

# 만약 사용자 입력이 들어오면 
if user_input := st.chat_input():
    # 사용자 입력 
    st.chat_message("user").write(user_input)
    chain = create_chain(selected_prompt, task=task_input)    
    
    # 스트리밍 호출 
    try:
        response = chain.stream({"question": user_input})
        with st.chat_message("assistant"):
            container = st.empty()
            
            ai_answer = ""
            for token in response:
                ai_answer += token
                container.markdown(ai_answer)
    except:
        warning_msg.error("왼쪽 사이드바에서 Task를 입력해주세요")
 

    # 대화 기록을 저장한다.
    add_message("user", user_input)
    add_message("assistant", ai_answer)
    
