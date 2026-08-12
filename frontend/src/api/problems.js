// Adjust the import to whatever axios instance your project already uses
// (e.g. one with baseURL + auth interceptor set up in src/api/client.js)
import api from "./client";

export const getTopics = () => api.get("/problems/topics").then((r) => r.data);

export const listProblems = (params = {}) =>
  api.get("/problems", { params }).then((r) => r.data);

export const getProblem = (id) => api.get(`/problems/${id}`).then((r) => r.data);

export const unlockProblem = (id, password) =>
  api.post(`/problems/${id}/unlock`, { password }).then((r) => r.data);

export const runCode = (id, code, language = "python3") =>
  api.post(`/problems/${id}/run`, { code, language }).then((r) => r.data);

export const submitCode = (id, code, language = "python3") =>
  api.post(`/problems/${id}/submit`, { code, language }).then((r) => r.data);

export const saveCode = (id, code, language = "python3") =>
  api.put(`/problems/${id}/save`, { code, language }).then((r) => r.data);

export const mySubmissions = (id) =>
  api.get(`/problems/${id}/submissions`).then((r) => r.data);

export const getSubmission = (id) =>
  api.get(`/problems/submissions/${id}`).then((r) => r.data);

// ---- Admin ----
export const adminListTopics = () => api.get("/admin/problems/topics").then((r) => r.data);
export const adminCreateTopic = (data) =>
  api.post("/admin/problems/topics", data).then((r) => r.data);

export const adminListProblems = () => api.get("/admin/problems").then((r) => r.data);
export const adminGetProblem = (id) => api.get(`/admin/problems/${id}`).then((r) => r.data);
export const adminCreateProblem = (data) =>
  api.post("/admin/problems", data).then((r) => r.data);
export const adminUpdateProblem = (id, data) =>
  api.put(`/admin/problems/${id}`, data).then((r) => r.data);
export const adminDeleteProblem = (id) => api.delete(`/admin/problems/${id}`);

export const adminAddTestCase = (problemId, data) =>
  api.post(`/admin/problems/${problemId}/test-cases`, data).then((r) => r.data);
export const adminUpdateTestCase = (tcId, data) =>
  api.put(`/admin/problems/test-cases/${tcId}`, data).then((r) => r.data);
export const adminDeleteTestCase = (tcId) =>
  api.delete(`/admin/problems/test-cases/${tcId}`);

// ---- Admin: LeetCode import ----
export const adminSearchLeetcode = (q, limit = 15) =>
  api.get("/admin/leetcode/search", { params: { q, limit } }).then((r) => r.data);

export const adminImportLeetcode = (titleSlug) =>
  api.get(`/admin/leetcode/import/${titleSlug}`).then((r) => r.data);
