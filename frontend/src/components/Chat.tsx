
import { useEffect, useRef } from "react";
import type { Msg } from "../App";
import { marked } from "marked";
import { SendHorizontal } from "lucide-react";

export default function Chat({
  messages, setMessages, input, setInput, onSend, isStreaming
}: {
  messages: Msg[];
  setMessages: (fn: any) => void;
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  isStreaming: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 grid grid-rows-[1fr_auto]">
      <div className="overflow-auto px-4 md:px-8 py-6 space-y-6">
        {messages.filter(m => m.role !== "system").map((m, i) => (
          <div key={i} className="flex gap-3">
            <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-sm shrink-0">
              {m.role === "user" ? "You" : "AI"}
            </div>
            <div className="prose prose-invert max-w-3xl" dangerouslySetInnerHTML={{__html: marked.parse(m.content)}} />
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 md:p-6 bg-gradient-to-t from-black/40 to-transparent">
        <div className="mx-auto max-w-3xl">
          <div className="flex items-end gap-2 bg-white/5 border border-white/10 rounded-2xl p-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSend(); }}}
              placeholder="Ask anything…"
              rows={1}
              className="flex-1 bg-transparent outline-none resize-none p-3"
            />
            <button
              onClick={onSend}
              disabled={isStreaming}
              className="px-4 py-3 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-50"
              title="Send"
            >
              <SendHorizontal />
            </button>
          </div>
          <p className="text-xs text-white/60 mt-2">
            Models: gemma3:270m (default), llama3.2:1b (ultra-tiny). Streaming via FastAPI proxy.
          </p>
        </div>
      </div>
    </div>
  );
}
