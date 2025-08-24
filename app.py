import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import json

# ----------------- CONFIG -----------------
MODEL_URL = "http://localhost:11434/api/generate"  # Gemma3 API URL
MODEL_NAME = "gemma3:270m"

# ----------------- FUNCTIONS -----------------
def generate_response(user_input):
    payload = {
        "model": MODEL_NAME,
        "prompt": user_input,
        "max_tokens": 200
    }
    try:
        response = requests.post(MODEL_URL, json=payload)
        data = response.json()
        return data.get("output", "No response")
    except:
        return "Error connecting to AI model."

def send_message():
    user_text = user_entry.get()
    if user_text.strip() == "":
        return
    chat_area.insert(tk.END, "You: " + user_text + "\n")
    user_entry.delete(0, tk.END)
    
    # Generate AI response in separate thread
    def ai_thread():
        response = generate_response(user_text)
        chat_area.insert(tk.END, "Bot: " + response + "\n")
        chat_area.see(tk.END)
    
    threading.Thread(target=ai_thread).start()

# ----------------- GUI -----------------
root = tk.Tk()
root.title("AI Chatbot")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20)
chat_area.pack(padx=10, pady=10)

user_entry = tk.Entry(root, width=50)
user_entry.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
user_entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

root.mainloop()
