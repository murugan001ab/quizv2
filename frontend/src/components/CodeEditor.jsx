import Editor from "@monaco-editor/react";
import * as monaco from "@monaco-editor/react";
const LANGUAGE_LABELS = {
  python: "Python 3",
  python3: "Python 3",
};

export default function CodeEditor({
  value,
  onChange,
  language = "python",
  height = "100%",
  readOnly = false,
}) {



  

function handleEditorDidMount(editor, monaco) {
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC, () => {});
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {});
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {});
}

  return (
    <div className="glass rounded-3xl overflow-hidden flex flex-col h-full border border-white/10">
      {/* Fake window titlebar, matches the glass/space theme instead of a bare editor */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10 bg-white/[0.03] shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-400/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/70" />
        </div>
        <span className="text-xs font-medium text-white/40 tracking-wide">
          {LANGUAGE_LABELS[language] || language}
        </span>
        <span className="w-14" /> {/* balances the dots so the label stays centered */}
      </div>

      <div className="flex-1 min-h-0">
        <Editor
          height={height}
          language={language}
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange?.(v ?? "")}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 14,
            minimap: { enabled: false },
            readOnly,
            automaticLayout: true,
            scrollBeyondLastLine: false,
            tabSize: 4,
            wordWrap: "on",
            padding: { top: 14 },
            fontLigatures: true,
            contextmenu: false,
          }}
        />
      </div>
    </div>
  );
}
