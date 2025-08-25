
import { useEffect, useMemo, useRef, useState } from "react";
import { MessageCircle, Rocket, SendHorizontal, Settings, Trash2, Plus, Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";
import Chat from "./components/Chat";
import ModelSwitch from "./components/ModelSwitch";

export type Role = "system" | "user" | "assistant";
export interface Msg { role: Role; content: string; }

export default function App() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "system", content: "You are ODS Vortex AI Assistant. Respond concisely and helpfully." },
  ]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("gemma3:270m");
  const [dark, setDark] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  async function send() {
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    const next: Msg[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setIsStreaming(true);

    const res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: next, model }),
    });

    if (!res.body) {
      setIsStreaming(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let assistant: Msg = { role: "assistant", content: "" };
    setMessages(prev => [...prev, assistant]);

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      assistant = { ...assistant, content: assistant.content + chunk };
      setMessages(prev => {
        const copy = prev.slice();
        copy[copy.length - 1] = assistant;
        return copy;
      });
    }
    setIsStreaming(false);
  }

  function clearChat() {
    setMessages([{ role: "system", content: messages[0].content }]);
  }

  return (
    <div className="h-screen grid md:grid-cols-[280px_1fr]">
      <aside className="hidden md:flex flex-col bg-[var(--panel)]/80 backdrop-blur p-4 gap-4 border-r border-white/10">
        <div className="flex items-center gap-2 text-xl font-semibold">
          <Rocket /> ODS Vortex
        </div>
        <button onClick={clearChat} className="flex items-center gap-2 px-3 py-2 rounded-2xl bg-white/5 hover:bg-white/10">
          <Trash2 size={18}/> New chat
        </button>
        <div className="mt-auto grid gap-3">
          <ModelSwitch model={model} onChange={setModel} />
          <button onClick={() => setDark(v => !v)} className="flex items-center gap-2 px-3 py-2 rounded-2xl bg-white/5 hover:bg-white/10">
            {dark ? <Sun size={18}/> : <Moon size={18}/>} Theme
          </button>
          <a href="https://ollama.com/library" target="_blank" className="text-sm opacity-80 hover:opacity-100">Get more models</a>
        </div>
      </aside>

      <main className="flex flex-col h-full">
        <header className="md:hidden flex items-center justify-between p-3 border-b border-white/10 bg-[var(--panel)]/60">
          <div className="flex items-center gap-2">
            <Rocket /> <span className="font-semibold">ODS Vortex</span>
          </div>
          <div className="flex items-center gap-2">
            <ModelSwitch compact model={model} onChange={setModel} />
            <button onClick={() => setDark(v => !v)} className="p-2 rounded-xl bg-white/5">
              {dark ? <Sun size={18}/> : <Moon size={18}/>}
            </button>
          </div>
        </header>

        <Chat messages={messages} setMessages={setMessages} input={input} setInput={setInput} onSend={send} isStreaming={isStreaming} />
      </main>
    </div>
  );
}
