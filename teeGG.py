import streamlit as st
from ollama import chat
import re
st.title('DeEpSeEk-R1 💀')
if 'messages' not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(name=message['role']):
        if message['role'] == 'assistant':
            chain_matches = re.findall(r"<think>(.*?)</think>", message["content"], re.DOTALL)
            chain_text = "\n".join(chain_matches).strip()
            answer_text = re.sub(r"<think>.*?</think>", "", message["content"], flags=re.DOTALL).strip()
            if chain_text:
                with st.expander("Chain-of-Thought", expanded=False):
                    st.write(chain_text)
            st.write(answer_text)
        else:
            st.write(message["content"])
user_message = st.chat_input("Type here")
if user_message:
    st.session_state.messages.append({
        'role': 'user',
        'content': user_message
    })
    with st.chat_message(name='user'):
        st.write(user_message)
    with st.chat_message(name='assistant'):
        chain_placeholder = st.empty()
        chain_expander = None
        chain_expander_container = None
        answer_container = st.empty()
        full_response = ""
        try:
            stream = chat(
                model="deepseek-r1",
                messages=[{'role': 'user', 'content': user_message}],
                stream=True
            )
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    full_response += token
                    chain_matches = re.findall(r"<think>(.*?)</think>", full_response, re.DOTALL)
                    chain_text = "\n".join(chain_matches).strip()
                    answer_text = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()
                    if chain_text:
                        if chain_expander is None:
                            chain_expander = chain_placeholder.expander("Chain-of-Thought", expanded=True)
                            chain_expander_container = chain_expander.empty()
                        chain_expander_container.write(chain_text)
                    else:
                        if chain_expander is None:
                            #chain_placeholder.write("Bro answered without thinking at all. 💀")
                            pass
                    answer_container.write(answer_text + "▌")
            answer_container.write(answer_text)
        except Exception as e:
            answer_container.error(f"Error: {str(e)}")
            full_response = "Fuck something went wrong bro. 💀💀💀"
    st.session_state.messages.append({
        'role': 'assistant',
        'content': full_response
    })
