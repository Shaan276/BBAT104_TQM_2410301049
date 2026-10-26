import React, { useState } from 'react';
import { Volume2, VolumeX, Shield, GraduationCap, Zap, RefreshCw, UserPlus } from 'lucide-react';
import { SoundFX } from '../utils/audio';

export default function Navbar({
  currentUser,
  users,
  onSwitchUser,
  onCreateUser,
  soundOn,
  onToggleSound,
  activeTab,
  setActiveTab
}) {
  const [showUserModal, setShowUserModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newRole, setNewRole] = useState('STUDENT');
  const [errorMsg, setErrorMsg] = useState('');

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newUsername.trim()) {
      setErrorMsg('Username cannot be blank (Poka-Yoke intercept)');
      return;
    }
    const res = await onCreateUser(newUsername.trim(), newRole);
    if (res.success) {
      setNewUsername('');
      setErrorMsg('');
      setShowUserModal(false);
    } else {
      setErrorMsg(res.error || 'Failed to create user');
    }
  };

  const isAdmin = currentUser?.role === 'ADMIN';

  return (
    <header className="sticky top-0 z-50 px-4 py-3 border-b border-purple-500/20" style={{ background: 'var(--bg-header)', backdropFilter: 'blur(16px)' }}>
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <div 
          onClick={() => setActiveTab('quizzes')} 
          className="flex items-center gap-2 cursor-pointer group select-none"
        >
          <div className="w-10 h-10 rounded-xl flex items-center justify-center font-fun text-2xl font-bold bg-gradient-to-br from-amber-400 via-rose-500 to-purple-600 shadow-lg shadow-purple-500/30 group-hover:scale-105 transition-transform">
            ⚡
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-fun text-2xl font-bold tracking-wide text-white group-hover:text-amber-300 transition-colors">
                Quiz<span className="text-amber-400">TQM</span>
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full font-mono font-semibold bg-purple-500/30 text-purple-200 border border-purple-400/30">
                Q05
              </span>
            </div>
            <p className="text-[10px] text-purple-300/70 font-medium tracking-wider uppercase">
              Speed & Quality Assessment
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-purple-950/60 p-1 rounded-2xl border border-purple-500/20">
          <button
            onClick={() => setActiveTab('quizzes')}
            className={`px-4 py-1.5 rounded-xl font-fun text-sm font-semibold transition-all ${
              activeTab === 'quizzes'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/40'
                : 'text-purple-200 hover:text-white hover:bg-purple-900/40'
            }`}
          >
            🎮 Play Quizzes
          </button>

          {!isAdmin && (
            <button
              onClick={() => setActiveTab('my-history')}
              className={`px-4 py-1.5 rounded-xl font-fun text-sm font-semibold transition-all ${
                activeTab === 'my-history'
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-600/40'
                  : 'text-purple-200 hover:text-white hover:bg-purple-900/40'
              }`}
            >
              📊 My Scores
            </button>
          )}

          {isAdmin && (
            <button
              onClick={() => setActiveTab('admin')}
              className={`px-4 py-1.5 rounded-xl font-fun text-sm font-semibold transition-all ${
                activeTab === 'admin'
                  ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/40'
                  : 'text-amber-300 hover:text-amber-100 hover:bg-purple-900/40'
              }`}
            >
              🛠️ Teacher Studio
            </button>
          )}
        </nav>

        {/* Right Tools: Audio + User Selector */}
        <div className="flex items-center gap-3">
          
          {/* Audio Toggle */}
          <button
            onClick={onToggleSound}
            title={soundOn ? 'Sound FX On' : 'Sound FX Muted'}
            className="w-9 h-9 rounded-xl flex items-center justify-center bg-purple-900/40 hover:bg-purple-800/60 text-purple-200 hover:text-white border border-purple-500/30 transition-all"
          >
            {soundOn ? <Volume2 size={18} className="text-emerald-400" /> : <VolumeX size={18} className="text-rose-400" />}
          </button>

          {/* User Selector Dropdown */}
          <div className="flex items-center gap-2 bg-purple-950/70 border border-purple-500/30 px-3 py-1.5 rounded-2xl">
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
              isAdmin ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
            }`}>
              {isAdmin ? <Shield size={14} /> : <GraduationCap size={14} />}
            </div>

            <select
              value={currentUser?.id || ''}
              onChange={(e) => onSwitchUser(parseInt(e.target.value, 10))}
              className="bg-transparent text-white font-fun text-sm font-semibold focus:outline-none cursor-pointer pr-1"
            >
              {users.map((u) => (
                <option key={u.id} value={u.id} className="bg-slate-900 text-white">
                  {u.username} ({u.role})
                </option>
              ))}
            </select>

            <button
              onClick={() => setShowUserModal(true)}
              title="Add New User"
              className="p-1 hover:bg-purple-800/50 rounded-lg text-purple-300 hover:text-white transition-colors ml-1"
            >
              <UserPlus size={16} />
            </button>
          </div>

        </div>

      </div>

      {/* New User Modal */}
      {showUserModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="glass-panel-elevated p-6 max-w-md w-full border border-purple-400/40 animate-in fade-in zoom-in-95 duration-200">
            <h3 className="font-fun text-xl font-bold text-white mb-1">Create New Profile</h3>
            <p className="text-xs text-purple-300/80 mb-4">Add a new student or teacher account to test role isolation.</p>
            
            {errorMsg && (
              <div className="mb-3 px-3 py-2 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-medium">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Username</label>
                <input
                  type="text"
                  placeholder="e.g. rahul, ananya, testuser"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none focus:border-amber-400"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Role</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setNewRole('STUDENT')}
                    className={`py-2 px-3 rounded-xl font-fun text-sm font-semibold border transition-all ${
                      newRole === 'STUDENT'
                        ? 'bg-emerald-600/40 border-emerald-400 text-emerald-200'
                        : 'bg-purple-950/40 border-purple-500/20 text-purple-300'
                    }`}
                  >
                    🎓 Student
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewRole('ADMIN')}
                    className={`py-2 px-3 rounded-xl font-fun text-sm font-semibold border transition-all ${
                      newRole === 'ADMIN'
                        ? 'bg-amber-600/40 border-amber-400 text-amber-200'
                        : 'bg-purple-950/40 border-purple-500/20 text-purple-300'
                    }`}
                  >
                    👨‍🏫 Admin
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUserModal(false)}
                  className="px-4 py-2 rounded-xl text-purple-300 hover:text-white font-fun text-sm font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-push btn-push-purple px-5 py-2 text-sm"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
