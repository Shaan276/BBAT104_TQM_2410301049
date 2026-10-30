import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import QuizCatalog from './components/QuizCatalog';
import KahootPlayer from './components/KahootPlayer';
import PodiumResults from './components/PodiumResults';
import StudentHistory from './components/StudentHistory';
import AdminDashboard from './components/AdminDashboard';
import { SoundFX } from './utils/audio';

export default function App() {
  // Navigation & Role State
  const [activeTab, setActiveTab] = useState('quizzes'); // 'quizzes' | 'my-history' | 'admin'
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [soundOn, setSoundOn] = useState(true);

  // Catalog State
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('id_asc');
  const [searchLatency, setSearchLatency] = useState(0);
  const [withinSla, setWithinSla] = useState(true);

  // Game Engine State
  const [gameState, setGameState] = useState('LOBBY'); // 'LOBBY' | 'PLAYING' | 'RESULTS'
  const [activeQuizSession, setActiveQuizSession] = useState(null);
  const [submissionSummary, setSubmissionSummary] = useState(null);
  const [gamifiedScore, setGamifiedScore] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [totalTimeSec, setTotalTimeSec] = useState(0);

  // 1. Initial Load: Users & Categories
  useEffect(() => {
    fetchUsers();
    fetchCategories();
  }, []);

  // Fetch Users
  const fetchUsers = async () => {
    try {
      const res = await fetch('/api/users');
      const data = await res.json();
      if (data.success && data.users.length > 0) {
        setUsers(data.users);
        if (!currentUser) {
          const student = data.users.find((u) => u.username === 'piyush') || data.users[0];
          setCurrentUser(student);
        }
      }
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  // Fetch Categories
  const fetchCategories = async () => {
    try {
      const res = await fetch('/api/quizzes/categories');
      const data = await res.json();
      if (data.success) {
        setCategories(data.categories);
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  // Fetch Quizzes Catalog (with debounced search)
  const fetchQuizzes = async (query = searchQuery, category = selectedCategory, sort = sortBy) => {
    try {
      const params = new URLSearchParams();
      if (query) params.append('query', query);
      if (category && category !== 'all') params.append('category', category);
      if (sort) params.append('sort', sort);

      const res = await fetch(`/api/quizzes?${params.toString()}`);
      const data = await res.json();
      if (data.success) {
        setQuizzes(data.quizzes);
        setSearchLatency(data.latencyMs);
        setWithinSla(data.withinSla);
      }
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
    }
  };

  // Trigger search on filter change
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchQuizzes(searchQuery, selectedCategory, sortBy);
    }, 150);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedCategory, sortBy]);

  // Switch User
  const handleSwitchUser = (userId) => {
    const user = users.find((u) => u.id === userId);
    if (user) {
      setCurrentUser(user);
      if (user.role === 'ADMIN') {
        setActiveTab('admin');
      } else {
        if (activeTab === 'admin') setActiveTab('quizzes');
      }
    }
  };

  // Create User
  const handleCreateUser = async (username, role) => {
    try {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, role })
      });
      const data = await res.json();
      if (data.success) {
        await fetchUsers();
        setCurrentUser(data.user);
        if (data.user.role === 'ADMIN') setActiveTab('admin');
        return { success: true };
      }
      return { success: false, error: data.error };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Toggle Sound FX
  const handleToggleSound = () => {
    const newSoundState = SoundFX.toggle();
    setSoundOn(newSoundState);
  };

  // Start Quiz (Kahoot Player)
  const handleStartQuiz = async (quizId) => {
    try {
      const res = await fetch(`/api/quizzes/${quizId}`);
      const data = await res.json();
      if (data.success) {
        if (!data.questions || data.questions.length === 0) {
          alert('This quiz currently has no questions. Please add questions first!');
          return;
        }
        setActiveQuizSession(data);
        setGameState('PLAYING');
      } else {
        alert(data.error || 'Failed to load quiz');
      }
    } catch (err) {
      console.error('Error starting quiz:', err);
    }
  };

  // Complete Quiz & Atomic Grading Submission (FR-04)
  const handleCompleteQuiz = async (answers, finalGameScore, durationSec, streakCount) => {
    if (!activeQuizSession || !currentUser) return;

    try {
      const res = await fetch(`/api/quizzes/${activeQuizSession.quiz.id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          answers: answers,
          time_taken_seconds: durationSec
        })
      });
      const data = await res.json();
      if (data.success) {
        setSubmissionSummary(data.summary);
        setGamifiedScore(finalGameScore);
        setBestStreak(streakCount);
        setTotalTimeSec(durationSec);
        setGameState('RESULTS');
      } else {
        alert(data.error || 'Failed to submit attempt');
        setGameState('LOBBY');
      }
    } catch (err) {
      console.error('Error completing quiz:', err);
      setGameState('LOBBY');
    }
  };

  // Delete Quiz
  const handleDeleteQuiz = async (quizId) => {
    if (!window.confirm(`Are you sure you want to delete quiz #${quizId}?`)) return;
    try {
      const res = await fetch(`/api/quizzes/${quizId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        fetchQuizzes();
        fetchCategories();
      } else {
        alert(data.error || 'Failed to delete quiz');
      }
    } catch (err) {
      console.error('Error deleting quiz:', err);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#080D14] text-white selection:bg-[#10B981] selection:text-[#042F2E]">
      
      {/* Sleek Sidebar Navigation - Matching Nutri-Track Layout */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setGameState('LOBBY');
        }}
        currentUser={currentUser}
        users={users}
        onSwitchUser={handleSwitchUser}
        onCreateUser={handleCreateUser}
        soundOn={soundOn}
        onToggleSound={handleToggleSound}
        onStartQuickQuiz={handleStartQuiz}
        firstQuizId={quizzes.length > 0 ? quizzes[0].id : null}
      />

      {/* Main App Content Viewport */}
      <main className="flex-1 p-6 lg:p-8 overflow-y-auto max-w-[1400px]">
        
        {/* GAME STATE: PLAYING */}
        {gameState === 'PLAYING' && activeQuizSession && (
          <KahootPlayer
            quizSession={activeQuizSession}
            onCompleteQuiz={handleCompleteQuiz}
            onCancelQuiz={() => setGameState('LOBBY')}
          />
        )}

        {/* GAME STATE: RESULTS & PODIUM */}
        {gameState === 'RESULTS' && submissionSummary && (
          <PodiumResults
            summary={submissionSummary}
            quizSession={activeQuizSession}
            currentUser={currentUser}
            gamifiedScore={gamifiedScore}
            bestStreak={bestStreak}
            totalTimeSec={totalTimeSec}
            onPlayAgain={() => handleStartQuiz(activeQuizSession.quiz.id)}
            onBackToLobby={() => setGameState('LOBBY')}
          />
        )}

        {/* GAME STATE: LOBBY TABS */}
        {gameState === 'LOBBY' && (
          <>
            {/* Tab 1: Quizzes Catalog */}
            {activeTab === 'quizzes' && (
              <QuizCatalog
                quizzes={quizzes}
                categories={categories}
                selectedCategory={selectedCategory}
                onSelectCategory={setSelectedCategory}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                sortBy={sortBy}
                onSortChange={setSortBy}
                searchLatency={searchLatency}
                withinSla={withinSla}
                onStartQuiz={handleStartQuiz}
                isAdmin={currentUser?.role === 'ADMIN'}
                onDeleteQuiz={handleDeleteQuiz}
                currentUser={currentUser}
              />
            )}

            {/* Tab 2: Student Personal History */}
            {activeTab === 'my-history' && (
              <StudentHistory currentUser={currentUser} />
            )}

            {/* Tab 3: Admin / Teacher Studio */}
            {activeTab === 'admin' && (
              <AdminDashboard
                onQuizCreated={() => {
                  fetchQuizzes();
                  fetchCategories();
                }}
              />
            )}
          </>
        )}

      </main>

    </div>
  );
}
