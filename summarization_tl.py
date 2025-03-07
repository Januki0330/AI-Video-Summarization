{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "d:\\pojects python\\conda_envs\\summ_tl\\Lib\\site-packages\\tqdm\\auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html\n",
      "  from .autonotebook import tqdm as notebook_tqdm\n"
     ]
    }
   ],
   "source": [
    "# video_processing.py\n",
    "from pydub import AudioSegment\n",
    "import speech_recognition as sr\n",
    "from transformers import pipeline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def extract_audio_from_video(video_path, audio_output=\"output.wav\"):\n",
    "    \"\"\"Extract audio from a video file and save as WAV.\"\"\"\n",
    "    audio = AudioSegment.from_file(video_path, format=\"mp4\")\n",
    "    audio.export(audio_output, format=\"wav\")\n",
    "    return audio_output\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def audio_to_text(audio_file):\n",
    "    \"\"\"Convert audio file to text using Google's API.\"\"\"\n",
    "    recognizer = sr.Recognizer()\n",
    "    with sr.AudioFile(audio_file) as source:\n",
    "        audio_data = recognizer.record(source)\n",
    "        try:\n",
    "            text = recognizer.recognize_google(audio_data)\n",
    "            return text\n",
    "        except sr.UnknownValueError:\n",
    "            return \"Could not understand audio.\"\n",
    "        except sr.RequestError:\n",
    "            return \"API request failed.\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "def summarize_text(text):\n",
    "    \"\"\"Summarize text using a pre-trained model.\"\"\"\n",
    "    summarizer = pipeline(\"summarization\", model=\"facebook/bart-large-cnn\")\n",
    "    summary = summarizer(text, max_length=50, min_length=20, do_sample=False)\n",
    "    return summary[0][\"summary_text\"]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "def generate_quiz(summary):\n",
    "    \"\"\"Generate a quiz from the summary.\"\"\"\n",
    "    sentences = summary.split(\". \")\n",
    "    if len(sentences) < 2:\n",
    "        return \"Summary too short for quiz.\"\n",
    "    question = f\"What is the main idea of: '{sentences[0]}'?\"\n",
    "    options = [\n",
    "        \"A) \" + sentences[0],\n",
    "        \"B) Something unrelated.\",\n",
    "        \"C) Another wrong answer.\",\n",
    "        \"D) None of the above.\"\n",
    "    ]\n",
    "    return {\"question\": question, \"options\": options, \"answer\": \"A\"}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Device set to use cpu\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Text: computers are all around us from laptop computers to smartphone to smart watches that changing the way that we live our lives but have you ever ask yourself what exactly is a computer a computer is an electronic device the manipulates information or data the computer as once in zeros for the nose how to combine them into much more Complex things such as a photo movie website gain and much more computers use a combination of hardware and software hardware is any physical part of the computer which includes the internal components in the external parts like the monitor in keyboard software is any set of instructions that tells the hardware what to do web browser media player or word processor when most people say computer they are talking about a personal computer or laptop which has basically the same capabilities few different styles most common type uses the Windows operating system maths computers feature the Mac OS operating system for chromebooks run on Chrome OS Smartphones and other mobile devices mostly used the iOS or Android operating systems will talk more about operating system in many other Shapes and sizes TVS game controls and even appliances like refrigerator for laptops on a network in fact every time you use the internet are also used in many offices to store in share files as you can see there are many types of computers are there in each one place a part in our modern world creating opportunities for a better life\n",
      "Summary: A computer is an electronic device that manipulates information or data. Most common type uses the Windows operating system for computers. Smartphones and other mobile devices mostly used the iOS or Android operating systems. TVS game controls and even appliances like\n",
      "Quiz: {'question': \"What is the main idea of: 'A computer is an electronic device that manipulates information or data'?\", 'options': ['A) A computer is an electronic device that manipulates information or data', 'B) Something unrelated.', 'C) Another wrong answer.', 'D) None of the above.'], 'answer': 'A'}\n"
     ]
    }
   ],
   "source": [
    "\n",
    "# Optional: Test the module standalone\n",
    "if __name__ == \"__main__\":\n",
    "    video_path = \"Computer Basics_ What Is a Computer_.mp4\"\n",
    "    audio_file = extract_audio_from_video(video_path)\n",
    "    text = audio_to_text(audio_file)\n",
    "    summary = summarize_text(text)\n",
    "    quiz = generate_quiz(summary)\n",
    "    print(\"Text:\", text)\n",
    "    print(\"Summary:\", summary)\n",
    "    print(\"Quiz:\", quiz)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
