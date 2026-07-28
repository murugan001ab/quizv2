import api from "./client";

export const getDiscussion = (problemId) =>
  api.get(`/problems/${problemId}/discussion`).then((r) => r.data);

export const createPost = (problemId, content) =>
  api.post(`/problems/${problemId}/discussion`, { content }).then((r) => r.data);

export const deletePost = (postId) => api.delete(`/discussion/posts/${postId}`);

export const togglePostLike = (postId) =>
  api.post(`/discussion/posts/${postId}/like`).then((r) => r.data);

export const createComment = (postId, content) =>
  api.post(`/discussion/posts/${postId}/comments`, { content }).then((r) => r.data);

export const deleteComment = (commentId) =>
  api.delete(`/discussion/comments/${commentId}`);

export const toggleCommentLike = (commentId) =>
  api.post(`/discussion/comments/${commentId}/like`).then((r) => r.data);
