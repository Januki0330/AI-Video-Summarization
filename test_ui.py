import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
from queue import Queue
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import test  # Your processing module

# Queue for thread-safe GUI updates
update_queue = Queue()

# UI Functions
def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if video_path:
        video_label.config(text=f"Selected: {video_path}")
        url_entry.delete(0, tk.END)
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
        update_queue.put(("update", text, summary, quiz))
    except Exception as e:
        update_queue.put(("error", str(e)))
    finally:
        update_queue.put(("stop_progress",))

def process_video():
    transcript_text.delete(1.0, tk.END)
    summary_text.delete(1.0, tk.END)
    for widget in quiz_frame.winfo_children()[1:]:
        widget.destroy()
    transcript_text.insert(tk.END, "Processing... Please wait.\n")
    threading.Thread(target=process_video_thread, daemon=True).start()
    check_queue()

def check_answer():
    if quiz_question.winfo_exists() and quiz_var.get() == quiz_answer:
        quiz_question.config(text=quiz_question.cget("text") + "\nCorrect!")
    elif quiz_question.winfo_exists():
        quiz_question.config(text=quiz_question.cget("text") + "\nWrong! Correct answer: " + quiz_answer)
    update_scroll_region()

def save_to_pdf():
    pdf_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if pdf_file:
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("Video Transcript", styles['Heading1']))
        story.append(Paragraph(transcript_text.get(1.0, tk.END).strip(), styles['BodyText']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Summary", styles['Heading1']))
        story.append(Paragraph(summary_text.get(1.0, tk.END).strip(), styles['BodyText']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Quiz", styles['Heading1']))
        quiz_text = quiz_question.cget("text") if quiz_question.winfo_exists() else "No quiz available"
        story.append(Paragraph(quiz_text, styles['BodyText']))
        for child in quiz_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                story.append(Paragraph(child.cget("text"), styles['BodyText']))
        doc.build(story)
        transcript_text.insert(tk.END, "\nSaved to PDF!")
        update_scroll_region()

def refresh_ui():
    """Reset the UI to its initial state."""
    transcript_text.delete(1.0, tk.END)
    summary_text.delete(1.0, tk.END)
    for widget in quiz_frame.winfo_children()[1:]:
        widget.destroy()
    video_label.config(text="No video selected")
    url_entry.delete(0, tk.END)
    process_button.config(state="disabled")
    quiz_question.config(text="")
    update_scroll_region()

def update_ui_from_queue():
    while not update_queue.empty():
        action, *args = update_queue.get()
        if action == "update":
            text, summary, quiz = args
            transcript_text.delete(1.0, tk.END)
            transcript_text.insert(tk.END, text)
            summary_text.delete(1.0, tk.END)
            summary_text.insert(tk.END, summary)
            if quiz_question.winfo_exists():
                quiz_question.config(text=quiz["question"])
            quiz_var.set(None)
            global quiz_answer
            quiz_answer = quiz["answer"]
            for widget in quiz_frame.winfo_children()[1:]:
                widget.destroy()
            for opt in quiz["options"]:
                rb = tk.Radiobutton(quiz_frame, text=opt, variable=quiz_var, value=opt[0], command=check_answer, font=("Helvetica", 12), bg="#333333", fg="#E0E0E0", selectcolor="#555555")
                rb.pack(anchor="w")
            update_scroll_region()
        elif action == "error":
            error_msg = args[0]
            transcript_text.delete(1.0, tk.END)
            transcript_text.insert(tk.END, f"Error: {error_msg}")
            summary_text.delete(1.0, tk.END)
            if quiz_question.winfo_exists():
                quiz_question.config(text="")
            update_scroll_region()
        elif action == "stop_progress":
            progress.stop()

def check_queue():
    update_ui_from_queue()
    window.after(100, check_queue)

def update_scroll_region():
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Main Window Setup
window = tk.Tk()
window.title("Video Summarizer & Quiz Generator")
window.geometry("1000x600")
window.configure(bg="#333333")  # Dark background

main_frame = tk.Frame(window, bg="#333333")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg="#333333")
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

content_frame = tk.Frame(canvas, bg="#333333")
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Styling for dark theme
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Helvetica", 10), padding=5, background="#555555", foreground="#E0E0E0")
style.configure("TLabel", font=("Helvetica", 12), background="#333333", foreground="#E0E0E0")
style.configure("TProgressbar", background="#555555", troughcolor="#333333")

# Input Section
input_frame = tk.Frame(content_frame, bg="#333333", padx=10, pady=10, relief="groove", borderwidth=2)
input_frame.pack(fill="x", pady=5)
tk.Label(input_frame, text="Step 1: Select a Video or Enter YouTube URL", font=("Helvetica", 14, "bold"), bg="#333333", fg="#E0E0E0").pack(pady=5)
select_button = ttk.Button(input_frame, text="Browse Local File", command=select_video)
select_button.pack()
url_frame = tk.Frame(input_frame, bg="#333333")
url_frame.pack(pady=5)
tk.Label(url_frame, text="YouTube URL:", bg="#333333", fg="#E0E0E0").pack(side=tk.LEFT)
url_entry = tk.Entry(url_frame, width=50, font=("Helvetica", 12), bg="#555555", fg="#E0E0E0", insertbackground="#E0E0E0")
url_entry.pack(side=tk.LEFT, padx=5)
url_button = ttk.Button(url_frame, text="Use URL", command=use_url)
url_button.pack(side=tk.LEFT)
video_label = tk.Label(input_frame, text="No video selected", bg="#333333", fg="#E0E0E0", font=("Helvetica", 12))
video_label.pack(pady=5)
tk.Label(input_frame, text="Summary Style", font=("Helvetica", 14, "bold"), bg="#333333", fg="#E0E0E0").pack()
style_var = tk.StringVar(value="concise")
style_menu = ttk.OptionMenu(input_frame, style_var, "concise", "detailed")
style_menu.pack(pady=5)
process_button = ttk.Button(input_frame, text="Step 2: Process Video", command=process_video, state="disabled")
process_button.pack(pady=10)
progress = ttk.Progressbar(input_frame, length=300, mode="indeterminate")
progress.pack(pady=5)

# Refresh Button
refresh_button = ttk.Button(input_frame, text="Refresh", command=refresh_ui)
refresh_button.pack(pady=5)

# Output Sections
transcript_frame = tk.Frame(content_frame, bg="#333333", padx=10, pady=10, relief="groove", borderwidth=2)
transcript_frame.pack(fill="x", pady=5)
tk.Label(transcript_frame, text="Transcript", font=("Helvetica", 14, "bold"), bg="#333333", fg="#E0E0E0").pack()
transcript_text = scrolledtext.ScrolledText(transcript_frame, width=80, height=10, font=("Helvetica", 12), bg="#555555", fg="#E0E0E0", insertbackground="#E0E0E0")
transcript_text.pack(fill="x")

summary_frame = tk.Frame(content_frame, bg="#333333", padx=10, pady=10, relief="groove", borderwidth=2)
summary_frame.pack(fill="x", pady=5)
tk.Label(summary_frame, text="Summary", font=("Helvetica", 14, "bold"), bg="#333333", fg="#E0E0E0").pack()
summary_text = scrolledtext.ScrolledText(summary_frame, width=80, height=5, font=("Helvetica", 12), bg="#555555", fg="#E0E0E0", insertbackground="#E0E0E0")
summary_text.pack(fill="x")

quiz_frame = tk.Frame(content_frame, bg="#333333", padx=10, pady=10, relief="groove", borderwidth=2)
quiz_frame.pack(fill="x", pady=5)
tk.Label(quiz_frame, text="Quiz", font=("Helvetica", 14, "bold"), bg="#333333", fg="#E0E0E0").pack()
quiz_question = tk.Label(quiz_frame, text="", wraplength=700, justify="left", bg="#333333", fg="#E0E0E0", font=("Helvetica", 12))
quiz_question.pack()
quiz_var = tk.StringVar()
quiz_answer = ""

save_button = ttk.Button(content_frame, text="Save as PDF", command=save_to_pdf)
save_button.pack(pady=10)

selected_video = None
window.bind("<Configure>", lambda event: update_scroll_region())
update_scroll_region()
window.after(100, check_queue)
window.mainloop()