import React, { useState } from 'react';
import { 
  Zap, 
  LayoutDashboard, 
  History, 
  ShieldCheck, 
  BookOpen, 
  Database, 
  Settings, 
  UserPlus, 
  Volume2, 
  VolumeX, 
  CheckCircle, 
  Flame, 
  Clock, 
  Award, 
  Layers, 
  FileText 
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  setActiveTab,
  currentUser,
  users,
  onSwitchUser,
  onCreateUser,
  soundOn,
  onToggleSound,
  onStartQuickQuiz,
  firstQuizId
}) {
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newRole, setNewRole] = useState('STUDENT');
  const [errorMsg, setErrorMsg] = useState('');

  const isAdmin = currentUser?.role === 'ADMIN';

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newUsername.trim()) {
      setErrorMsg('Username cannot be blank');
      return;
    }
    const res = await onCreateUser(newUsername.trim(), newRole);
    if (res.success) {
      setNewUsername('');
      setErrorMsg('');
      setShowAddUser(false);
    } else {
      setErrorMsg(res.error || 'Failed to create user');
    }
  };

  return (
    <aside className="w-64 bg-[#0C131F] border-r border-[#1E2D47] flex flex-col justify-between shrink-0 select-none min-h-screen">
      
      {/* Top Brand & Header */}
      <div className="p-5 space-y-6">
        
        {/* Brand Logo - matching Nutri-Track style */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#132238] border border-[#34D399]/30 flex items-center justify-center text-[#34D399] shadow-lg shadow-[#10B981]/10">
            <Zap size={22} className="fill-current text-[#10B981]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-wider text-white">
                QUIZ-TQM
              </span>
            </div>
            <p className="text-[10px] text-[#94A3B8] font-bold tracking-widest uppercase">
              SPEED ENGINE OS
            </p>
          </div>
        </div>

        {/* Primary Action Button (Matches "QUICK LOG" in Nutri-Track) */}
        <button
          onClick={() => {
            if (firstQuizId) onStartQuickQuiz(firstQuizId);
            else setActiveTab('quizzes');
          }}
          className="btn-emerald-primary w-full text-sm font-bold tracking-wide"
        >
          <Zap size={16} className="fill-current" />
          START SPEED QUIZ
        </button>

        {/* Section: Administration */}
        {isAdmin && (
          <div className="space-y-1">
            <p className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase px-3 mb-2">
              ADMINISTRATION
            </p>
            <button
              onClick={() => setActiveTab('admin')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold ${
                activeTab === 'admin' ? 'nav-item-active' : 'nav-item-idle'
              }`}
            >
              <ShieldCheck size={16} />
              Admin Control Center
            </button>
          </div>
        )}

        {/* Section: Core Navigation */}
        <div className="space-y-1">
          <p className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase px-3 mb-2">
            CORE NAVIGATION
          </p>

          <button
            onClick={() => setActiveTab('quizzes')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold ${
              activeTab === 'quizzes' ? 'nav-item-active' : 'nav-item-idle'
            }`}
          >
            <LayoutDashboard size={16} />
            Quiz Arena Catalog
          </button>

          {!isAdmin && (
            <button
              onClick={() => setActiveTab('my-history')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold ${
                activeTab === 'my-history' ? 'nav-item-active' : 'nav-item-idle'
              }`}
            >
              <History size={16} />
              My Scores & History
            </button>
          )}

          <button
            onClick={() => {
              if (isAdmin) setActiveTab('admin');
              else setActiveTab('quizzes');
            }}
            className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold nav-item-idle"
          >
            <Award size={16} />
            TQM Response Benchmarks
          </button>
        </div>

        {/* Section: Databases & Logs */}
        <div className="space-y-1">
          <p className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase px-3 mb-2">
            QUALITY AUDITING
          </p>
          <div className="px-3.5 py-2 text-xs text-[#94A3B8] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
            SQLite WAL Indexed (B-Tree)
          </div>
          <div className="px-3.5 py-2 text-xs text-[#94A3B8] flex items-center gap-2">
            <Clock size={14} className="text-[#06B6D4]" />
            Response Time: &lt; 40ms SLA
          </div>
        </div>

      </div>

      {/* Bottom Profile & Audio Bar */}
      <div className="p-4 border-t border-[#1E2D47] bg-[#0A101A] space-y-3">
        
        {/* User Account Card */}
        <div className="flex items-center justify-between gap-2 bg-[#131E31] p-2.5 rounded-xl border border-[#1E2D47]">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
              isAdmin 
                ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30' 
                : 'bg-[#10B981]/20 text-[#34D399] border border-[#10B981]/30'
            }`}>
              {currentUser?.username ? currentUser.username[0].toUpperCase() : 'U'}
            </div>
            
            <div className="overflow-hidden">
              <select
                value={currentUser?.id || ''}
                onChange={(e) => onSwitchUser(parseInt(e.target.value, 10))}
                className="bg-transparent text-white text-xs font-bold focus:outline-none cursor-pointer w-full truncate"
              >
                {users.map((u) => (
                  <option key={u.id} value={u.id} className="bg-[#0C131F] text-white">
                    {u.username} ({u.role})
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-[#64748B] font-semibold uppercase">
                {currentUser?.role} MODE
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            {/* Audio Toggle */}
            <button
              onClick={onToggleSound}
              title={soundOn ? 'Mute SFX' : 'Enable SFX'}
              className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E2D47] transition-colors"
            >
              {soundOn ? <Volume2 size={15} className="text-[#34D399]" /> : <VolumeX size={15} className="text-[#F43F5E]" />}
            </button>

            {/* Add User */}
            <button
              onClick={() => setShowAddUser(true)}
              title="Add New Profile"
              className="p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-[#1E2D47] transition-colors"
            >
              <UserPlus size={15} />
            </button>
          </div>
        </div>

        <p className="text-[9px] text-[#64748B] text-center font-mono">
          BBAT104 TQM &bull; Piyush (2410301049)
        </p>

      </div>

      {/* New User Dialog */}
      {showAddUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="dashboard-card p-6 max-w-sm w-full border border-[#34D399]/40 space-y-4">
            <h3 className="text-base font-bold text-white">Create New Profile</h3>
            <p className="text-xs text-[#94A3B8]">Add student or admin account for role isolation testing.</p>

            {errorMsg && (
              <div className="p-2.5 rounded-lg bg-[#F43F5E]/20 border border-[#F43F5E]/40 text-[#F43F5E] text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1">Username</label>
                <input
                  type="text"
                  placeholder="e.g. rohit, sneha"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#080D14] border border-[#1E2D47] text-white text-xs focus:outline-none focus:border-[#34D399]"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#94A3B8] mb-1">Role</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setNewRole('STUDENT')}
                    className={`py-2 text-xs font-bold rounded-xl border ${
                      newRole === 'STUDENT'
                        ? 'bg-[#10B981]/20 border-[#34D399] text-[#34D399]'
                        : 'bg-[#080D14] border-[#1E2D47] text-[#94A3B8]'
                    }`}
                  >
                    Student
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewRole('ADMIN')}
                    className={`py-2 text-xs font-bold rounded-xl border ${
                      newRole === 'ADMIN'
                        ? 'bg-[#F59E0B]/20 border-[#F59E0B] text-[#F59E0B]'
                        : 'bg-[#080D14] border-[#1E2D47] text-[#94A3B8]'
                    }`}
                  >
                    Teacher / Admin
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddUser(false)}
                  className="px-3 py-2 rounded-xl text-xs text-[#94A3B8] hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-emerald-primary px-4 py-2 text-xs"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </aside>
  );
}
