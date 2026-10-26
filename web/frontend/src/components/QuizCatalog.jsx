import React, { useState } from 'react';
import { Search, Sparkles, Clock, CheckCircle2, Play, Flame, Layers, ArrowUpDown, Trash2 } from 'lucide-react';

export default function QuizCatalog({
  quizzes,
  categories,
  selectedCategory,
  onSelectCategory,
  searchQuery,
  onSearchChange,
  sortBy,
  onSortChange,
  searchLatency,
  withinSla,
  onStartQuiz,
  isAdmin,
  onDeleteQuiz
}) {
  const [hoveredCard, setHoveredCard] = useState(null);

  // Gradient generator for cards
  const cardGradients = [
    'from-rose-500 via-pink-600 to-purple-600',
    'from-blue-500 via-indigo-600 to-violet-700',
    'from-amber-400 via-orange-500 to-red-600',
    'from-emerald-400 via-teal-500 to-cyan-600',
    'from-purple-500 via-fuchsia-600 to-pink-600'
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 border border-purple-500/30 shadow-2xl"
           style={{
             background: 'linear-gradient(135deg, rgba(70, 23, 143, 0.9) 0%, rgba(20, 10, 50, 0.95) 100%)'
           }}>
        
        {/* Floating decoration dots */}
        <div className="absolute top-4 right-12 w-24 h-24 bg-amber-400/20 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute bottom-2 left-1/3 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-400/10 border border-purple-400/30 text-amber-300 text-xs font-semibold font-fun uppercase tracking-wider">
            <Sparkles size={14} className="text-amber-400" />
            Interactive Kahoot & Quizizz Gamified Arena
          </div>

          <h1 className="font-fun text-4xl sm:text-5xl font-extrabold text-white leading-tight">
            Level Up Your Speed & <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-orange-400 to-pink-400">Master Every Quiz</span>
          </h1>

          <p className="text-purple-200/90 text-sm sm:text-base font-medium max-w-2xl leading-relaxed">
            Fast, zero-latency assessments powered by in-memory caching and B-Tree indexes. Answer swiftly to score maximum multiplier points!
          </p>

          {/* SLA Benchmark Live Tag */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <div className={withinSla ? 'badge-sla-pass' : 'badge-sla-warn'}>
              <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
              Indexed Fast Search Latency: <strong className="font-mono">{searchLatency} ms</strong> (SLA &le; 40 ms)
            </div>
            <div className="text-xs text-purple-300/70 font-mono">
              Total Quizzes Available: <strong>{quizzes.length}</strong>
            </div>
          </div>
        </div>

      </div>

      {/* Search & Filter Bar */}
      <div className="glass-panel p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-purple-400" />
          <input
            type="text"
            placeholder="Search quiz title, topic, category..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-purple-950/60 border border-purple-500/30 text-white placeholder-purple-300/40 text-sm focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-500/20 font-medium transition-all"
          />
        </div>

        {/* Categories Pills */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto py-1 scrollbar-none">
          <button
            onClick={() => onSelectCategory('all')}
            className={`px-3.5 py-1.5 rounded-xl font-fun text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === 'all'
                ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/30'
                : 'bg-purple-900/40 text-purple-200 hover:text-white hover:bg-purple-800/50 border border-purple-500/20'
            }`}
          >
            🌟 All Quizzes
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onSelectCategory(cat)}
              className={`px-3.5 py-1.5 rounded-xl font-fun text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-purple-500 text-white shadow-md shadow-purple-500/40'
                  : 'bg-purple-900/40 text-purple-200 hover:text-white hover:bg-purple-800/50 border border-purple-500/20'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Sort Selector */}
        <div className="flex items-center gap-2 self-end md:self-center">
          <ArrowUpDown size={15} className="text-purple-400" />
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="bg-purple-950/70 border border-purple-500/30 text-purple-200 text-xs font-fun font-semibold py-2 px-3 rounded-xl focus:outline-none cursor-pointer"
          >
            <option value="id_asc" className="bg-slate-900 text-white">Default (ID)</option>
            <option value="title_asc" className="bg-slate-900 text-white">Title (A-Z)</option>
            <option value="title_desc" className="bg-slate-900 text-white">Title (Z-A)</option>
            <option value="duration_asc" className="bg-slate-900 text-white">Duration (Shortest)</option>
            <option value="duration_desc" className="bg-slate-900 text-white">Duration (Longest)</option>
            <option value="pass_score_asc" className="bg-slate-900 text-white">Pass Score (Low-High)</option>
            <option value="pass_score_desc" className="bg-slate-900 text-white">Pass Score (High-Low)</option>
          </select>
        </div>

      </div>

      {/* Quiz Cards Grid */}
      {quizzes.length === 0 ? (
        <div className="glass-panel p-12 text-center space-y-3">
          <div className="text-5xl">🔍</div>
          <h3 className="font-fun text-xl font-bold text-white">No quizzes match your filter</h3>
          <p className="text-purple-300 text-xs max-w-sm mx-auto">
            Try searching for another topic or clear the search field to view all active quizzes.
          </p>
        </div>
      ) : (
        <div className="quiz-grid">
          {quizzes.map((quiz, index) => {
            const gradient = cardGradients[index % cardGradients.length];
            const hasQuestions = quiz.question_count > 0;

            return (
              <div
                key={quiz.id}
                onMouseEnter={() => setHoveredCard(quiz.id)}
                onMouseLeave={() => setHoveredCard(null)}
                className="glass-panel rounded-3xl overflow-hidden flex flex-col justify-between transition-all duration-200 hover:-translate-y-1.5 hover:shadow-2xl hover:border-purple-400/50"
              >
                {/* Card Header Gradient with Category Badge */}
                <div className={`p-6 bg-gradient-to-r ${gradient} relative`}>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold font-fun uppercase tracking-wider bg-black/30 backdrop-blur-md text-white border border-white/20">
                      {quiz.category}
                    </span>
                    <span className="font-mono text-xs font-bold text-white/90 bg-black/20 px-2 py-0.5 rounded-md">
                      #{quiz.id}
                    </span>
                  </div>

                  <h3 className="font-fun text-2xl font-bold text-white drop-shadow-md line-clamp-2">
                    {quiz.title}
                  </h3>
                </div>

                {/* Card Content & Metrics */}
                <div className="p-6 space-y-5 flex-1 flex flex-col justify-between">
                  
                  <div className="grid grid-cols-3 gap-2 py-2 px-3 rounded-2xl bg-purple-950/40 border border-purple-500/20 text-center">
                    <div>
                      <p className="text-[10px] text-purple-300/80 uppercase font-bold tracking-wider">Questions</p>
                      <p className="font-fun text-lg font-bold text-white flex items-center justify-center gap-1">
                        <Layers size={14} className="text-amber-400" />
                        {quiz.question_count}
                      </p>
                    </div>

                    <div>
                      <p className="text-[10px] text-purple-300/80 uppercase font-bold tracking-wider">Time Limit</p>
                      <p className="font-fun text-lg font-bold text-white flex items-center justify-center gap-1">
                        <Clock size={14} className="text-cyan-400" />
                        {quiz.duration_minutes}m
                      </p>
                    </div>

                    <div>
                      <p className="text-[10px] text-purple-300/80 uppercase font-bold tracking-wider">Pass Mark</p>
                      <p className="font-fun text-lg font-bold text-white flex items-center justify-center gap-1">
                        <CheckCircle2 size={14} className="text-emerald-400" />
                        {quiz.passing_score}%
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2 pt-2">
                    {hasQuestions ? (
                      <button
                        onClick={() => onStartQuiz(quiz.id)}
                        className="btn-push btn-push-green w-full py-3.5 text-base gap-2"
                      >
                        <Play size={18} fill="currentColor" />
                        PLAY SOLO
                      </button>
                    ) : (
                      <div className="py-3 px-4 rounded-xl bg-purple-900/30 border border-purple-500/20 text-center text-xs text-purple-300 font-medium">
                        ⚠️ No questions added yet
                      </div>
                    )}

                    {/* Admin delete shortcut */}
                    {isAdmin && (
                      <button
                        onClick={() => onDeleteQuiz(quiz.id)}
                        className="w-full py-1.5 rounded-xl text-xs font-fun font-semibold text-rose-300 hover:text-rose-100 hover:bg-rose-500/20 transition-colors flex items-center justify-center gap-1.5"
                      >
                        <Trash2 size={13} />
                        Delete Quiz
                      </button>
                    )}
                  </div>

                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
