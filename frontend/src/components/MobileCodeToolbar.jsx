import { useKeyboardOffset } from "../hooks/useKeyboardOffset"

// A Termux-style "extra keys" row for the code editor. Phone keyboards have
// no Tab/arrow/bracket-pair keys and no shortcut for common Python snippets,
// so this appears pinned directly above the on-screen keyboard — tracking it
// live via the visualViewport API — and disappears again once the keyboard
// closes, exactly like Termux's own extra-keys row.
//
// Split into two rows so nothing needs to be dropped: snippets/brackets on
// top, quotes/navigation/undo below.
const ROW_1 = [
 
  { label: "(", action: (ed) => ed.insertText("(") },
  { label: ")", action: (ed) => ed.insertText(")") },
  { label: "[", action: (ed) => ed.insertText("[") },
  { label: "]", action: (ed) => ed.insertText("]") },
  { label: "↑", action: (ed) => ed.moveCursor(0, -1) },
  { label: "{", action: (ed) => ed.insertText("{") },
  { label: "}", action: (ed) => ed.insertText("}") },
  { label: ":", action: (ed) => ed.insertText(":") },

]

const ROW_2 = [
  { label: "Tab", action: (ed) => ed.indent() },
    { label: "=", action: (ed) => ed.insertText("=") },
  { label: '"', action: (ed) => ed.insertText('""', 1) },
  { label: "←", action: (ed) => ed.moveCursor(-1, 0) },
  { label: "↓", action: (ed) => ed.moveCursor(0, 1) },
  { label: "→", action: (ed) => ed.moveCursor(1, 0) },
  { label: "↺", action: (ed) => ed.undo() },
  { label: "↻", action: (ed) => ed.redo() },
]

const KEYBOARD_THRESHOLD = 100

// Both rows are laid out as one CSS grid (row 1 fills first, row 2 flows
// into the second grid row automatically) so buttons line up in columns
// instead of each row packing to its own content width independently.
const COLS = Math.max(ROW_1.length, ROW_2.length)

function Key({ k, editorRef }) {
  if (!k) return <div />
  return (
    <button
      type="button"
      // onMouseDown/preventDefault so tapping a key doesn't blur (and
      // dismiss the on-screen keyboard for) the editor first.
      onMouseDown={(e) => e.preventDefault()}
      onClick={() => editorRef.current && k.action(editorRef.current)}
      className="h-9 rounded-xl bg-white/[0.05] border border-white/10 text-white/70 text-sm font-mono
                 active:bg-white/[0.12] active:scale-95 transition-all duration-100"
    >
      {k.label}
    </button>
  )
}

export default function MobileCodeToolbar({ editorRef }) {
  const keyboardOffset = useKeyboardOffset()

  // Only float above an actually-open on-screen keyboard — hide entirely
  // (no reserved space either, that's handled by the parent using
  // useKeyboardOpen) once it closes.
  if (keyboardOffset < KEYBOARD_THRESHOLD) return null

  // Pad the shorter row with blank cells so both rows share the same COLS
  // grid and every button still lines up under the one above/below it.
  const row1 = [...ROW_1, ...Array(COLS - ROW_1.length).fill(null)]
  const row2 = [...ROW_2, ...Array(COLS - ROW_2.length).fill(null)]

  return (
    <div
      className="lg:hidden fixed inset-x-0 z-50 glass border-t border-white/10 px-1 py-1.5 overflow-x-auto"
      style={{ bottom: keyboardOffset }}
    >
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${COLS}, minmax(2.75rem, 1fr))` }}
      >
        {row1.map((k, i) => <Key key={`r1-${i}`} k={k} editorRef={editorRef} />)}
        {row2.map((k, i) => <Key key={`r2-${i}`} k={k} editorRef={editorRef} />)}
      </div>
    </div>
  )
}
