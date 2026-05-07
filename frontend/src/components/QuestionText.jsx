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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {lines.map((line, i) => {
        const isA = /கூற்று\s*\(A\)/i.test(line)
        const isR = /காரணம்\s*\(R\)/i.test(line)
        if (isA || isR) {
          const [label, ...rest] = line.split(':')
          const body = rest.join(':').trim()
          return (
            <div key={i} style={{
              display: 'flex', gap: '0.625rem',
              padding: '0.5rem 0.75rem',
              background: isA ? 'rgba(96,165,250,0.07)' : 'rgba(167,139,250,0.07)',
              border: `1px solid ${isA ? 'rgba(96,165,250,0.2)' : 'rgba(167,139,250,0.2)'}`,
              borderRadius: 6,
            }}>
              <span style={{
                fontWeight: 700, fontSize: '0.8rem', flexShrink: 0,
                color: isA ? 'var(--blue)' : 'var(--purple, #a78bfa)',
                paddingTop: '0.1rem',
              }}>{label.trim()}:</span>
              <span style={{ lineHeight: 1.6, color: 'var(--text)' }}>{body}</span>
            </div>
          )
        }
        // trailing instruction line
        return (
          <p key={i} style={{ color: 'var(--text2)', fontSize: '0.9rem', marginTop: '0.25rem', lineHeight: 1.6 }}>
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {header.map((h, i) => (
        <p key={i} style={{ fontWeight: 600, color: 'var(--text)', lineHeight: 1.6 }}>{h}</p>
      ))}
      {(leftCol.length > 0 || rightCol.length > 0) && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '0.375rem 1.5rem',
          padding: '0.75rem',
          background: 'var(--bg3)',
          border: '1px solid var(--border)',
          borderRadius: 8,
        }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.06em', paddingBottom: '0.25rem', borderBottom: '1px solid var(--border)' }}>Column A</div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.06em', paddingBottom: '0.25rem', borderBottom: '1px solid var(--border)' }}>Column B</div>
          {Array.from({ length: Math.max(leftCol.length, rightCol.length) }).map((_, i) => (
            <>
              <div key={`l${i}`} style={{ fontSize: '0.875rem', color: 'var(--text)', lineHeight: 1.5, padding: '0.2rem 0' }}>{leftCol[i] || ''}</div>
              <div key={`r${i}`} style={{ fontSize: '0.875rem', color: 'var(--text)', lineHeight: 1.5, padding: '0.2rem 0' }}>{rightCol[i] || ''}</div>
            </>
          ))}
        </div>
      )}
      {footer.map((f, i) => (
        <p key={i} style={{ color: 'var(--text2)', fontSize: '0.9rem', lineHeight: 1.6 }}>{f}</p>
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
      {header.map((h, i) => (
        <p key={i} style={{ fontWeight: 500, color: 'var(--text)', lineHeight: 1.7 }}>{h}</p>
      ))}
      <div style={{
        display: 'flex', flexDirection: 'column', gap: '0.25rem',
        padding: '0.625rem 0.875rem',
        background: 'var(--bg3)', border: '1px solid var(--border)',
        borderRadius: 8, marginTop: '0.25rem',
      }}>
        {items.map((item, i) => (
          <div key={i} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text)' }}>
            <span style={{ fontWeight: 700, color: 'var(--accent)', minWidth: 28, flexShrink: 0 }}>
              {item.match(/^[IVX]+\./)?.[0]}
            </span>
            <span>{item.replace(/^[IVX]+\.\s*/, '')}</span>
          </div>
        ))}
      </div>
      {footer.map((f, i) => (
        <p key={i} style={{ color: 'var(--text2)', fontSize: '0.9rem', lineHeight: 1.6 }}>{f}</p>
      ))}
    </div>
  )
}

// ── Main export ───────────────────────────────────────────
export default function QuestionText({ text, style = {} }) {
  if (!text) return null
  const lines = splitLines(text)

  // Detect format
  const hasAssertion = lines.some(l => ASSERTION_RE.test(l))
  const hasMatch = lines.some(l => MATCH_RE.test(l))
  const hasRoman = lines.some(l => isRomanLine(l))

  if (hasAssertion) return <div style={style}><AssertionReason lines={lines} /></div>
  if (hasMatch)     return <div style={style}><MatchTable lines={lines} /></div>
  if (hasRoman)     return <div style={style}><RomanList lines={lines} /></div>

  // Plain — just render with proper line breaks
  return (
    <div style={{ lineHeight: 1.7, fontWeight: 500, color: 'var(--text)', ...style }}>
      {lines.map((line, i) => (
        <p key={i} style={{ margin: i > 0 ? '0.375rem 0 0' : 0 }}>{line}</p>
      ))}
    </div>
  )
}
