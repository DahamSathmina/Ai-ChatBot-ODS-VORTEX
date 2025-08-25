
import { useEffect, useState } from "react";
import { ChevronDown, Cpu } from "lucide-react";
import clsx from "clsx";

export default function ModelSwitch({ model, onChange, compact=false }: { model: string; onChange: (m: string)=>void; compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [models, setModels] = useState<string[]>(["gemma3:270m", "llama3.2:1b"]);

  useEffect(() => {
    fetch("/api/models", { method: "POST" })
      .then(r => r.json())
      .then((data: any) => {
        // Normalize different possible response shapes into a string[] of model ids
        const tags: string[] = Array.isArray(data?.models)
          ? data.models
          : Array.isArray(data)
          ? data
          : typeof data?.models === "string"
          ? [data.models]
          : [];
        if (tags.length > 0) {
          setModels(tags);
        }
      })
      .catch(() => {});
  }, []);

  function Item({ id }: { id: string }) {
    return (
      <button
        onClick={() => { onChange(id); setOpen(false); }}
        className={clsx("w-full text-left px-3 py-2 rounded-xl hover:bg-white/10", id === model && "bg-white/10")}
      >
        {id}
      </button>
    );
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen(v=>!v)} className={clsx("flex items-center gap-2 px-3 py-2 rounded-2xl bg-white/5 hover:bg-white/10 w-full", compact && "px-2 py-1 rounded-xl")}>
        <Cpu size={18}/> <span className="truncate">{model}</span> <ChevronDown size={16} className="opacity-70 ml-auto"/>
      </button>
      {open && (
        <div className="absolute left-0 mt-2 w-64 bg-[var(--panel)] border border-white/10 rounded-2xl p-2 z-10">
          {models.map(m => <Item key={m} id={m} />)}
        </div>
      )}
    </div>
  );
}
