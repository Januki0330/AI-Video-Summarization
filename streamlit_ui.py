import streamlit as st
import os
from pydub import AudioSegment
import speech_recognition as sr
import yt_dlp
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Set page configuration for dark theme
st.set_page_config(page_title="Video Summarizer & Quiz Generator", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #333333;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #555555;
        color: #E0E0E0;
        border: 1px solid #777777;
        padding: 5px 15px;
    }
    .stButton>button:hover {
        background-color: #777777;
    }
    .stTextInput>div>input {
        background-color: #555555;
        color: #E0E0E0;
        border: 1px solid #777777;
    }
    .stRadio label {
        color: #E0E0E0;
    }
    .stExpander {
        background-color: #444444;
        color: #E0E0E0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'quiz' not in st.session_state:
    st.session_state.quiz = {"question": "", "options": [], "answer": ""}
if 'quiz_answer' not in st.session_state:
    st.session_state.quiz_answer = ""
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = ""

# Helper Functions
def download_youtube_audio(url, audio_output="youtube_audio.wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'temp_audio.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    audio = AudioSegment.from_file("temp_audio.wav")
    audio.export(audio_output, format="wav")
    os.remove("temp_audio.wav")
    return audio_output

def extract_audio_from_video(video_path, audio_output="output.wav"):
    st.write("Extracting audio...")
    if video_path.startswith("http://") or video_path.startswith("https://"):
        return download_youtube_audio(video_path, audio_output)
    else:
        with open(video_path, 'rb') as f:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
        audio = AudioSegment.from_file(tmp_path, format="mp4")
        audio.export(audio_output, format="wav")
        os.remove(tmp_path)
        return audio_output

def audio_to_text(audio_file):
    st.write("Transcribing audio...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError as e:
            return f"API request failed: {str(e)}"

def summarize_text(text, max_length=50, min_length=20, style="concise"):
    st.write("Loading summarizer model...")
    try:
        from transformers import pipeline
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    except Exception as e:
        return f"Failed to load summarizer: {str(e)}"
    st.write("Summarizing text...")
    if style == "detailed":
        max_length, min_length = 100, 50
    try:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Summarization failed: {str(e)}"

def generate_quiz(summary):
    st.write("Generating quiz...")
    sentences = summary.split(". ")
    if len(sentences) < 2:
        return {"question": "Summary too short for quiz.", "options": [], "answer": ""}
    question = f"What is the main idea of: '{sentences[0]}'?"
    options = [
        "A) " + sentences[0],
        "B) Something unrelated.",
        "C) Another wrong answer.",
        "D) None of the above."
    ]
    return {"question": question, "options": options, "answer": "A"}

def save_to_pdf():
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(pdf_file.name, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Video Transcript", styles['Heading1']))
    story.append(Paragraph(st.session_state.transcript, styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Summary", styles['Heading1']))
    story.append(Paragraph(st.session_state.summary, styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Quiz", styles['Heading1']))
    story.append(Paragraph(st.session_state.quiz["question"], styles['BodyText']))
    for opt in st.session_state.quiz["options"]:
        story.append(Paragraph(opt, styles['BodyText']))
    doc.build(story)
    with open(pdf_file.name, "rb") as f:
        btn = st.download_button(
            label="Download PDF",
            data=f,
            file_name="summary_quiz.pdf",
            mime="application/pdf"
        )
    os.unlink(pdf_file.name)

# UI Layout
st.title("Video Summarizer & Quiz Generator")

# Input Section
with st.expander("Input Settings", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload MP4 File", type=["mp4"])
        if uploaded_file:
            st.session_state.selected_video = uploaded_file.name
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.processed = False
    with col2:
        url = st.text_input("YouTube URL", key="url_input")
        if st.button("Use URL") and url:
            st.session_state.selected_video = url
            st.session_state.processed = False

    if st.session_state.selected_video:
        st.write(f"Selected: {st.session_state.selected_video}")
    else:
        st.write("No video selected")

    style = st.radio("Summary Style", ["concise", "detailed"], index=0, horizontal=True)
    if st.button("Process Video", disabled=not st.session_state.selected_video):
        with st.spinner("Processing..."):
            audio_file = extract_audio_from_video(st.session_state.selected_video)
            st.session_state.transcript = audio_to_text(audio_file)
            st.session_state.summary = summarize_text(st.session_state.transcript, style=style)
            st.session_state.quiz = generate_quiz(st.session_state.summary)
            st.session_state.quiz_answer = st.session_state.quiz["answer"]
            st.session_state.processed = True
            os.remove(audio_file)

    if st.button("Refresh"):
        st.session_state.selected_video = None
        st.session_state.processed = False
        st.session_state.transcript = ""
        st.session_state.summary = ""
        st.session_state.quiz = {"question": "", "options": [], "answer": ""}
        st.session_state.quiz_answer = ""
        st.session_state.user_answer = ""
        st.rerun()

# Output Sections
with st.expander("Results", expanded=True):
    st.subheader("Transcript")
    st.text_area("Transcript", st.session_state.transcript, height=200, key="transcript_area")

    st.subheader("Summary")
    st.text_area("Summary", st.session_state.summary, height=100, key="summary_area")

    st.subheader("Quiz")
    if st.session_state.processed and st.session_state.quiz["question"]:
        st.write(st.session_state.quiz["question"])
        st.session_state.user_answer = st.radio("Select an answer:", st.session_state.quiz["options"], key="quiz_options")
        if st.button("Check Answer"):
            if st.session_state.user_answer[0] == st.session_state.quiz_answer:
                st.success("Correct!")
            else:
                st.error(f"Wrong! Correct answer: {st.session_state.quiz_answer}")

    if st.session_state.processed:
        save_to_pdf()