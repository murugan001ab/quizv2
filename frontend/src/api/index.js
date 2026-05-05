const BASE = ''  // vite proxy handles /auth /admin /user

async function req(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // Auth
  register: (data) => req('POST', '/auth/register', data),
  login: async (username, password) => {
    const form = new URLSearchParams({ username, password })
    const res = await fetch('/auth/login', { method: 'POST', body: form })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(err.detail || 'Login failed')
    }
    return res.json()
  },
  me: (token) => req('GET', '/auth/me', null, token),

  // Admin
  adminStats: (token) => req('GET', '/admin/stats', null, token),
  adminUsers: (token) => req('GET', '/admin/users', null, token),
  adminQuizzes: (token, params = '') => req('GET', `/admin/quizzes${params}`, null, token),
  adminQuiz: (token, id) => req('GET', `/admin/quizzes/${id}`, null, token),
  createQuiz: (token, data) => req('POST', '/admin/quizzes', data, token),
  updateQuiz: (token, id, data) => req('PUT', `/admin/quizzes/${id}`, data, token),
  deleteQuiz: (token, id) => req('DELETE', `/admin/quizzes/${id}`, null, token),
  addQuestion: (token, quizId, data) => req('POST', `/admin/quizzes/${quizId}/questions`, data, token),
  updateQuestion: (token, qId, data) => req('PUT', `/admin/questions/${qId}`, data, token),
  deleteQuestion: (token, qId) => req('DELETE', `/admin/questions/${qId}`, null, token),
  quizAttempts: (token, quizId) => req('GET', `/admin/quizzes/${quizId}/attempts`, null, token),

  // User
  userQuizzes: (token, params = '') => req('GET', `/user/quizzes${params}`, null, token),
  userQuiz: (token, id) => req('GET', `/user/quizzes/${id}`, null, token),
  startQuiz: (token, id) => req('POST', `/user/quizzes/${id}/start`, {}, token),
  submitQuiz: (token, attemptId, answers) => req('POST', `/user/attempts/${attemptId}/submit`, { answers }, token),
  myResults: (token) => req('GET', '/user/results', null, token),
  resultDetail: (token, id) => req('GET', `/user/results/${id}`, null, token),
}
