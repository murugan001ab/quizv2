import { useRef, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { Spinner } from '../components/Shared'

function ProfilePictureCard({ user, token, toast, updateUser }) {
  const fileRef = useRef(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)

  const pickFile = () => fileRef.current?.click()

  const onFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const objectUrl = URL.createObjectURL(file)
    setPreview(objectUrl)

    setUploading(true)
    try {
      const updated = await api.uploadProfilePicture(token, file)
      updateUser(updated)
      toast('Profile picture updated!', 'success')
    } catch (err) {
      toast(err.message, 'error')
    } finally {
      setUploading(false)
      URL.revokeObjectURL(objectUrl)
      setPreview(null)
      e.target.value = ''
    }
  }

  const avatarSrc = preview || user?.profile_url

  return (
    <div className="card fade-up" style={{ maxWidth: 480 }}>
      <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '1rem' }}>
        Profile picture
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
          width: 88, height: 88, borderRadius: '50%', flexShrink: 0, overflow: 'hidden',
          background: 'var(--bg3)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative',
        }}>
          {avatarSrc ? (
            <img src={avatarSrc} alt="Profile" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '1.75rem', color: 'var(--text3)' }}>
              {(user?.username || '?').slice(0, 1).toUpperCase()}
            </span>
          )}
          {uploading && (
            <div style={{
              position: 'absolute', inset: 0, background: 'rgba(10,10,15,0.6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Spinner sm />
            </div>
          )}
        </div>
        <div>
          <button className="btn btn-ghost btn-sm" onClick={pickFile} disabled={uploading}>
            {user?.profile_url ? 'Change picture' : 'Upload picture'}
          </button>
          <div style={{ fontSize: '0.72rem', color: 'var(--text3)', marginTop: '0.5rem' }}>
            JPEG, PNG, WEBP or GIF · up to 5MB
          </div>
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          style={{ display: 'none' }}
          onChange={onFileChange}
        />
      </div>
    </div>
  )
}

function ChangePasswordCard({ token, toast }) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)

  const submit = async () => {
    if (!currentPassword || !newPassword) return toast('Fill in all fields', 'error')
    if (newPassword.length < 6) return toast('New password must be at least 6 characters', 'error')
    if (newPassword !== confirmPassword) return toast("New passwords don't match", 'error')

    setSaving(true)
    try {
      await api.changePassword(token, { current_password: currentPassword, new_password: newPassword })
      toast('Password updated!', 'success')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      toast(err.message, 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card fade-up-1" style={{ maxWidth: 480 }}>
      <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '1rem' }}>
        Change password
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="input-group">
          <label className="input-label">Current password</label>
          <input className="input" type="password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} placeholder="••••••••" />
        </div>
        <div className="input-group">
          <label className="input-label">New password</label>
          <input className="input" type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="At least 6 characters" />
        </div>
        <div className="input-group">
          <label className="input-label">Confirm new password</label>
          <input className="input" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Repeat new password" />
        </div>
        <button className="btn btn-primary w-full" onClick={submit} disabled={saving}>
          {saving ? <Spinner sm /> : 'Update password'}
        </button>
      </div>
    </div>
  )
}

export default function Account() {
  const { user, token, updateUser } = useAuth()
  const toast = useToast()

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">Account</h1>
        <p className="page-sub">Manage your profile picture and password</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="card" style={{ maxWidth: 480 }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Signed in as
          </div>
          <div style={{ fontWeight: 600 }}>{user?.username}</div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text3)' }}>{user?.email}</div>
        </div>

        <ProfilePictureCard user={user} token={token} toast={toast} updateUser={updateUser} />
        <ChangePasswordCard token={token} toast={toast} />
      </div>
    </div>
  )
}
