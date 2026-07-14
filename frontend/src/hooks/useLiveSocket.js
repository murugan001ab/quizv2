import { useCallback, useEffect, useRef, useState } from 'react'

// Same pattern as AdminMonitor's buildAdminWsUrl: reuse VITE_API_URL so the
// ws/http always point at the same backend, falling back to same-origin so
// the Vite dev proxy can do its job.
function buildLiveWsUrl(code, token,link_token) {
  const apiBase = import.meta.env.VITE_API_URL || ''
  if (apiBase) {
    const wsBase = apiBase.replace(/^http/, 'ws').replace(/\/$/, '')
    return `${wsBase}/live/ws/${code}?token=${token}&link=${link_token}`
  }
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/live/ws/${code}?token=${token}&link=${link_token}`
}

export function useLiveSocket() {
  const wsRef = useRef(null)
  const [connected, setConnected] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [channelInfo, setChannelInfo] = useState(null) // { code, name, quiz_title }
  const [users, setUsers] = useState([])
  const [quizState, setQuizState] = useState('waiting') // waiting | in_progress | finished
  const [question, setQuestion] = useState(null)
  const [correctIndex, setCorrectIndex] = useState(null)
  const [answerCounts, setAnswerCounts] = useState(null)
  const [locked, setLocked] = useState(false)
  const [leaderboard, setLeaderboard] = useState([])
  const [explainQuestion, setExplainQuestion] = useState(null)
  const [error, setError] = useState('')

  const join = useCallback((code, token, password,link_token) => {
    setError('')
    const ws = new WebSocket(buildLiveWsUrl(code, token,link_token))
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      ws.send(JSON.stringify({ type: 'join', password: password || undefined }))
    }

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      switch (msg.type) {
        case 'joined':
          setChannelInfo(msg.channel)
          setIsAdmin(msg.is_admin)
          setQuizState(msg.channel.state)
          break
        case 'user_list':
          setUsers(msg.users)
          break
        case 'quiz_started':
          setQuizState('in_progress')
          setCorrectIndex(null)
          setLocked(false)
          break
        case 'question':
          setQuestion(msg)
          setCorrectIndex(null)
          setAnswerCounts(null)
          setLocked(false)
          break
        case 'question_locked':
          // Sent to participants: the round is over, but the correct answer
          // is withheld until the admin runs the explanation walkthrough.
          setLocked(true)
          break
        case 'question_ended':
          // Only the admin receives this (host-only review of the round).
          setCorrectIndex(msg.correct_index)
          setAnswerCounts(msg.counts || null)
          setLocked(true)
          break
        case 'leaderboard':
          setLeaderboard(msg.scores)
          break
        case 'quiz_ended':
          setQuizState('finished')
          setLeaderboard(msg.final_leaderboard)
          // Quiz is over — clear the in-progress question so stale "current
          // question" UI (host view) doesn't linger after finish.
          setQuestion(null)
          setCorrectIndex(null)
          setAnswerCounts(null)
          setLocked(false)
          break
        case 'explain_question':
          setExplainQuestion(msg)
          break
        case 'error':
          setError(msg.message)
          break
      }
    }

    ws.onclose = () => setConnected(false)
  }, [])

  const startQuiz = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: 'start_quiz' }))
  }, [])

  const submitAnswer = useCallback((index, optionIndex) => {
    wsRef.current?.send(JSON.stringify({ type: 'answer', index, option_index: optionIndex }))
  }, [])

  const startExplain = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: 'start_explain' }))
  }, [])

  const explainNext = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: 'explain_next' }))
  }, [])

  const explainPrev = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: 'explain_prev' }))
  }, [])

  const leave = useCallback(() => {
    try { wsRef.current?.send(JSON.stringify({ type: 'leave' })) } catch { /* ignore */ }
    wsRef.current?.close()
  }, [])

  useEffect(() => () => wsRef.current?.close(), [])

  return {
    connected, isAdmin, channelInfo, users, quizState, question,
    correctIndex, answerCounts, locked, leaderboard, explainQuestion, error,
    join, startQuiz, submitAnswer, leave, startExplain, explainNext, explainPrev,
  }
}
