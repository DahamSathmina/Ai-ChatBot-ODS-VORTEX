import json
import threading
import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ---------------------- Config ----------------------
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "tinyllama"
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant. Keep answers short unless the user asks for detail."
)

# ---------------------- Chat Client ----------------------
class OllamaChatClient:
    def __init__(self, model=DEFAULT_MODEL, system_prompt=SYSTEM_PROMPT):
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]
        self._stop = False

    def reset(self, system_prompt=SYSTEM_PROMPT):
        self.messages = [{"role": "system", "content": system_prompt}]

    def stop(self):
        self._stop = True

    def send(self, user_text, stream=True):
        """Generator that yields assistant text chunks (streaming)."""
        self._stop = False
        self.messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": stream,
            "options": {"temperature": 0.6},
        }

        try:
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300) as r:
                r.raise_for_status()
                full_reply = []

                for raw_line in r.iter_lines():
                    if self._stop:
                        break
                    if not raw_line:
                        continue

                    # Ensure string (fix for bytes issue)
                    if isinstance(raw_line, bytes):
                        line = raw_line.decode("utf-8")
                    else:
                        line = raw_line

                    if line.startswith("data:"):
                        line = line[len("data:"):].strip()

                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg = chunk.get("message", {})
                    content_piece = msg.get("content", "")
                    if content_piece:
                        full_reply.append(content_piece)
                        yield content_piece

                    if chunk.get("done"):
                        assistant_text = "".join(full_reply).strip()
                        if assistant_text:
                            self.messages.append({"role": "assistant", "content": assistant_text})
                        break

                if self._stop and full_reply:
                    assistant_text = "".join(full_reply).strip()
                    self.messages.append({"role": "assistant", "content": assistant_text})

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Can't reach Ollama at http://localhost:11434. Is Ollama running?\n"
                "Open the Ollama app or run `ollama serve` in a terminal."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Ollama HTTP error: {e.response.status_code} {e.response.text[:200]}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

# ---------------------- UI ----------------------
class ChatUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TinyLlama Chat (Ollama)")
        self.geometry("820x640")
        self.minsize(720, 520)

        self.client = OllamaChatClient()

        self._build_widgets()
        self._bind_shortcuts()

    def _build_widgets(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        self.model_entry = ttk.Entry(top, textvariable=self.model_var, width=20)
        self.model_entry.pack(side=tk.LEFT, padx=(4, 12))

        ttk.Button(top, text="New Chat", command=self.on_new_chat).pack(side=tk.LEFT)
        ttk.Button(top, text="Save Chat", command=self.on_save_chat).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(top, text="Load Chat", command=self.on_load_chat).pack(side=tk.LEFT, padx=(6, 0))

        mid = ttk.Frame(self, padding=(8, 4, 8, 0))
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chat_text = tk.Text(mid, wrap="word", state="disabled", padx=8, pady=8)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(mid, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text["yscrollcommand"] = scrollbar.set

        bottom = ttk.Frame(self, padding=8)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(bottom, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus()

        self.send_btn = ttk.Button(bottom, text="Send (Enter)", command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.stop_btn = ttk.Button(bottom, text="Stop", command=self.on_stop, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 6))

        try:
            self.style = ttk.Style()
            if "vista" in self.style.theme_names():
                self.style.theme_use("vista")
        except Exception:
            pass

        self._insert_system_line("System prompt loaded. Say hi!")

    def _bind_shortcuts(self):
        self.bind("<Return>", self._enter_send)
        self.bind("<Shift-Return>", lambda e: None)
        self.bind("<Escape>", lambda e: self.on_stop())

    def _append_text(self, who, text):
        self.chat_text.configure(state="normal")
        self.chat_text.insert(tk.END, f"{who}: ", "bold")
        self.chat_text.insert(tk.END, text + "\n\n")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state="disabled")
        self.chat_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

    def _append_stream_piece(self, piece):
        self.chat_text.configure(state="normal")
        self.chat_text.insert(tk.END, piece)
        self.chat_text.see(tk.END)
        self.chat_text.configure(state="disabled")

    def _insert_system_line(self, text):
        self.chat_text.configure(state="normal")
        self.chat_text.insert(tk.END, f"💡 {text}\n\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see(tk.END)

    def set_busy(self, busy=True):
        self.send_btn.configure(state="disabled" if busy else "normal")
        self.stop_btn.configure(state="normal" if busy else "disabled")
        self.model_entry.configure(state="disabled" if busy else "normal")

    def on_new_chat(self):
        if not messagebox.askyesno("New Chat", "Start a new chat? Current history will be cleared."):
            return
        sys_text = self.client.messages[0]["content"] if self.client.messages else SYSTEM_PROMPT
        self.client.reset(system_prompt=sys_text)
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.configure(state="disabled")
        self._insert_system_line("New chat started.")

    def on_save_chat(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if not file:
            return
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump({"model": self.model_var.get(), "messages": self.client.messages}, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"Saved chat → {file}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def on_load_chat(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file:
            return
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.model_var.set(data.get("model", DEFAULT_MODEL))
            msgs = data.get("messages", [])
            if not msgs:
                raise ValueError("No messages found in file.")
            self.client.messages = msgs

            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.configure(state="disabled")
            for m in msgs:
                if m["role"] == "system":
                    self._insert_system_line(m["content"])
                elif m["role"] == "user":
                    self._append_text("You", m["content"])
                elif m["role"] == "assistant":
                    self._append_text("Assistant", m["content"])
            self.status_var.set(f"Loaded chat ← {file}")
        except Exception as e:
            messagebox.showerror("Load failed", str(e))

    def on_stop(self):
        self.client.stop()
        self.status_var.set("Stopping…")

    def _enter_send(self, event):
        if self.focus_get() == self.input_entry:
            self.on_send()
            return "break"

    def on_send(self):
        text = self.input_var.get().strip()
        if not text:
            return
        model = self.model_var.get().strip() or DEFAULT_MODEL
        self.client.model = model

        self._append_text("You", text)
        self.input_var.set("")
        self.set_busy(True)
        self.status_var.set(f"Thinking with {model}…")

        threading.Thread(target=self._stream_reply, args=(text,), daemon=True).start()

    def _stream_reply(self, user_text):
        start = time.time()
        try:
            first_chunk = True
            for piece in self.client.send(user_text, stream=True):
                if first_chunk:
                    self._append_text("Assistant", "")
                    first_chunk = False
                self._append_stream_piece(piece)
            self.status_var.set(f"Done in {time.time()-start:.1f}s")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error")
        finally:
            self.set_busy(False)

if __name__ == "__main__":
    app = ChatUI()
    app.mainloop()
