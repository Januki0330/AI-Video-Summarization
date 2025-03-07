# test_ui.py
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import test  # Import the renamed processing module

# UI Functions
def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if video_path:
        video_label.config(text=f"Selected: {video_path}")
        url_entry.delete(0, tk.END)  # Clear URL field if file is selected
        process_button.config(state="normal")
        global selected_video
        selected_video = video_path

def use_url():
    url = url_entry.get().strip()
    if url.startswith("http://") or url.startswith("https://"):
        video_label.config(text=f"Selected: {url}")
        process_button.config(state="normal")
        global selected_video
        selected_video = url
    else:
        video_label.config(text="Invalid URL! Please enter a valid YouTube link.")

def process_video_thread():
    progress.start()
    try:
        audio_file = test.extract_audio_from_video(selected_video)
        text = test.audio_to_text(audio_file)
        summary = test.summarize_text(text, style=style_var.get())
        quiz = test.generate_quiz(summary)

        # Update UI from thread
        transcript_text.delete(1.0, tk.END)
        transcript_text.insert(tk.END, text)
        summary_text.delete(1.0, tk.END)
        summary_text.insert(tk.END, summary)
        quiz_question.config(text=quiz["question"])
        quiz_var.set(None)
        global quiz_answer
        quiz_answer = quiz["answer"]
        for widget in quiz_frame.winfo_children()[1:]:  # Clear old options
            widget.destroy()
        for opt in quiz["options"]:
            rb = tk.Radiobutton(quiz_frame, text=opt, variable=quiz_var, value=opt[0], command=check_answer)
            rb.pack(anchor="w")
    except Exception as e:
        transcript_text.delete(1.0, tk.END)
        transcript_text.insert(tk.END, f"Error: {str(e)}")
        summary_text.delete(1.0, tk.END)
        quiz_question.config(text="")
        for widget in quiz_frame.winfo_children()[1:]:
            widget.destroy()
    finally:
        progress.stop()

def process_video():
    transcript_text.delete(1.0, tk.END)
    summary_text.delete(1.0, tk.END)
    for widget in quiz_frame.winfo_children()[1:]:
        widget.destroy()
    transcript_text.insert(tk.END, "Processing... Please wait.\n")
    threading.Thread(target=process_video_thread, daemon=True).start()

def check_answer():
    if quiz_var.get() == quiz_answer:
        quiz_question.config(text=quiz_question.cget("text") + "\nCorrect!")
    else:
        quiz_question.config(text=quiz_question.cget("text") + "\nWrong! Correct answer: " + quiz_answer)

def save_to_pdf():
    pdf_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if pdf_file:
        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, "Video Transcript")
        c.drawString(50, 735, transcript_text.get(1.0, tk.END)[:500])  # Limit length
        c.drawString(50, 700, "Summary")
        c.drawString(50, 685, summary_text.get(1.0, tk.END))
        c.drawString(50, 650, "Quiz")
        c.drawString(50, 635, quiz_question.cget("text"))
        for i, opt in enumerate(quiz_frame.winfo_children()[1:]):
            c.drawString(50, 620 - i*15, opt.cget("text"))
        c.save()
        transcript_text.insert(tk.END, "\nSaved to PDF!")

# Create the main window
window = tk.Tk()
window.title("Video Summarizer & Quiz Generator")
window.geometry("1000x1000")
window.configure(bg="#f0f0f0")

# Styling
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 10), padding=5)
style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")

# Video selection
tk.Label(window, text="Step 1: Select a Video or Enter YouTube URL").pack(pady=5)
select_button = ttk.Button(window, text="Browse Local File", command=select_video)
select_button.pack()

# URL entry
url_frame = tk.Frame(window, bg="#f0f0f0")
url_frame.pack(pady=5)
tk.Label(url_frame, text="YouTube URL:", bg="#f0f0f0").pack(side=tk.LEFT)
url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, padx=5)
url_button = ttk.Button(url_frame, text="Use URL", command=use_url)
url_button.pack(side=tk.LEFT)

video_label = tk.Label(window, text="No video selected", bg="#f0f0f0")
video_label.pack(pady=5)

# Summary style
tk.Label(window, text="Summary Style").pack()
style_var = tk.StringVar(value="concise")
style_menu = ttk.OptionMenu(window, style_var, "concise", "detailed")
style_menu.pack(pady=5)

# Process button
process_button = ttk.Button(window, text="Step 2: Process Video", command=process_video, state="disabled")
process_button.pack(pady=10)

# Progress bar
progress = ttk.Progressbar(window, length=300, mode="indeterminate")
progress.pack(pady=5)

# Output sections
tk.Label(window, text="Transcript").pack()
transcript_text = scrolledtext.ScrolledText(window, width=80, height=10)
transcript_text.pack(pady=5)

tk.Label(window, text="Summary").pack()
summary_text = scrolledtext.ScrolledText(window, width=80, height=5)
summary_text.pack(pady=5)

tk.Label(window, text="Quiz").pack()
quiz_frame = tk.Frame(window, bg="#f0f0f0")
quiz_frame.pack(pady=5)
quiz_question = tk.Label(quiz_frame, text="", wraplength=700, justify="left", bg="#f0f0f0")
quiz_question.pack()
quiz_var = tk.StringVar()
quiz_answer = ""

# Save button
save_button = ttk.Button(window, text="Save as PDF", command=save_to_pdf)
save_button.pack(pady=5)

# Store selected video path
selected_video = None

# Start the UI loop
window.mainloop()