# Modern Katakana → Romaji GUI (romkan2 + tkinter)

import tkinter as tk
from tkinter import filedialog, messagebox
from romkan2 import to_hepburn
from deep_translator import GoogleTranslator
translation_job = None
import re
from jaconv import kata2hira

def contains_japanese(text):
    return re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', text) is not None

# ---------- THEMES ----------
DARK = {
    "bg": "#0f172a",
    "card": "#111827",
    "text": "#e5e7eb",
    "muted": "#9ca3af",
    "accent": "#818cf8",
    "entry": "#1f2933",
    "border": "#374151"
}

LIGHT = {
    "bg": "#f3f4f6",
    "card": "#ffffff",
    "text": "#111827",
    "muted": "#6b7280",
    "accent": "#6366f1",
    "entry": "#f9fafb",
    "border": "#e5e7eb"
}

theme = DARK

def do_translation(text):
    # if user has cleared the box since this was scheduled, do nothing
    current_text = input_box.get("1.0", tk.END).strip()
    if not current_text:
        english_var.set("")
        return

    english = translate_to_english_live(text)
    english_var.set(english)

# ---------- FUNCTIONS ----------
def apply_theme():
    root.configure(bg=theme["bg"])
    card.configure(bg=theme["card"], highlightbackground=theme["border"])

    english_entry.configure(bg=theme["entry"], fg=theme["text"])

    title.configure(bg=theme["card"], fg=theme["text"])
    subtitle.configure(bg=theme["card"], fg=theme["muted"])
    footer.configure(bg=theme["bg"], fg=theme["muted"])

    input_box.configure(bg=theme["entry"], fg=theme["text"], insertbackground=theme["text"])
    output_entry.configure(bg=theme["entry"], fg=theme["text"])

    btn_frame.configure(bg=theme["card"])

    # style buttons safely
    for btn in [btn_copy, btn_clear, btn_save, btn_theme]:
        btn.configure(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent"],
            activeforeground="white"
        )

def toggle_theme():
    global theme
    theme = DARK if theme == LIGHT else LIGHT
    apply_theme()

translation_job = None

def convert_live(event=None):
    global translation_job

    text = input_box.get("1.0", tk.END).strip()

    if not text:
        output_var.set("")
        english_var.set("")
        return

    # Romaji conversion
    try:
        romaji = to_hepburn(text)
        output_var.set(romaji)
    except Exception:
        output_var.set("")

    # cancel previous scheduled translation
    if translation_job is not None:
        root.after_cancel(translation_job)

    # schedule translation after user stops typing
    translation_job = root.after(500, lambda: do_translation(text))




def translate_to_english_live(japanese_text):
    if not japanese_text.strip():
        return ""

    try:
        result = GoogleTranslator(source='ja', target='en').translate(japanese_text)
        hira = kata2hira(japanese_text)
        result = GoogleTranslator(source='ja', target='en').translate(hira)

        # If still Japanese, try again using romaji as fallback
        if contains_japanese(result):
            romaji = to_hepburn(japanese_text)
            result = GoogleTranslator(source='auto', target='en').translate(romaji)

        return result

    except Exception as e:
        print("Translation error:", e)
        return ""

def copy_text():
    root.clipboard_clear()
    root.clipboard_append(output_var.get())

def clear_all():
    global translation_job

    input_box.delete("1.0", tk.END)
    output_var.set("")
    english_var.set("")   # ← add this line

    # cancel any pending translation so it doesn't re-fill
    if translation_job is not None:
        root.after_cancel(translation_job)
        translation_job = None

def save_as_txt():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Save translation"
    )

    if file_path:
        original = input_box.get("1.0", tk.END).strip()
        romaji = output_var.get()
        english = english_var.get()

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Japanese:\n")
            f.write(original + "\n\n")

            f.write("Romaji:\n")
            f.write(romaji + "\n\n")

            f.write("English:\n")
            f.write(english + "\n")
# ---------- WINDOW ----------
root = tk.Tk()
root.title("Katakana → Romaji Converter")
root.geometry("620x480")
root.resizable(False, False)

# ---------- CARD ----------
card = tk.Frame(root, bd=0, highlightthickness=1)
card.pack(padx=20, pady=20, fill="both", expand=True)

# ---------- HEADER ----------
title = tk.Label(card, text="Katakana → Romaji", font=("Segoe UI", 18, "bold"))
title.pack(anchor="w", padx=20, pady=(20, 0))

subtitle = tk.Label(card, text="just add your katakana and get some Romaji :)",
                    font=("Segoe UI", 10))
subtitle.pack(anchor="w", padx=20, pady=(0, 10))

# ---------- INPUT ----------
input_box = tk.Text(card, height=6, font=("Segoe UI", 12), bd=0)
input_box.pack(fill="x", padx=20, pady=(0, 10))
input_box.bind("<KeyRelease>", convert_live)

# ---------- OUTPUT ----------
output_var = tk.StringVar()
output_entry = tk.Entry(card, textvariable=output_var, font=("Segoe UI", 12), bd=0)
output_entry.pack(fill="x", padx=20, pady=(0, 15))

# ---------- BUTTONS ----------
btn_frame = tk.Frame(card)
btn_frame.pack(padx=20, pady=10, fill="x")

def make_btn(text, cmd):
    return tk.Button(btn_frame, text=text, command=cmd,
                     relief="flat", font=("Segoe UI", 10, "bold"),
                     padx=10, pady=6)

btn_copy = make_btn("Copy", copy_text)
btn_copy.pack(side="left", padx=5)

btn_clear = make_btn("Clear", clear_all)
btn_clear.pack(side="left", padx=5)

btn_save = make_btn("Save .txt", save_as_txt)
btn_save.pack(side="left", padx=5)

english_var = tk.StringVar()
english_entry = tk.Entry(card, textvariable=english_var, font=("Segoe UI", 12), bd=0)
english_entry.pack(fill="x", padx=20, pady=(0, 15))

btn_theme = make_btn("Toggle Theme", toggle_theme)
btn_theme.pack(side="right", padx=5)

# ---------- FOOTER ----------
footer = tk.Label(root, text="Hope this helps • Powered by AI and Debug",
                  font=("Segoe UI", 9))
footer.pack(pady=(0, 10))

# apply theme once everything exists
apply_theme()

# run
root.mainloop()