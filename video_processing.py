# %%
# video_processing.py
from pydub import AudioSegment
import speech_recognition as sr
from transformers import pipeline

# %%
def extract_audio_from_video(video_path, audio_output="output.wav"):
    """Extract audio from a video file and save as WAV."""
    audio = AudioSegment.from_file(video_path, format="mp4")
    audio.export(audio_output, format="wav")
    return audio_output

# %%
def audio_to_text(audio_file):
    """Convert audio file to text using Google's API."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "API request failed."

# %%
def summarize_text(text):
    """Summarize text using a pre-trained model."""
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=50, min_length=20, do_sample=False)
    return summary[0]["summary_text"]

# %%
def generate_quiz(summary):
    """Generate a quiz from the summary."""
    sentences = summary.split(". ")
    if len(sentences) < 2:
        return "Summary too short for quiz."
    question = f"What is the main idea of: '{sentences[0]}'?"
    options = [
        "A) " + sentences[0],
        "B) Something unrelated.",
        "C) Another wrong answer.",
        "D) None of the above."
    ]
    return {"question": question, "options": options, "answer": "A"}

# %%
# Optional: Test the module standalone
if __name__ == "__main__":
    video_path = "Computer Basics_ What Is a Computer_.mp4"
    audio_file = extract_audio_from_video(video_path)
    text = audio_to_text(audio_file)
    summary = summarize_text(text)
    quiz = generate_quiz(summary)
    print("Text:", text)
    print("Summary:", summary)
    print("Quiz:", quiz)



# %%
