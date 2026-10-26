import React, { useState, useEffect, useRef } from 'react';
import { Clock, Zap, Flame, Award, ArrowRight, X, AlertCircle } from 'lucide-react';
import { SoundFX } from '../utils/audio';
import confetti from 'canvas-confetti';

export default function KahootPlayer({
  quizSession,
  onCompleteQuiz,
  onCancelQuiz
}) {
  const { quiz, questions } = quizSession;

  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [selectedOption, setSelectedOption] = useState(null);
  const [isAnswerRevealed, setIsAnswerRevealed] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [feedback, setFeedback] = useState(null);

  // Per-question timer (e.g. 20 seconds per question like Kahoot, or calculated from quiz duration)
  const questionTimeLimit = Math.max(10, Math.min(30, Math.floor((quiz.duration_minutes * 60) / questions.length)));
  const [timeLeft, setTimeLeft] = useState(questionTimeLimit);

  // Overall stopwatch
  const overallStartTime = useRef(Date.now());
  const questionStartTime = useRef(Date.now());

  const currentQ = questions[currentIndex];

  // Reset timer on question change
  useEffect(() => {
    setTimeLeft(questionTimeLimit);
    setSelectedOption(null);
    setIsAnswerRevealed(false);
    setFeedback(null);
    questionStartTime.current = Date.now();
  }, [currentIndex, questionTimeLimit]);

  // Timer countdown hook
  useEffect(() => {
    if (isAnswerRevealed) return;

    if (timeLeft <= 0) {
      handleTimeOut();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        if (prev <= 5) {
          SoundFX.urgentTick();
        } else {
          SoundFX.tick();
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, isAnswerRevealed]);

  // Handle timeout when user fails to pick in time
  const handleTimeOut = () => {
    setIsAnswerRevealed(true);
    SoundFX.wrong();
    setStreak(0);
    setUserAnswers((prev) => ({ ...prev, [currentQ.id]: 'NONE' }));
    setFeedback({
      type: 'timeout',
      text: "Time's Up! ⏰",
      subtext: `The correct answer was (${currentQ.correct_option})`,
      points: 0
    });
  };

  // Handle option selection
  const handleSelectOption = (optionKey) => {
    if (isAnswerRevealed) return;

    const elapsedSeconds = Math.max(0.1, (Date.now() - questionStartTime.current) / 1000);
    setSelectedOption(optionKey);
    setIsAnswerRevealed(true);

    const isCorrect = optionKey.toUpperCase() === currentQ.correct_option.toUpperCase();
    const updatedAnswers = { ...userAnswers, [currentQ.id]: optionKey };
    setUserAnswers(updatedAnswers);

    if (isCorrect) {
      // Speed multiplier formula (Kahoot-inspired: 1000 base minus elapsed fraction)
      const speedRatio = Math.max(0, (questionTimeLimit - elapsedSeconds) / questionTimeLimit);
      const basePoints = 500;
      const speedBonus = Math.round(500 * speedRatio);
      const newStreak = streak + 1;
      const streakMultiplier = newStreak >= 3 ? 1.5 : newStreak >= 2 ? 1.2 : 1.0;
      const totalQuestionPoints = Math.round((basePoints + speedBonus) * streakMultiplier);

      setScore((prev) => prev + totalQuestionPoints);
      setStreak(newStreak);
      if (newStreak > bestStreak) setBestStreak(newStreak);

      SoundFX.correct();

      if (newStreak >= 2) {
        SoundFX.streak();
        try {
          confetti({
            particleCount: 40,
            spread: 60,
            origin: { y: 0.6 }
          });
        } catch (e) {}
      }

      setFeedback({
        type: 'correct',
        text: newStreak >= 3 ? 'SUPER STREAK! 🔥' : speedRatio > 0.7 ? 'GENIUS SPEED! ⚡' : 'CORRECT! ✨',
        subtext: `+${totalQuestionPoints} PTS (Base: ${basePoints} + Speed: ${speedBonus}${newStreak >= 2 ? ` x${streakMultiplier}` : ''})`,
        points: totalQuestionPoints
      });
    } else {
      SoundFX.wrong();
      setStreak(0);
      setFeedback({
        type: 'wrong',
        text: 'INCORRECT! 💡',
        subtext: `Correct answer was option (${currentQ.correct_option})`,
        points: 0
      });
    }
  };

  // Keyboard navigation (1, 2, 3, 4 or A, B, C, D)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (isAnswerRevealed) {
        if (e.key === 'Enter' || e.key === ' ') {
          handleNextQuestion();
        }
        return;
      }
      const key = e.key.toUpperCase();
      if (key === '1' || key === 'A') handleSelectOption('A');
      if (key === '2' || key === 'B') handleSelectOption('B');
      if (key === '3' || key === 'C') handleSelectOption('C');
      if (key === '4' || key === 'D') handleSelectOption('D');
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isAnswerRevealed, currentQ, userAnswers, streak, score]);

  const handleNextQuestion = () => {
    if (currentIndex + 1 < questions.length) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      // Quiz completed!
      const totalDurationSec = Math.round((Date.now() - overallStartTime.current) / 1000);
      onCompleteQuiz(userAnswers, score, totalDurationSec, bestStreak);
    }
  };

  // Timer visual helpers
  const timerPercentage = (timeLeft / questionTimeLimit) * 100;
  const isUrgent = timeLeft <= 5;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in zoom-in-95 duration-200">
      
      {/* Top Game Bar HUD */}
      <div className="glass-panel p-4 flex items-center justify-between gap-4">
        
        {/* Left: Question Counter & Exit */}
        <div className="flex items-center gap-3">
          <button
            onClick={onCancelQuiz}
            title="Leave Quiz"
            className="w-8 h-8 rounded-xl flex items-center justify-center bg-purple-900/40 text-purple-300 hover:text-white hover:bg-rose-500/20 transition-all border border-purple-500/20"
          >
            <X size={16} />
          </button>
          <div>
            <p className="text-[11px] font-bold text-purple-300 uppercase tracking-wider font-fun">
              {quiz.title}
            </p>
            <p className="font-fun text-base font-bold text-white">
              Question {currentIndex + 1} <span className="text-purple-400">/ {questions.length}</span>
            </p>
          </div>
        </div>

        {/* Center: Circular / Numeric Timer */}
        <div className="flex items-center gap-2">
          <div className={`px-4 py-1.5 rounded-2xl flex items-center gap-2 font-mono text-xl font-black border transition-all ${
            isUrgent
              ? 'bg-rose-500/30 text-rose-300 border-rose-500/50 animate-pulse scale-105'
              : 'bg-purple-950/70 text-amber-300 border-purple-500/30'
          }`}>
            <Clock size={18} className={isUrgent ? 'text-rose-400 animate-spin' : 'text-amber-400'} />
            {timeLeft}s
          </div>
        </div>

        {/* Right: Score & Streak */}
        <div className="flex items-center gap-4">
          {streak >= 2 && (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-xl bg-orange-500/20 border border-orange-500/40 text-orange-300 font-fun text-xs font-bold flame-active">
              <Flame size={15} className="text-orange-400 fill-orange-400" />
              {streak}x Combo!
            </div>
          )}

          <div className="text-right">
            <p className="text-[10px] font-bold text-purple-300 uppercase tracking-wider font-fun">Score</p>
            <p className="font-fun text-xl font-extrabold text-amber-400 flex items-center gap-1">
              <Zap size={16} fill="currentColor" />
              {score.toLocaleString()}
            </p>
          </div>
        </div>

      </div>

      {/* Progress & Time Bar */}
      <div className="timer-track">
        <div
          className="timer-fill"
          style={{
            width: `${timerPercentage}%`,
            backgroundColor: isUrgent ? '#E21B3C' : timeLeft <= 10 ? '#FFA600' : '#10B981'
          }}
        />
      </div>

      {/* Center Question Card */}
      <div className="glass-panel-elevated p-8 text-center space-y-4 min-h-[160px] flex flex-col justify-center relative overflow-hidden">
        
        {/* Subtle background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-32 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <p className="text-xs font-mono font-semibold text-purple-300/80 uppercase tracking-widest">
          {currentQ.marks || 1} Point Question
        </p>

        <h2 className="font-fun text-2xl sm:text-3xl font-bold text-white max-w-3xl mx-auto leading-relaxed drop-shadow-md">
          {currentQ.question_text}
        </h2>
      </div>

      {/* 4 Iconic Kahoot Option Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Option A - Red Triangle */}
        <button
          onClick={() => handleSelectOption('A')}
          disabled={isAnswerRevealed}
          className={`kahoot-card card-a ${
            isAnswerRevealed && currentQ.correct_option === 'A'
              ? 'ring-4 ring-white shadow-2xl scale-[1.02]'
              : isAnswerRevealed && selectedOption === 'A'
              ? 'opacity-60 grayscale-[0.4]'
              : isAnswerRevealed
              ? 'opacity-30'
              : ''
          }`}
        >
          <div className="shape-badge">▲</div>
          <div className="flex-1">
            <span className="text-xs text-white/70 block uppercase font-mono">Option A</span>
            <span>{currentQ.option_a}</span>
          </div>
        </button>

        {/* Option B - Blue Diamond */}
        <button
          onClick={() => handleSelectOption('B')}
          disabled={isAnswerRevealed}
          className={`kahoot-card card-b ${
            isAnswerRevealed && currentQ.correct_option === 'B'
              ? 'ring-4 ring-white shadow-2xl scale-[1.02]'
              : isAnswerRevealed && selectedOption === 'B'
              ? 'opacity-60 grayscale-[0.4]'
              : isAnswerRevealed
              ? 'opacity-30'
              : ''
          }`}
        >
          <div className="shape-badge">◆</div>
          <div className="flex-1">
            <span className="text-xs text-white/70 block uppercase font-mono">Option B</span>
            <span>{currentQ.option_b}</span>
          </div>
        </button>

        {/* Option C - Yellow Circle */}
        <button
          onClick={() => handleSelectOption('C')}
          disabled={isAnswerRevealed}
          className={`kahoot-card card-c ${
            isAnswerRevealed && currentQ.correct_option === 'C'
              ? 'ring-4 ring-white shadow-2xl scale-[1.02]'
              : isAnswerRevealed && selectedOption === 'C'
              ? 'opacity-60 grayscale-[0.4]'
              : isAnswerRevealed
              ? 'opacity-30'
              : ''
          }`}
        >
          <div className="shape-badge">●</div>
          <div className="flex-1">
            <span className="text-xs text-black/60 block uppercase font-mono">Option C</span>
            <span>{currentQ.option_c}</span>
          </div>
        </button>

        {/* Option D - Green Square */}
        <button
          onClick={() => handleSelectOption('D')}
          disabled={isAnswerRevealed}
          className={`kahoot-card card-d ${
            isAnswerRevealed && currentQ.correct_option === 'D'
              ? 'ring-4 ring-white shadow-2xl scale-[1.02]'
              : isAnswerRevealed && selectedOption === 'D'
              ? 'opacity-60 grayscale-[0.4]'
              : isAnswerRevealed
              ? 'opacity-30'
              : ''
          }`}
        >
          <div className="shape-badge">■</div>
          <div className="flex-1">
            <span className="text-xs text-white/70 block uppercase font-mono">Option D</span>
            <span>{currentQ.option_d}</span>
          </div>
        </button>

      </div>

      {/* Reveal Overlay & Next Button */}
      {isAnswerRevealed && feedback && (
        <div className="glass-panel p-5 flex flex-col sm:flex-row items-center justify-between gap-4 border border-purple-400/40 animate-in fade-in slide-in-from-bottom-4 duration-200">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl font-bold shadow-lg ${
              feedback.type === 'correct'
                ? 'bg-emerald-500 text-white shadow-emerald-500/40'
                : 'bg-rose-500 text-white shadow-rose-500/40'
            }`}>
              {feedback.type === 'correct' ? '✓' : '✕'}
            </div>

            <div>
              <h4 className="font-fun text-xl font-bold text-white flex items-center gap-2">
                {feedback.text}
              </h4>
              <p className="text-xs text-purple-200 font-medium">
                {feedback.subtext}
              </p>
            </div>
          </div>

          <button
            onClick={handleNextQuestion}
            className="btn-push btn-push-purple px-8 py-3.5 text-base gap-2 w-full sm:w-auto shadow-xl"
            autoFocus
          >
            {currentIndex + 1 < questions.length ? 'Next Question' : 'View Results'}
            <ArrowRight size={18} />
          </button>
        </div>
      )}

      {/* Footer shortcut helper */}
      <div className="text-center text-xs text-purple-300/60 font-mono">
        💡 Tip: You can press keys <kbd className="px-1.5 py-0.5 rounded bg-purple-900/60 border border-purple-400/30 text-white">1</kbd>, <kbd className="px-1.5 py-0.5 rounded bg-purple-900/60 border border-purple-400/30 text-white">2</kbd>, <kbd className="px-1.5 py-0.5 rounded bg-purple-900/60 border border-purple-400/30 text-white">3</kbd>, <kbd className="px-1.5 py-0.5 rounded bg-purple-900/60 border border-purple-400/30 text-white">4</kbd> or <kbd className="px-1.5 py-0.5 rounded bg-purple-900/60 border border-purple-400/30 text-white">Enter</kbd> to answer instantly.
      </div>

    </div>
  );
}
