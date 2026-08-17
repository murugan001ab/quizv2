import React from 'react'

// ============================================================
// REGEX
// ============================================================

const ASSERTION_RE = /கூற்று\s*\(A\)|காரணம்\s*\(R\)/i
const MATCH_RE = /பொருத்துக|match\s+the\s+following/i
const ROMAN_LINE_RE = /^(?=[IVXLCDM]+\.)[IVXLCDM]+\.\s/
const ALPHA_LIST_RE = /^\([a-d]\)\s/i
const NUMBER_COL_RE = /^\d+\.\s/

const CODE_PATTERNS = [
  /output\s+of\s+the\s+following\s+code/i,
  /following\s+code/i,
  /console\.log\s*\(/i,
  /print\s*\(/i,
  /\bdef\s+\w+\s*\(/i,
  /\bfunction\s+\w+\s*\(/i,
  /\bfor\s+\w+\s+in\b/i,
  /\bwhile\s+.+:/i,
  /\bif\s+.+:/i,
  /\belif\s+.+:/i,
  /\belse\s*:/i,
  /\breturn\s+/i,
  /\bimport\s+\w+/i,
  /\bfrom\s+\w+\s+import/i,
  /\bconst\s+\w+\s*=/i,
  /\blet\s+\w+\s*=/i,
  /\bvar\s+\w+\s*=/i,
  /\bSystem\.out\.println\s*\(/i,
]

// ============================================================
// BASIC HELPERS
// ============================================================

function isRomanLine(text) {
  return ROMAN_LINE_RE.test(text.trim())
}

function isAlphaLine(text) {
  return ALPHA_LIST_RE.test(text.trim())
}

function isNumberLine(text) {
  return NUMBER_COL_RE.test(text.trim())
}

function splitLines(text) {
  return text
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
}

// ============================================================
// MARKDOWN CLEANING
// ============================================================

function cleanQuestionText(text) {
  return text
    .replace(/^\s*\*\*Q\d+\*\*\s*/i, '')
    .replace(/^\s*Q\d+\s*/i, '')
    .replace(/\*\*(.*?)\*\*/gs, '$1')
    .trim()
}

// ============================================================
// CODE DETECTION
// ============================================================

function isCodeQuestion(text) {
  if (!text) return false
  if (text.includes('```')) return true
  return CODE_PATTERNS.some(pattern => pattern.test(text))
}

// ============================================================
// EXTRACT MARKDOWN CODE BLOCK
// ============================================================

function extractCodeBlock(text) {
  const match = text.match(
    /```(?:python|py|javascript|js|typescript|ts|java|c|cpp)?\s*\n?([\s\S]*?)```/i
  )

  if (!match) return null

  return {
    question: text.slice(0, match.index).trim(),
    code: match[1].trim(),
  }
}

// ============================================================
// SPLIT QUESTION FROM CODE
// ============================================================

function splitQuestionAndCode(text) {
  const patterns = [
    /^(.*?following\s+code\s*\?)\s*([\s\S]*)$/i,
    /^(.*?output\s+of\s+the\s+following\s+code)\s*:?\s*([\s\S]*)$/i,
    /^(.*?output\s+of\s+this\s+code\s*\?)\s*([\s\S]*)$/i,
    /^(.*?what\s+is\s+the\s+output\s*\?)\s*([\s\S]*)$/i,
  ]

  for (const pattern of patterns) {
    const match = text.match(pattern)
    if (!match) continue

    const question = match[1].trim()
    const code = match[2].trim()

    if (code) {
      return { question, code }
    }
  }

  return null
}

// ============================================================
// PYTHON STATEMENT SPLITTER
// ============================================================

function splitPythonStatements(code) {
  const statements = []
  let current = ''
  let quote = null
  let escaped = false
  let parenDepth = 0
  let bracketDepth = 0
  let braceDepth = 0

  for (let i = 0; i < code.length; i++) {
    const char = code[i]

    if (quote !== null) {
      current += char
      if (escaped) {
        escaped = false
        continue
      }
      if (char === '\\') {
        escaped = true
        continue
      }
      if (char === quote) {
        quote = null
      }
      continue
    }

    if (char === "'" || char === '"') {
      quote = char
      current += char
      continue
    }

    if (char === '(') parenDepth++
    if (char === ')') parenDepth--
    if (char === '[') bracketDepth++
    if (char === ']') bracketDepth--
    if (char === '{') braceDepth++
    if (char === '}') braceDepth--

    const outsideBrackets =
      parenDepth === 0 &&
      bracketDepth === 0 &&
      braceDepth === 0 &&
      quote === null

    if (char === '\n' && outsideBrackets) {
      if (current.trim()) statements.push(current.trim())
      current = ''
      continue
    }

    if (char === ';' && outsideBrackets) {
      if (current.trim()) statements.push(current.trim())
      current = ''
      continue
    }

    current += char

    if (char === ':' && outsideBrackets) {
      let j = i + 1
      while (j < code.length && /\s/.test(code[j])) j++
      const remaining = code.slice(j)

      const nextStatement =
        /^(if|elif|else|for|while|try|except|finally|def|class|return|break|continue|pass|raise|print)\b/i.test(
          remaining
        )

      if (nextStatement) {
        if (current.trim()) statements.push(current.trim())
        current = ''
        continue
      }
    }
  }

  if (current.trim()) {
    statements.push(current.trim())
  }

  return statements
}

// ============================================================
// SPLIT ATTACHED ELSE / ELIF / EXCEPT / FINALLY
// ============================================================

function splitAttachedKeywords(statements) {
  const result = []

  for (const statement of statements) {
    const parts = statement.split(
      /\s+(?=(?:else|elif|except|finally)\s*:)/i
    )

    for (const part of parts) {
      if (part.trim()) {
        result.push(part.trim())
      }
    }
  }

  return result
}

// ============================================================
// BUILD PYTHON INDENTATION
// ============================================================

function buildPythonCode(statements) {
  const result = []
  let indent = 0
  let pendingDedentAfterSingleStatement = false

  for (const statement of statements) {
    let line = statement.trim()
    if (!line) continue

    // Remove preexisting leading whitespace
    line = line.replace(/^\s+/, '')

    // If previous line was a single terminal statement (break/continue/pass/return)
    // inside a nested inline block, step back one indentation level
    if (pendingDedentAfterSingleStatement && !line.endsWith(':')) {
      if (!/^(else|elif|except|finally)\b/i.test(line)) {
        indent = Math.max(0, indent - 1)
      }
      pendingDedentAfterSingleStatement = false
    }

    // De-indent branch headers
    if (/^(else|elif|except|finally)\b/i.test(line)) {
      indent = Math.max(0, indent - 1)
      pendingDedentAfterSingleStatement = false
    }

    // Add properly indented line (4 spaces per level)
    result.push('    '.repeat(indent) + line)

    // Increase indentation after block openers
    if (line.endsWith(':')) {
      indent++
      pendingDedentAfterSingleStatement = false
    } else if (/^(break|continue|pass|return\b)/i.test(line)) {
      // Mark for auto-dedent so following lines don't stay trapped inside the inner if-block
      pendingDedentAfterSingleStatement = true
    }
  }

  return result.join('\n')
}

// ============================================================
// FORMAT CODE
// ============================================================

function formatCode(code) {
  if (!code) return ''

  let value = code
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .trim()

  value = value.replace(/^```(?:python|py|javascript|js)?\s*/i, '')
  value = value.replace(/\s*```$/i, '')
  value = value.trim()

  let statements = splitPythonStatements(value)
  statements = splitAttachedKeywords(statements)

  return buildPythonCode(statements)
}

// ============================================================
// CODE QUESTION RENDERER
// ============================================================

function CodeQuestion({ text }) {
  const cleanedText = cleanQuestionText(text)
  let questionText = ''
  let codeSnippet = ''

  const codeBlock = extractCodeBlock(cleanedText)

  if (codeBlock) {
    questionText = codeBlock.question
    codeSnippet = formatCode(codeBlock.code)
  } else {
    const split = splitQuestionAndCode(cleanedText)
    if (split) {
      questionText = split.question
      codeSnippet = formatCode(split.code)
    } else {
      questionText = cleanedText
    }
  }

  return (
    <div className="flex flex-col gap-2.5">
      {questionText && (
        <p className="font-medium text-white/90 leading-relaxed">
          {questionText}
        </p>
      )}

      {codeSnippet && (
        <pre className="font-mono text-sm bg-slate-950/80 border border-white/10 rounded-xl p-4 text-emerald-300 overflow-x-auto leading-relaxed shadow-inner whitespace-pre">
          <code>{codeSnippet}</code>
        </pre>
      )}
    </div>
  )
}

// ============================================================
// ASSERTION / REASON
// ============================================================

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
              className={`flex gap-2.5 rounded-lg px-3 py-2 border ${
                isA
                  ? 'bg-accent-400/[0.07] border-accent-400/20'
                  : 'bg-glow-violet/[0.07] border-glow-violet/20'
              }`}
            >
              <span
                className={`font-bold text-sm shrink-0 pt-px ${
                  isA ? 'text-accent-300' : 'text-glow-violet'
                }`}
              >
                {label.trim()}:
              </span>
              <span className="leading-relaxed text-white/90">{body}</span>
            </div>
          )
        }

        return (
          <p key={i} className="text-white/60 text-sm mt-1 leading-relaxed">
            {line}
          </p>
        )
      })}
    </div>
  )
}

// ============================================================
// MATCH TABLE
// ============================================================

function MatchTable({ lines }) {
  const header = []
  const leftCol = []
  const rightCol = []
  const footer = []

  let phase = 'header'

  for (const line of lines) {
    if (MATCH_RE.test(line) && phase === 'header') {
      header.push(line)
      continue
    }

    if (isAlphaLine(line)) {
      phase = 'left'
      leftCol.push(line)
      continue
    }

    if (isNumberLine(line)) {
      phase = 'right'
      rightCol.push(line)
      continue
    }

    if (phase === 'header') {
      header.push(line)
    } else {
      footer.push(line)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      {header.map((h, i) => (
        <p key={i} className="font-semibold text-white/90 leading-relaxed">
          {h}
        </p>
      ))}

      {(leftCol.length > 0 || rightCol.length > 0) && (
        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 p-3 bg-white/[0.04] border border-white/10 rounded-xl">
          <div className="text-xs font-bold text-white/40 uppercase tracking-wide pb-1 border-b border-white/10">
            Column A
          </div>
          <div className="text-xs font-bold text-white/40 uppercase tracking-wide pb-1 border-b border-white/10">
            Column B
          </div>

          {Array.from({
            length: Math.max(leftCol.length, rightCol.length),
          }).map((_, i) => (
            <React.Fragment key={i}>
              <div className="text-sm text-white/90 leading-normal py-0.5">
                {leftCol[i] || ''}
              </div>
              <div className="text-sm text-white/90 leading-normal py-0.5">
                {rightCol[i] || ''}
              </div>
            </React.Fragment>
          ))}
        </div>
      )}

      {footer.map((f, i) => (
        <p key={i} className="text-white/60 text-sm leading-relaxed">
          {f}
        </p>
      ))}
    </div>
  )
}

// ============================================================
// ROMAN LIST
// ============================================================

function RomanList({ lines }) {
  const header = []
  const items = []
  const footer = []

  let phase = 'header'

  for (const line of lines) {
    if (isRomanLine(line)) {
      phase = 'items'
      items.push(line)
      continue
    }

    if (phase === 'header') {
      header.push(line)
    } else {
      footer.push(line)
    }
  }

  return (
    <div className="flex flex-col gap-1.5">
      {header.map((h, i) => (
        <p key={i} className="font-medium text-white/90 leading-loose">
          {h}
        </p>
      ))}

      {items.length > 0 && (
        <div className="flex flex-col gap-1 px-3.5 py-2.5 bg-white/[0.04] border border-white/10 rounded-xl mt-1">
          {items.map((item, i) => {
            const match = item.match(/^[IVXLCDM]+\./)
            const number = match?.[0] || ''
            const content = item.replace(/^[IVXLCDM]+\.\s*/, '')

            return (
              <div key={i} className="flex gap-2 text-sm leading-relaxed text-white/90">
                <span className="font-bold text-accent-400 min-w-[28px] shrink-0">
                  {number}
                </span>
                <span>{content}</span>
              </div>
            )
          })}
        </div>
      )}

      {footer.map((f, i) => (
        <p key={i} className="text-white/60 text-sm leading-relaxed">
          {f}
        </p>
      ))}
    </div>
  )
}

// ============================================================
// MAIN COMPONENT
// ============================================================

export default function QuestionText({ text, className = '' }) {
  if (!text) return null

  const lines = splitLines(text)

  const hasAssertion = lines.some(line => ASSERTION_RE.test(line))
  const hasMatch = lines.some(line => MATCH_RE.test(line))
  const hasRoman = lines.some(line => isRomanLine(line))
  const isCode = isCodeQuestion(text)

  if (hasAssertion) {
    return (
      <div className={className}>
        <AssertionReason lines={lines} />
      </div>
    )
  }

  if (hasMatch) {
    return (
      <div className={className}>
        <MatchTable lines={lines} />
      </div>
    )
  }

  if (hasRoman) {
    return (
      <div className={className}>
        <RomanList lines={lines} />
      </div>
    )
  }

  if (isCode) {
    return (
      <div className={className}>
        <CodeQuestion text={text} />
      </div>
    )
  }

  return (
    <div className={`leading-relaxed font-medium text-white/90 ${className}`}>
      {lines.map((line, i) => (
        <p key={i} className={i > 0 ? 'mt-1.5' : ''}>
          {line}
        </p>
      ))}
    </div>
  )
}