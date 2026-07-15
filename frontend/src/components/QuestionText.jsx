/**
 * QuestionText — renders structured question text properly.
 *
 * Handles:
 *   • \n line breaks → real line breaks
 *   • கூற்று (A) / காரணம் (R)  — Assertion-Reason blocks
 *   • பொருத்துக / Match-the-following — two-column table
 *   • I. II. III. / numbered list items
 *   • Plain paragraph text
 */

const ASSERTION_RE = /கூற்று\s*\(A\)|காரணம்\s*\(R\)/
const MATCH_RE = /பொருத்துக|Match the following/i
const ROMAN_LINE_RE = /^(I{1,3}V?|VI{0,3}|IX|IV|V?I{0,3})\.\s/  // I. II. III. IV. etc.
const ALPHA_LIST_RE = /^\([a-d]\)\s/i   // (a) (b) (c) (d)
const NUMBER_COL_RE = /^\d+\.\s/        // 1. 2. 3. 4.

function isRomanLine(s) { return ROMAN_LINE_RE.test(s.trim()) }
function isAlphaLine(s) { return ALPHA_LIST_RE.test(s.trim()) }
function isNumberLine(s) { return NUMBER_COL_RE.test(s.trim()) }

// Split raw text on \n, trim each line, drop empties
function splitLines(text) {
  return text.split('\n').map(l => l.trim()).filter(Boolean)
}

// ── Assertion-Reason renderer ─────────────────────────────
function AssertionReason({ lines }) {
  return (
    <div className="flex flex-col gap-2">
      {lines.map((line, i) => {
        const isA = /கூற்று\s*\(A\)/i.test(line)
        const isR = /காரணம்\s*\(R\)/i.test(line)
        if (isA || isR) {
          const [label, ...rest] = line.split(':')
          const body = rest.join(':').trim()
          return (
            <div
              key={i}
              className={`flex gap-2.5 rounded-lg px-3 py-2 border
                ${isA
                  ? 'bg-accent-400/[0.07] border-accent-400/20'
                  : 'bg-glow-violet/[0.07] border-glow-violet/20'}`}
            >
              <span className={`font-bold text-sm shrink-0 pt-px ${isA ? 'text-accent-300' : 'text-glow-violet'}`}>
                {label.trim()}:
              </span>
              <span className="leading-relaxed text-white/90">{body}</span>
            </div>
          )
        }
        // trailing instruction line
        return (
          <p key={i} className="text-white/60 text-sm mt-1 leading-relaxed">
            {line}
          </p>
        )
      })}
    </div>
  )
}

// ── Match-the-following renderer ──────────────────────────
function MatchTable({ lines }) {
  // Separate header, left-col lines (a)(b)(c)(d), right-col (1)(2)(3)(4), instruction
  const header = []
  const leftCol = []
  const rightCol = []
  const footer = []

  let phase = 'header'
  for (const line of lines) {
    if (MATCH_RE.test(line) && phase === 'header') { header.push(line); continue }
    if (isAlphaLine(line)) { phase = 'left'; leftCol.push(line); continue }
    if (isNumberLine(line)) { phase = 'right'; rightCol.push(line); continue }
    if (phase === 'header') header.push(line)
    else footer.push(line)
  }

  return (
    <div className="flex flex-col gap-2">
      {header.map((h, i) => (
        <p key={i} className="font-semibold text-white/90 leading-relaxed">{h}</p>
      ))}
      {(leftCol.length > 0 || rightCol.length > 0) && (
        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 p-3 bg-white/[0.04] border border-white/10 rounded-xl">
          <div className="text-xs font-bold text-white/40 uppercase tracking-wide pb-1 border-b border-white/10">Column A</div>
          <div className="text-xs font-bold text-white/40 uppercase tracking-wide pb-1 border-b border-white/10">Column B</div>
          {Array.from({ length: Math.max(leftCol.length, rightCol.length) }).map((_, i) => (
            <>
              <div key={`l${i}`} className="text-sm text-white/90 leading-normal py-0.5">{leftCol[i] || ''}</div>
              <div key={`r${i}`} className="text-sm text-white/90 leading-normal py-0.5">{rightCol[i] || ''}</div>
            </>
          ))}
        </div>
      )}
      {footer.map((f, i) => (
        <p key={i} className="text-white/60 text-sm leading-relaxed">{f}</p>
      ))}
    </div>
  )
}

// ── Roman-numeral list renderer ───────────────────────────
function RomanList({ lines }) {
  const header = []
  const items = []
  const footer = []
  let phase = 'header'

  for (const line of lines) {
    if (isRomanLine(line)) { phase = 'items'; items.push(line); continue }
    if (phase === 'header') header.push(line)
    else footer.push(line)
  }

  return (
    <div className="flex flex-col gap-1.5">
      {header.map((h, i) => (
        <p key={i} className="font-medium text-white/90 leading-loose">{h}</p>
      ))}
      <div className="flex flex-col gap-1 px-3.5 py-2.5 bg-white/[0.04] border border-white/10 rounded-xl mt-1">
        {items.map((item, i) => (
          <div key={i} className="flex gap-2 text-sm leading-relaxed text-white/90">
            <span className="font-bold text-accent-400 min-w-[28px] shrink-0">
              {item.match(/^[IVX]+\./)?.[0]}
            </span>
            <span>{item.replace(/^[IVX]+\.\s*/, '')}</span>
          </div>
        ))}
      </div>
      {footer.map((f, i) => (
        <p key={i} className="text-white/60 text-sm leading-relaxed">{f}</p>
      ))}
    </div>
  )
}

// ── Main export ───────────────────────────────────────────
export default function QuestionText({ text, className = '' }) {
  if (!text) return null
  const lines = splitLines(text)

  // Detect format
  const hasAssertion = lines.some(l => ASSERTION_RE.test(l))
  const hasMatch = lines.some(l => MATCH_RE.test(l))
  const hasRoman = lines.some(l => isRomanLine(l))

  if (hasAssertion) return <div className={className}><AssertionReason lines={lines} /></div>
  if (hasMatch)     return <div className={className}><MatchTable lines={lines} /></div>
  if (hasRoman)     return <div className={className}><RomanList lines={lines} /></div>

  // Plain — just render with proper line breaks
  return (
    <div className={`leading-relaxed font-medium text-white/90 ${className}`}>
      {lines.map((line, i) => (
        <p key={i} className={i > 0 ? 'mt-1.5' : ''}>{line}</p>
      ))}
    </div>
  )
}
