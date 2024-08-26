import streamlit as st
import requests
import pyperclip
from gtts import gTTS
from io import BytesIO
import re
import cohere

# Initialize Cohere client
co = cohere.Client('evLatt2FuOBOJti8orWXbEoATx0NDUTGAkLcXRJO')

def summarize_response(text):
    # Check if text length is more than 250 characters
    if len(text) > 250:
        response = co.summarize(text=text, length='short')
        return response.summary
    else:
        return text  # Return the text as is if it's too short

def extract_key_points(text):
    # Refined key points extraction
    sentences = re.split(r'(?<!\b[A-Z])\.(?![A-Z]\b)', text)
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 10]  # Ensure points are long enough

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

api_url = "http://localhost:5001/query"

if 'response' not in st.session_state:
    st.session_state.response = ""
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
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
                # Preserve the full response
                st.session_state.full_response = ai_response

                # Summarize the response if it's long enough
                summarized_response = summarize_response(ai_response)
                st.session_state.response = summarized_response

                # Extract key points from the summarized response
                st.session_state.key_points = extract_key_points(summarized_response)
                
                st.session_state.history.append({
                    "query": query, 
                    "response": summarized_response
                })
                
                # Handle key points
                if not st.session_state.key_points:
                    st.session_state.key_points = extract_key_points(ai_response)  # Extract key points from full response
                
                if st.session_state.key_points:
                    st.session_state.key_points.pop()
        else:
            st.error("Failed to retrieve the response. Please try again.")

with button_col2:
    if st.session_state.response and st.button("Clear Response"):
        st.session_state.response = ""
        st.session_state.full_response = ""
        st.session_state.key_points = []

if st.session_state.response:
    st.markdown("### Key Points:")

    if st.session_state.key_points:
        # Show key points if they exist
        st.markdown("\n".join([f"- {point}" for point in st.session_state.key_points]))
    else:
        # No key points extracted, so show detailed response as key points
        st.markdown(f"- {st.session_state.full_response}")

    if st.button("Copy to Clipboard"):
        pyperclip.copy(st.session_state.response)
        st.success("Response copied to clipboard!")

    detailed_response = st.session_state.full_response
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
