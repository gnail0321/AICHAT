import streamlit as st
from ollama import chat
import re

st.title('DeEpSeEk-R1 💀')

if 'messages' not in st.session_state:
    st.session_state.messages = []

########################################
# 1. DISPLAY PREVIOUS MESSAGES
########################################
for message in st.session_state.messages:
    with st.chat_message(name=message['role']):
        # Only parse chain-of-thought if it's an assistant message
        if message['role'] == 'assistant':
            # Find all chain-of-thought segments
            chain_matches = re.findall(r"<think>(.*?)</think>", message["content"], re.DOTALL)
            chain_text = "\n".join(chain_matches).strip()

            # Remove the chain-of-thought text from the displayed answer
            answer_text = re.sub(r"<think>.*?</think>", "", message["content"], flags=re.DOTALL).strip()

            # If chain-of-thought text is present, show it in an expander
            if chain_text:
                with st.expander("Chain-of-Thought", expanded=False):
                    st.write(chain_text)
            # Display the remaining answer
            st.write(answer_text)
        else:
            # User messages or system messages shown as is
            st.write(message["content"])

########################################
# 2. PROCESS NEW USER MESSAGE
########################################
user_message = st.chat_input("Type here")
if user_message:
    # Store user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_message
    })

    # Display user message in the chat
    with st.chat_message(name='user'):
        st.write(user_message)

    # Display assistant response (streaming)
    with st.chat_message(name='assistant'):
        # Placeholders for chain-of-thought and answer
        chain_placeholder = st.empty()
        chain_expander = None
        chain_expander_container = None

        answer_container = st.empty()
        full_response = ""

        try:
            # Stream the assistant's response
            stream = chat(
                model="deepseek-r1",
                messages=[{'role': 'user', 'content': user_message}],
                stream=True
            )
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    full_response += token

                    # Extract chain-of-thought text so far
                    chain_matches = re.findall(r"<think>(.*?)</think>", full_response, re.DOTALL)
                    chain_text = "\n".join(chain_matches).strip()

                    # Remove chain-of-thought segments for the displayed answer
                    answer_text = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()

                    # Update chain-of-thought display
                    if chain_text:
                        if chain_expander is None:
                            chain_expander = chain_placeholder.expander("Chain-of-Thought", expanded=True)
                            chain_expander_container = chain_expander.empty()
                        chain_expander_container.write(chain_text)
                    else:
                        if chain_expander is None:
                            #chain_placeholder.write("No chain-of-thought provided.")
                            pass

                    # Update the answer container live (with the blinking cursor)
                    answer_container.write(answer_text + "▌")
            answer_container.write(answer_text)

        except Exception as e:
            answer_container.error(f"Error: {str(e)}")
            full_response = "Sorry, something went wrong."

    # Store the assistant's final response (including chain-of-thought) in session
    st.session_state.messages.append({
        'role': 'assistant',
        'content': full_response
    })
