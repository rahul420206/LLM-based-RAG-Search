import streamlit as st
import requests
import pyperclip
from gtts import gTTS
from io import BytesIO
import re

st.markdown("""
    <style>
    .css-1aumxhk {
        background-color: #f7f9fc !important;
        padding: 15px !important;
        width: 250px !important;
        border-right: 1px solid #ddd !important;
    }
    
    .history-block {
        background-color: #e9ecef;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 10px;
        padding: 10px;
    }

    .query-text {
        font-weight: bold;
        color: #333;
    }

    .response-text {
        color: #666;
        font-size: 12px;
    }

    .css-1aumxhk::-webkit-scrollbar {
        width: 8px;
    }
    .css-1aumxhk::-webkit-scrollbar-thumb {
        background-color: #888;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("LLM-based RAG Search")

# URL of the backend service
api_url = "https://your-backend-service.herokuapp.com/query"


if 'response' not in st.session_state:
    st.session_state.response = ""
if 'key_points' not in st.session_state:
    st.session_state.key_points = []
if 'history' not in st.session_state:
    st.session_state.history = []

st.sidebar.markdown("<h3 style='text-align: center;'>History</h3>", unsafe_allow_html=True)
for idx, entry in enumerate(st.session_state.history):
    query = entry['query']
    response_first_sentence = entry['response'].split('.')[0] + '.'
    with st.sidebar.expander(f"Query {idx + 1}"):
        st.sidebar.markdown(
            f"<div class='history-block'>"
            f"<p class='query-text'>{query}</p>"
            f"<p class='response-text'>{response_first_sentence}</p>"
            f"</div>", 
            unsafe_allow_html=True
        )

query = st.text_input("Enter your query:")

button_col1, button_col2 = st.columns([2, 1])

with button_col1:
    if st.button("Submit"):
        response = requests.post(api_url, json={"query": query})

        if response.status_code == 200:
            ai_response = response.json().get("answer", "")
            
            if len(ai_response.split()) < 5:
                st.error("Response is too short. Please try again.")
            else:
                st.session_state.response = ai_response

                st.session_state.history.append({
                    "query": query, 
                    "response": ai_response
                })

                key_points = re.split(r'(?<!\b[A-Z])\.(?![A-Z]\b)', ai_response)
                st.session_state.key_points = [point.strip() for point in key_points if point]
                
                if st.session_state.key_points:
                    st.session_state.key_points.pop()
        else:
            st.error("Failed to retrieve the response. Please try again.")

with button_col2:
    if st.session_state.response and st.button("Clear Response"):
        st.session_state.response = ""
        st.session_state.key_points = []

if st.session_state.response:
    st.markdown("### Key Points:")
    if st.session_state.key_points:
        st.markdown("\n".join([f"- {point}" for point in st.session_state.key_points]))
    else:
        st.write("No key points extracted.")

    if st.button("Copy to Clipboard"):
        pyperclip.copy(st.session_state.response)
        st.success("Response copied to clipboard!")

    detailed_response = st.session_state.response
    if not detailed_response.endswith('.'):
        detailed_response += '.'
    with st.expander("View Detailed Response"):
        st.markdown(detailed_response)

    if st.button("Convert to Speech"):
        tts = gTTS(text=st.session_state.response, lang='en')
        speech_file = BytesIO()
        tts.write_to_fp(speech_file)
        speech_file.seek(0)
        st.audio(speech_file, format='audio/mp3')

st.markdown("<p style='text-align: center;'>Developed by Rahul</p>", unsafe_allow_html=True)
