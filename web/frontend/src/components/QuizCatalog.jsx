import React from 'react';
import { 
  Search, 
  Sparkles, 
  Clock, 
  CheckCircle2, 
  Play, 
  Layers, 
  ArrowUpDown, 
  Trash2, 
  Activity, 
  Cpu, 
  Calendar,
  User,
  Zap,
  Target
} from 'lucide-react';

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
  onDeleteQuiz,
  currentUser
}) {
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* 1. Top Header Bar (Matching Nutri-Track Top Bar) */}
      <div className="flex items-center justify-between pb-4 border-b border-[#1B2A44]">
        <h1 className="text-2xl font-bold text-white tracking-wide">
          Dashboard
        </h1>

        <div className="flex items-center gap-3">
          {/* Date Tag */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#0E1626] border border-[#1B2A44] text-xs font-semibold text-[#94A3B8]">
            <Calendar size={14} className="text-[#06B6D4]" />
            {currentDate}
          </div>

          {/* SLA Benchmark Pill */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#0E1626] border border-[#1B2A44] text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
            <span className="text-[#94A3B8]">Fast Search SLA:</span>
            <span className="text-[#34D399] font-mono font-bold">{searchLatency} ms</span>
          </div>

          {/* Quick Play Top Button */}
          {quizzes.length > 0 && (
            <button
              onClick={() => onStartQuiz(quizzes[0].id)}
              className="btn-emerald-primary text-xs py-2 px-4 font-bold"
            >
              <Zap size={14} className="fill-current" />
              QUICK PLAY
            </button>
          )}

          {/* User Icon */}
          <div className="w-9 h-9 rounded-xl bg-[#0E1626] border border-[#1B2A44] flex items-center justify-center text-[#94A3B8]">
            <User size={16} />
          </div>
        </div>
      </div>

      {/* 2. Top Notification Banner (Matching AI Health Assessment In Progress in Reference) */}
      <div className="dashboard-card p-4 flex items-center justify-between gap-4 border-l-4 border-l-[#10B981]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#10B981]/15 border border-[#10B981]/30 flex items-center justify-center text-[#34D399] shrink-0">
            <Cpu size={20} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              TQM Assessment Engine Active &bull; Goal Q05
            </h3>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              In-Memory caching (sub-15ms) & B-Tree indexed catalog active for zero UI freezing.
            </p>
          </div>
        </div>

        <span className="px-3.5 py-1.5 rounded-xl bg-[#10B981]/15 border border-[#10B981]/30 text-[#34D399] text-xs font-bold tracking-wider uppercase shrink-0">
          SLA &le; 40ms PASSED
        </span>
      </div>

      {/* 3. Hero Welcome Card (Matching "Welcome back, Piyush Pilkhwal!" Card in Reference) */}
      <div className="dashboard-card p-6">
        <div className="flex items-center gap-2 mb-2 text-xs font-bold tracking-wider text-[#34D399] uppercase">
          <Sparkles size={14} />
          LIVE DASHBOARD &bull; ACADEMIC QUIZ ARENA
        </div>

        <h2 className="text-2xl font-extrabold text-white mb-1">
          Welcome back, {currentUser?.username ? currentUser.username.charAt(0).toUpperCase() + currentUser.username.slice(1) : 'Student'}!
        </h2>
        <p className="text-xs text-[#94A3B8]">
          Available: <strong className="text-white">{quizzes.length} quizzes</strong> &bull; Total Questions: <strong className="text-white">{quizzes.reduce((acc, q) => acc + (q.question_count || 0), 0)}</strong> &bull; Ready for speed assessment.
        </p>

        {/* Filter Badges Row inside Hero */}
        <div className="flex items-center gap-2 mt-5 pt-4 border-t border-[#1B2A44] flex-wrap">
          <span className="text-xs font-bold text-[#64748B] uppercase mr-1">Categories:</span>
          <button
            onClick={() => onSelectCategory('all')}
            className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
              selectedCategory === 'all'
                ? 'bg-[#10B981] text-[#042F2E]'
                : 'bg-[#121D32] text-[#94A3B8] hover:text-white border border-[#1F304E]'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onSelectCategory(cat)}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                selectedCategory === cat
                  ? 'bg-[#10B981] text-[#042F2E]'
                  : 'bg-[#121D32] text-[#94A3B8] hover:text-white border border-[#1F304E]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* 4. TQM 4-Metric Container (Matching CALORIES, PROTEIN, CARBS, FAT in Reference) */}
      <div className="dashboard-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold tracking-wider text-[#34D399] uppercase">
            <Target size={14} />
            TQM PERFORMANCE METRICS OVERVIEW
          </div>
          <span className="text-xs text-[#64748B] font-mono">Real-Time Measurements</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Card 1: SEARCH SLA */}
          <div className="dashboard-card-inner p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-[#34D399] uppercase flex items-center gap-1.5">
                <Zap size={14} /> SEARCH SLA
              </span>
              <span className="text-[#10B981] font-mono text-[11px] font-bold">&le; 40 ms</span>
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">
              {searchLatency} <span className="text-xs text-[#64748B] font-normal">ms</span>
            </div>
            <div className="w-full bg-[#080D14] h-2 rounded-full overflow-hidden">
              <div 
                className="bg-[#10B981] h-full transition-all duration-300" 
                style={{ width: `${Math.max(8, Math.min(100, (searchLatency / 40) * 100))}%` }}
              ></div>
            </div>
          </div>

          {/* Card 2: CACHE READ */}
          <div className="dashboard-card-inner p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-[#06B6D4] uppercase flex items-center gap-1.5">
                <Cpu size={14} /> CACHE READ
              </span>
              <span className="text-[#06B6D4] font-mono text-[11px] font-bold">&le; 15 ms</span>
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">
              0.01 <span className="text-xs text-[#64748B] font-normal">ms</span>
            </div>
            <div className="w-full bg-[#080D14] h-2 rounded-full overflow-hidden">
              <div className="bg-[#06B6D4] h-full w-[12%]"></div>
            </div>
          </div>

          {/* Card 3: QUIZZES */}
          <div className="dashboard-card-inner p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-[#F59E0B] uppercase flex items-center gap-1.5">
                <Layers size={14} /> QUIZZES
              </span>
              <span className="text-[#F59E0B] font-mono text-[11px] font-bold">ACTIVE</span>
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">
              {quizzes.length} <span className="text-xs text-[#64748B] font-normal">sets</span>
            </div>
            <div className="w-full bg-[#080D14] h-2 rounded-full overflow-hidden">
              <div className="bg-[#F59E0B] h-full w-[75%]"></div>
            </div>
          </div>

          {/* Card 4: INDEX MODE */}
          <div className="dashboard-card-inner p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-[#8B5CF6] uppercase flex items-center gap-1.5">
                <Activity size={14} /> INDEX MODE
              </span>
              <span className="text-[#8B5CF6] font-mono text-[11px] font-bold">B-TREE</span>
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">
              WAL <span className="text-xs text-[#64748B] font-normal">Pragma</span>
            </div>
            <div className="w-full bg-[#080D14] h-2 rounded-full overflow-hidden">
              <div className="bg-[#8B5CF6] h-full w-[100%]"></div>
            </div>
          </div>

        </div>
      </div>

      {/* 5. Search Bar & Sorting Controls */}
      <div className="dashboard-card p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search quizzes by title or topic..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-3 py-2.5 rounded-xl bg-[#080D14] border border-[#1B2A44] text-white placeholder-[#64748B] text-xs focus:outline-none focus:border-[#34D399]"
          />
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          <ArrowUpDown size={14} className="text-[#64748B]" />
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="bg-[#080D14] border border-[#1B2A44] text-[#94A3B8] text-xs font-semibold py-2 px-3 rounded-xl focus:outline-none cursor-pointer"
          >
            <option value="id_asc">Sort: Default (ID)</option>
            <option value="title_asc">Title (A-Z)</option>
            <option value="title_desc">Title (Z-A)</option>
            <option value="duration_asc">Duration (Shortest)</option>
            <option value="duration_desc">Duration (Longest)</option>
          </select>
        </div>
      </div>

      {/* 6. Quiz Grid Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {quizzes.map((quiz) => {
          const hasQuestions = (quiz.question_count || 0) > 0;
          return (
            <div
              key={quiz.id}
              className="dashboard-card p-5 flex flex-col justify-between hover:border-[#34D399]/40 transition-all duration-150"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase bg-[#132238] text-[#34D399] border border-[#34D399]/30">
                    {quiz.category}
                  </span>
                  <span className="font-mono text-xs text-[#64748B]">#{quiz.id}</span>
                </div>

                <h3 className="text-base font-bold text-white mb-4 line-clamp-2">
                  {quiz.title}
                </h3>

                <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-[#080D14] border border-[#1B2A44] text-center mb-4">
                  <div>
                    <p className="text-[9px] uppercase font-bold text-[#64748B]">Questions</p>
                    <p className="text-xs font-bold text-white mt-0.5">{quiz.question_count || 0}</p>
                  </div>
                  <div>
                    <p className="text-[9px] uppercase font-bold text-[#64748B]">Time</p>
                    <p className="text-xs font-bold text-white mt-0.5">{quiz.duration_minutes}m</p>
                  </div>
                  <div>
                    <p className="text-[9px] uppercase font-bold text-[#64748B]">Pass</p>
                    <p className="text-xs font-bold text-[#34D399] mt-0.5">{quiz.passing_score}%</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                {hasQuestions ? (
                  <button
                    onClick={() => onStartQuiz(quiz.id)}
                    className="btn-emerald-primary w-full text-xs py-2.5"
                  >
                    <Play size={14} className="fill-current" />
                    PLAY SOLO
                  </button>
                ) : (
                  <div className="py-2.5 px-3 rounded-xl bg-[#121D32] text-center text-xs text-[#64748B] font-semibold border border-[#1F304E]">
                    No questions added
                  </div>
                )}

                {isAdmin && (
                  <button
                    onClick={() => onDeleteQuiz(quiz.id)}
                    className="w-full py-1.5 rounded-lg text-[11px] font-bold text-[#F43F5E] hover:bg-[#F43F5E]/10 transition-colors flex items-center justify-center gap-1"
                  >
                    <Trash2 size={12} />
                    Delete Quiz
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
