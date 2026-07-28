import { useEffect, useState } from "react";
import { Spinner, EmptyState } from "./Shared";
import {
  getDiscussion,
  createPost,
  deletePost,
  togglePostLike,
  createComment,
  deleteComment,
  toggleCommentLike,
} from "../api/discussion";

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

function LikeButton({ liked, count, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 text-xs font-medium transition-colors duration-150
        ${liked ? "text-rose-400" : "text-white/40 hover:text-white/70"}`}
    >
      <span>{liked ? "❤️" : "🤍"}</span>
      <span>{count}</span>
    </button>
  );
}

function Avatar({ name }) {
  const initial = (name || "?").trim().charAt(0).toUpperCase();
  return (
    <div className="w-8 h-8 shrink-0 rounded-full bg-white/[0.08] border border-white/10 flex items-center justify-center text-xs font-semibold text-white/70">
      {initial}
    </div>
  );
}

function Comment({ comment, onLike, onDelete }) {
  return (
    <div className="flex gap-2.5 py-2.5">
      <Avatar name={comment.user?.name} />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2 flex-wrap">
          <span className="text-xs font-semibold text-white/80">{comment.user?.name}</span>
          <span className="text-[0.7rem] text-white/30">{timeAgo(comment.created_at)}</span>
        </div>
        <p className="text-sm text-white/70 mt-0.5 whitespace-pre-wrap break-words">
          {comment.content}
        </p>
        <div className="flex items-center gap-3 mt-1">
          <LikeButton liked={comment.liked_by_me} count={comment.likes_count} onClick={onLike} />
          {comment.is_mine && (
            <button
              onClick={onDelete}
              className="text-xs text-white/30 hover:text-rose-400 transition-colors duration-150"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function PostCard({ post, onChanged }) {
  const [commentOpen, setCommentOpen] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [busy, setBusy] = useState(false);

  const handleLikePost = async () => {
    const r = await togglePostLike(post.id);
    onChanged((prev) =>
      prev.map((p) => (p.id === post.id ? { ...p, liked_by_me: r.liked, likes_count: r.likes_count } : p))
    );
  };

  const handleDeletePost = async () => {
    if (!confirm("Delete this post?")) return;
    await deletePost(post.id);
    onChanged((prev) => prev.filter((p) => p.id !== post.id));
  };

  const handleLikeComment = async (commentId) => {
    const r = await toggleCommentLike(commentId);
    onChanged((prev) =>
      prev.map((p) =>
        p.id !== post.id
          ? p
          : {
              ...p,
              comments: p.comments.map((c) =>
                c.id === commentId ? { ...c, liked_by_me: r.liked, likes_count: r.likes_count } : c
              ),
            }
      )
    );
  };

  const handleDeleteComment = async (commentId) => {
    await deleteComment(commentId);
    onChanged((prev) =>
      prev.map((p) =>
        p.id !== post.id ? p : { ...p, comments: p.comments.filter((c) => c.id !== commentId) }
      )
    );
  };

  const handleAddComment = async () => {
    const text = commentText.trim();
    if (!text) return;
    setBusy(true);
    try {
      const created = await createComment(post.id, text);
      setCommentText("");
      onChanged((prev) =>
        prev.map((p) => (p.id === post.id ? { ...p, comments: [...p.comments, created] } : p))
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="glass rounded-2xl p-4 sm:p-5">
      <div className="flex gap-3">
        <Avatar name={post.user?.name} />
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-sm font-semibold text-white/85">{post.user?.name}</span>
            <span className="text-xs text-white/30">{timeAgo(post.created_at)}</span>
          </div>
          <p className="text-sm text-white/75 mt-1 whitespace-pre-wrap break-words leading-relaxed">
            {post.content}
          </p>

          <div className="flex items-center gap-4 mt-3">
            <LikeButton liked={post.liked_by_me} count={post.likes_count} onClick={handleLikePost} />
            <button
              onClick={() => setCommentOpen((v) => !v)}
              className="text-xs font-medium text-white/40 hover:text-white/70 transition-colors duration-150"
            >
              💬 {post.comments.length} {post.comments.length === 1 ? "comment" : "comments"}
            </button>
            {post.is_mine && (
              <button
                onClick={handleDeletePost}
                className="text-xs text-white/30 hover:text-rose-400 transition-colors duration-150 ml-auto"
              >
                Delete
              </button>
            )}
          </div>

          {commentOpen && (
            <div className="mt-2 border-t border-white/10 pt-1">
              {post.comments.map((c) => (
                <Comment
                  key={c.id}
                  comment={c}
                  onLike={() => handleLikeComment(c.id)}
                  onDelete={() => handleDeleteComment(c.id)}
                />
              ))}

              <div className="flex gap-2 mt-2">
                <input
                  className="input flex-1 !py-2 text-sm"
                  placeholder="Write a comment…"
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAddComment()}
                  disabled={busy}
                />
                <button
                  onClick={handleAddComment}
                  disabled={busy || !commentText.trim()}
                  className="btn btn-ghost btn-sm shrink-0"
                >
                  {busy ? <Spinner sm /> : "Post"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DiscussionRoom({ problemId }) {
  const [posts, setPosts] = useState(null); // null = loading
  const [error, setError] = useState("");
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setPosts(null);
    setError("");
    getDiscussion(problemId)
      .then((data) => !cancelled && setPosts(data))
      .catch((e) => {
        if (cancelled) return;
        setError(
          e?.response?.status === 403
            ? "Solve this problem to unlock its discussion room."
            : "Couldn't load the discussion room."
        );
      });
    return () => {
      cancelled = true;
    };
  }, [problemId]);

  const handlePost = async () => {
    const text = newPost.trim();
    if (!text) return;
    setPosting(true);
    try {
      const created = await createPost(problemId, text);
      setPosts((prev) => [created, ...(prev || [])]);
      setNewPost("");
    } finally {
      setPosting(false);
    }
  };

  if (error) {
    return <EmptyState icon="🔒" title="Discussion locked" sub={error} />;
  }

  if (posts === null) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="glass rounded-2xl p-4 sm:p-5">
        <textarea
          className="input w-full min-h-[80px] resize-y text-sm"
          placeholder="Share your approach, ask a question, or discuss the problem…"
          value={newPost}
          onChange={(e) => setNewPost(e.target.value)}
        />
        <div className="flex justify-end mt-2">
          <button
            onClick={handlePost}
            disabled={posting || !newPost.trim()}
            className="btn btn-primary btn-sm"
          >
            {posting ? <Spinner sm /> : "Post"}
          </button>
        </div>
      </div>

      {posts.length === 0 ? (
        <EmptyState
          icon="💬"
          title="No discussion yet"
          sub="Be the first to share your solution or ask a question."
        />
      ) : (
        <div className="space-y-3">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onChanged={setPosts} />
          ))}
        </div>
      )}
    </div>
  );
}
