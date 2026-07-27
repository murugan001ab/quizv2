import { forwardRef, useImperativeHandle, useRef } from "react";
import Editor from "@monaco-editor/react";

const LANGUAGE_LABELS = {
  python: "Python 3",
  python3: "Python 3",
};

// Snippets available to both the imperative API (used by the mobile extra-keys
// toolbar) and anything else that wants to programmatically insert code.
// `cursorOffset` is where the caret lands inside the inserted text (e.g. right
// between the parens of "print()").
export const SNIPPETS = {
  print: { text: "print()", cursorOffset: 6 },
};

const CodeEditor = forwardRef(function CodeEditor(
  { value, onChange, language = "python", height = "100%", readOnly = false, onFocus, onBlur },
  ref
) {
  const editorInstance = useRef(null);
  const monacoInstance = useRef(null);

  function handleEditorDidMount(editor, monaco) {
    editorInstance.current = editor;
    monacoInstance.current = monaco;
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC, () => {});
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {});
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {});
    // Lets the mobile extra-keys toolbar know when to show/hide itself —
    // it should only float above the keyboard while you're actually editing.
    editor.onDidFocusEditorText(() => onFocus?.());
    editor.onDidBlurEditorText(() => onBlur?.());
  }

  // Exposed so parents (e.g. the mobile "extra keys" toolbar, which stands in
  // for keyboard shortcuts a phone keyboard can't send — Tab, Ctrl+], etc.)
  // can drive the editor without needing to know about Monaco directly.
  useImperativeHandle(ref, () => ({
    focus() {
      editorInstance.current?.focus();
    },
    // Insert raw text at the current cursor position (replacing any
    // selection), then place the caret `cursorOffset` characters into the
    // inserted text if provided, otherwise right after it.
    insertText(text, cursorOffset) {
      const editor = editorInstance.current;
      const monaco = monacoInstance.current;
      if (!editor || !monaco) return;
      editor.focus();
      const selection = editor.getSelection();
      editor.executeEdits("toolbar", [{ range: selection, text, forceMoveMarkers: true }]);
      const start = selection.getStartPosition();
      const lines = text.split("\n");
      const offset = cursorOffset ?? text.length;
      // Walk `offset` characters through the inserted text to find the
      // resulting line/column, so multi-line snippets place the caret right.
      let remaining = offset;
      let line = start.lineNumber;
      let col = start.column;
      for (let i = 0; i < lines.length; i++) {
        const lineLen = lines[i].length;
        if (remaining <= lineLen) {
          line = start.lineNumber + i;
          col = (i === 0 ? start.column : 1) + remaining;
          break;
        }
        remaining -= lineLen + 1; // +1 for the newline
        line = start.lineNumber + i + 1;
        col = 1;
      }
      const pos = { lineNumber: line, column: col };
      editor.setPosition(pos);
      editor.revealPositionInCenterIfOutsideViewport(pos);
    },
    indent() {
      editorInstance.current?.focus();
      editorInstance.current?.trigger("toolbar", "tab", null);
    },
    outdent() {
      editorInstance.current?.focus();
      editorInstance.current?.trigger("toolbar", "outdent", null);
    },
    moveCursor(dx, dy) {
      const editor = editorInstance.current;
      if (!editor) return;
      editor.focus();
      const pos = editor.getPosition();
      editor.setPosition({ lineNumber: Math.max(1, pos.lineNumber + dy), column: Math.max(1, pos.column + dx) });
    },
    undo() {
      editorInstance.current?.focus();
      editorInstance.current?.trigger("toolbar", "undo", null);
    },
    redo() {
      editorInstance.current?.focus();
      editorInstance.current?.trigger("toolbar", "redo", null);
    },
  }));

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
});

export default CodeEditor;
