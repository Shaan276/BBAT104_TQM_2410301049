import React, { useEffect, useState } from 'react';
import { Award, Zap, Clock, CheckCircle2, XCircle, RotateCcw, Home, Sparkles, Flame, ChevronDown, ChevronUp } from 'lucide-react';
import confetti from 'canvas-confetti';
import { SoundFX } from '../utils/audio';

export default function PodiumResults({
  summary,
  quizSession,
  currentUser,
  gamifiedScore,
  bestStreak,
  totalTimeSec,
  onPlayAgain,
  onBackToLobby
}) {
  const [showReview, setShowReview] = useState(false);

  useEffect(() => {
    SoundFX.victory();

    // Trigger double confetti blast
    try {
      const end = Date.now() + 2 * 1000;
      const colors = ['#F59E0B', '#10B981', '#E21B3C', '#1368CE', '#8854C0'];

      (function frame() {
        confetti({
          particleCount: 5,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors
        });
        confetti({
          particleCount: 5,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors
        });

        if (Date.now() < end) {
          requestAnimationFrame(frame);
        }
      })();
    } catch (e) {}
  }, []);

  const isPassed = summary.status === 'PASSED';
  const accuracy = summary.scorePercentage;

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in zoom-in-95 duration-300">
      
      {/* Celebration Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-400/10 border border-amber-400/30 text-amber-300 font-fun text-sm font-bold">
          <Sparkles size={16} />
          Quiz Completed!
        </div>

        <h1 className="font-fun text-4xl sm:text-5xl font-extrabold text-white">
          {isPassed ? '🏆 Brilliant Performance!' : '💪 Good Effort! Keep Going!'}
        </h1>
        <p className="text-purple-300 text-sm max-w-md mx-auto">
          {quizSession?.quiz?.title} &bull; Passing Score: {summary.passingScore}%
        </p>
      </div>

      {/* 3D Olympic Podium */}
      <div className="podium-container">
        
        {/* 2nd Place (Silver) */}
        <div className="podium-step">
          <div className="w-12 h-12 rounded-full bg-slate-300 border-2 border-white flex items-center justify-center text-slate-800 font-fun font-bold text-lg mb-2 shadow-lg">
            🥈
          </div>
          <p className="font-fun text-xs font-bold text-slate-300 mb-1">Runner Up</p>
          <div className="podium-block podium-2nd">
            <span className="font-fun text-3xl font-extrabold text-white/90">2</span>
          </div>
        </div>

        {/* 1st Place (Gold) - Current Player */}
        <div className="podium-step">
          <div className="relative mb-2">
            <div className="w-16 h-16 rounded-full bg-amber-400 border-4 border-amber-200 flex items-center justify-center text-slate-900 font-fun font-black text-2xl shadow-xl shadow-amber-500/40">
              👑
            </div>
            {isPassed && (
              <span className="absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full bg-emerald-500 text-white text-[10px] font-bold">
                PASS
              </span>
            )}
          </div>
          <p className="font-fun text-sm font-bold text-amber-300 mb-1">
            {currentUser?.username || 'Player'}
          </p>
          <p className="font-mono text-xs font-extrabold text-white mb-1">
            {gamifiedScore.toLocaleString()} pts
          </p>
          <div className="podium-block podium-1st">
            <span className="font-fun text-5xl font-black text-amber-950">1</span>
          </div>
        </div>

        {/* 3rd Place (Bronze) */}
        <div className="podium-step">
          <div className="w-12 h-12 rounded-full bg-amber-700 border-2 border-amber-400 flex items-center justify-center text-amber-200 font-fun font-bold text-lg mb-2 shadow-lg">
            🥉
          </div>
          <p className="font-fun text-xs font-bold text-amber-400 mb-1">Contender</p>
          <div className="podium-block podium-3rd">
            <span className="font-fun text-3xl font-extrabold text-white/80">3</span>
          </div>
        </div>

      </div>

      {/* Stats Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        {/* Card 1: Score & Pass Status */}
        <div className="glass-panel p-4 rounded-2xl text-center space-y-1">
          <p className="text-[10px] uppercase font-bold tracking-wider text-purple-300">Accuracy</p>
          <p className={`font-fun text-2xl font-black ${isPassed ? 'text-emerald-400' : 'text-rose-400'}`}>
            {accuracy}%
          </p>
          <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${
            isPassed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
          }`}>
            {summary.correctAnswers} / {summary.totalQuestions} Correct
          </span>
        </div>

        {/* Card 2: Kahoot Game Points */}
        <div className="glass-panel p-4 rounded-2xl text-center space-y-1">
          <p className="text-[10px] uppercase font-bold tracking-wider text-purple-300">Game Points</p>
          <p className="font-fun text-2xl font-black text-amber-400 flex items-center justify-center gap-1">
            <Zap size={18} fill="currentColor" />
            {gamifiedScore.toLocaleString()}
          </p>
          <span className="text-[10px] font-medium text-purple-300/80">
            Speed Multiplier Points
          </span>
        </div>

        {/* Card 3: Best Streak */}
        <div className="glass-panel p-4 rounded-2xl text-center space-y-1">
          <p className="text-[10px] uppercase font-bold tracking-wider text-purple-300">Best Streak</p>
          <p className="font-fun text-2xl font-black text-orange-400 flex items-center justify-center gap-1">
            <Flame size={18} fill="currentColor" />
            {bestStreak}x
          </p>
          <span className="text-[10px] font-medium text-purple-300/80">
            Consecutive Hits
          </span>
        </div>

        {/* Card 4: TQM Atomic Latency */}
        <div className="glass-panel p-4 rounded-2xl text-center space-y-1">
          <p className="text-[10px] uppercase font-bold tracking-wider text-purple-300">Commit Latency</p>
          <p className="font-mono text-2xl font-black text-cyan-300">
            {summary.latencyMs} ms
          </p>
          <span className="badge-sla-pass text-[10px]">
            SLA &le; {summary.slaLimitMs} ms
          </span>
        </div>

      </div>

      {/* Question Review Section (Collapsible) */}
      <div className="glass-panel rounded-3xl overflow-hidden">
        <button
          onClick={() => setShowReview(!showReview)}
          className="w-full p-5 flex items-center justify-between text-left hover:bg-purple-900/20 transition-colors"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-400" />
            <span className="font-fun text-lg font-bold text-white">Review Detailed Answer Breakdown</span>
          </div>
          {showReview ? <ChevronUp size={18} className="text-purple-300" /> : <ChevronDown size={18} className="text-purple-300" />}
        </button>

        {showReview && (
          <div className="p-5 pt-0 space-y-3 border-t border-purple-500/20">
            {quizSession.questions.map((q, idx) => {
              const item = summary.itemDetails?.find((d) => d.questionId === q.id);
              const userPick = item?.selected || 'NONE';
              const isCorrect = item?.isCorrect === 1;

              return (
                <div
                  key={q.id}
                  className={`p-4 rounded-2xl border transition-all ${
                    isCorrect
                      ? 'bg-emerald-950/20 border-emerald-500/30'
                      : 'bg-rose-950/20 border-rose-500/30'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <p className="font-fun text-sm font-bold text-white">
                      Q{idx + 1}: {q.question_text}
                    </p>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold font-fun ${
                      isCorrect ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                    }`}>
                      {isCorrect ? '✓ Correct' : '✕ Wrong'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-medium">
                    <div className="p-2 rounded-xl bg-purple-950/40 text-purple-200">
                      Your Choice: <strong className={isCorrect ? 'text-emerald-300' : 'text-rose-300'}>Option {userPick}</strong>
                    </div>
                    <div className="p-2 rounded-xl bg-purple-950/40 text-purple-200">
                      Correct Key: <strong className="text-emerald-300">Option {q.correct_option}</strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
        <button
          onClick={onPlayAgain}
          className="btn-push btn-push-green px-8 py-4 text-base gap-2 w-full sm:w-auto shadow-xl"
        >
          <RotateCcw size={18} />
          Play Quiz Again
        </button>

        <button
          onClick={onBackToLobby}
          className="btn-push btn-push-purple px-8 py-4 text-base gap-2 w-full sm:w-auto shadow-xl"
        >
          <Home size={18} />
          Back to Quiz Arena
        </button>
      </div>

    </div>
  );
}
