import React, { useState, useEffect } from 'react';
import {
  Shield, Database, Cpu, Activity, RefreshCw, PlusCircle, CheckCircle2,
  AlertTriangle, Users, BookOpen, Layers, BarChart3, Clock, Search, ChevronLeft, ChevronRight
} from 'lucide-react';

export default function AdminDashboard({ onQuizCreated }) {
  const [activeSubTab, setActiveSubTab] = useState('metrics'); // 'metrics' | 'creator' | 'cohort' | 'audit' | 'indexes'
  
  // Dashboard metrics state
  const [metrics, setMetrics] = useState(null);
  const [metricsLatency, setMetricsLatency] = useState(0);
  const [isCached, setIsCached] = useState(false);
  const [cacheStats, setCacheStats] = useState(null);
  const [flushingCache, setFlushingCache] = useState(false);

  // Cohort reports state
  const [cohortData, setCohortData] = useState(null);
  const [cohortPage, setCohortPage] = useState(1);
  const [cohortSearch, setCohortSearch] = useState('');

  // Audit logs state
  const [auditLogs, setAuditLogs] = useState([]);

  // Database benchmarks state
  const [benchmarks, setBenchmarks] = useState(null);

  // Quiz Creator state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newDuration, setNewDuration] = useState(10);
  const [newPassingScore, setNewPassingScore] = useState(60);

  // Question state
  const [quizzesList, setQuizzesList] = useState([]);
  const [selectedQuizId, setSelectedQuizId] = useState('');
  const [qText, setQText] = useState('');
  const [optA, setOptA] = useState('');
  const [optB, setOptB] = useState('');
  const [optC, setOptC] = useState('');
  const [optD, setOptD] = useState('');
  const [correctOpt, setCorrectOpt] = useState('A');
  const [marks, setMarks] = useState(1);
  const [creatorMsg, setCreatorMsg] = useState(null);

  // Fetch Dashboard Metrics
  const fetchMetrics = async (forceRefresh = false) => {
    try {
      const res = await fetch(`/api/dashboard/metrics?force_refresh=${forceRefresh}`);
      const data = await res.json();
      if (data.success) {
        setMetrics(data.metrics);
        setMetricsLatency(data.latencyMs);
        setIsCached(data.isCached);
        setCacheStats(data.cacheStats);
      }
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  // Invalidate Cache
  const handleFlushCache = async () => {
    setFlushingCache(true);
    try {
      const res = await fetch('/api/dashboard/cache/flush', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchMetrics(false);
      }
    } catch (err) {
      console.error('Failed to flush cache:', err);
    } finally {
      setFlushingCache(false);
    }
  };

  // Fetch Cohort Reports
  const fetchCohortReports = async (page = 1, query = '') => {
    try {
      const res = await fetch(`/api/reports/attempts?page=${page}&page_size=8&query=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (data.success) {
        setCohortData(data);
        setCohortPage(data.page);
      }
    } catch (err) {
      console.error('Failed to fetch cohort:', err);
    }
  };

  // Fetch Audit Logs
  const fetchAuditLogs = async () => {
    try {
      const res = await fetch('/api/audit-logs?limit=40');
      const data = await res.json();
      if (data.success) {
        setAuditLogs(data.logs);
      }
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    }
  };

  // Fetch Benchmarks & Indexes
  const fetchBenchmarks = async () => {
    try {
      const res = await fetch('/api/tqm/benchmarks');
      const data = await res.json();
      if (data.success) {
        setBenchmarks(data);
      }
    } catch (err) {
      console.error('Failed to fetch benchmarks:', err);
    }
  };

  // Fetch Quizzes for question creator dropdown
  const fetchQuizzesList = async () => {
    try {
      const res = await fetch('/api/quizzes');
      const data = await res.json();
      if (data.success) {
        setQuizzesList(data.quizzes);
        if (data.quizzes.length > 0 && !selectedQuizId) {
          setSelectedQuizId(data.quizzes[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to fetch quizzes list:', err);
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchQuizzesList();
  }, []);

  useEffect(() => {
    if (activeSubTab === 'cohort') fetchCohortReports(1, cohortSearch);
    if (activeSubTab === 'audit') fetchAuditLogs();
    if (activeSubTab === 'indexes') fetchBenchmarks();
  }, [activeSubTab]);

  // Handle Create Quiz
  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    setCreatorMsg(null);
    if (!newTitle.trim() || !newCategory.trim()) {
      setCreatorMsg({ type: 'error', text: 'Poka-Yoke: Title and Category cannot be empty!' });
      return;
    }
    try {
      const res = await fetch('/api/quizzes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          category: newCategory,
          duration_minutes: newDuration,
          passing_score: newPassingScore
        })
      });
      const data = await res.json();
      if (data.success) {
        setCreatorMsg({ type: 'success', text: `Quiz created successfully! (ID: #${data.quizId})` });
        setNewTitle('');
        setNewCategory('');
        fetchQuizzesList();
        fetchMetrics(true);
        if (onQuizCreated) onQuizCreated();
      } else {
        setCreatorMsg({ type: 'error', text: data.error || 'Failed to create quiz' });
      }
    } catch (err) {
      setCreatorMsg({ type: 'error', text: err.message });
    }
  };

  // Handle Add Question
  const handleAddQuestion = async (e) => {
    e.preventDefault();
    setCreatorMsg(null);
    if (!selectedQuizId) {
      setCreatorMsg({ type: 'error', text: 'Please select a quiz first.' });
      return;
    }
    if (!qText.trim() || !optA.trim() || !optB.trim() || !optC.trim() || !optD.trim()) {
      setCreatorMsg({ type: 'error', text: 'Poka-Yoke: Question text and all 4 options are required.' });
      return;
    }
    try {
      const res = await fetch(`/api/quizzes/${selectedQuizId}/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_text: qText,
          option_a: optA,
          option_b: optB,
          option_c: optC,
          option_d: optD,
          correct_option: correctOpt,
          marks: marks
        })
      });
      const data = await res.json();
      if (data.success) {
        setCreatorMsg({ type: 'success', text: `Question added successfully to quiz #${selectedQuizId}!` });
        setQText('');
        setOptA('');
        setOptB('');
        setOptC('');
        setOptD('');
        fetchQuizzesList();
        fetchMetrics(true);
        if (onQuizCreated) onQuizCreated();
      } else {
        setCreatorMsg({ type: 'error', text: data.error || 'Failed to add question' });
      }
    } catch (err) {
      setCreatorMsg({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-fun text-3xl font-extrabold text-white flex items-center gap-2">
            👨‍🏫 Teacher Studio & TQM Quality Cockpit
          </h1>
          <p className="text-xs text-purple-300 font-medium">
            TQM Goal Q05 [Reduce Response Time] &bull; Course BBAT104 Session 2026-27 &bull; Piyush Pilkhwal (2410301049)
          </p>
        </div>

        {/* Sub Navigation */}
        <div className="flex items-center gap-1 bg-purple-950/70 p-1 rounded-2xl border border-purple-500/20 overflow-x-auto">
          {[
            { id: 'metrics', label: '⚡ TQM Metrics' },
            { id: 'creator', label: '✏️ Quiz Studio' },
            { id: 'cohort', label: '👥 Cohort Scores' },
            { id: 'audit', label: '📜 Audit Logs' },
            { id: 'indexes', label: '🗄️ B-Tree Indexes' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`px-3 py-1.5 rounded-xl font-fun text-xs font-semibold whitespace-nowrap transition-all ${
                activeSubTab === tab.id
                  ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/30'
                  : 'text-purple-200 hover:text-white hover:bg-purple-900/40'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ----------------- SUBTAB 1: TQM METRICS ----------------- */}
      {activeSubTab === 'metrics' && (
        <div className="space-y-6">
          
          {/* Cache Cockpit Card */}
          <div className="glass-panel-elevated p-6 border-amber-400/30">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Cpu size={20} className="text-amber-400" />
                  <h3 className="font-fun text-xl font-bold text-white">
                    In-Memory TTL Cache Cockpit (Q05-F3)
                  </h3>
                </div>
                <p className="text-xs text-purple-300">
                  Direct RAM retrieval eliminates disk I/O bottlenecks to achieve sub-15ms response times.
                </p>
              </div>

              {/* Cache Invalidation Action Button */}
              <button
                onClick={handleFlushCache}
                disabled={flushingCache}
                className="btn-push btn-push-amber px-5 py-2.5 text-xs gap-2 whitespace-nowrap"
              >
                <RefreshCw size={14} className={flushingCache ? 'animate-spin' : ''} />
                Flush RAM Cache (Demonstrate Q05)
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl bg-purple-950/50 border border-purple-500/20 text-center">
                <p className="text-[10px] text-purple-300 uppercase font-bold tracking-wider">Status</p>
                <p className="font-fun text-lg font-bold text-white flex items-center justify-center gap-1 mt-1">
                  {isCached ? (
                    <span className="text-emerald-400 flex items-center gap-1">⚡ RAM HIT</span>
                  ) : (
                    <span className="text-amber-400 flex items-center gap-1">💾 DB FETCH</span>
                  )}
                </p>
                <span className="text-[10px] text-purple-300/80 block mt-1">
                  60s Auto Invalidation TTL
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-purple-950/50 border border-purple-500/20 text-center">
                <p className="text-[10px] text-purple-300 uppercase font-bold tracking-wider">Read Latency</p>
                <p className="font-mono text-2xl font-black text-cyan-300 mt-1">
                  {metricsLatency} ms
                </p>
                <span className="badge-sla-pass text-[10px] mt-1">
                  SLA &le; 15.0 ms
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-purple-950/50 border border-purple-500/20 text-center">
                <p className="text-[10px] text-purple-300 uppercase font-bold tracking-wider">Cache Hit Ratio</p>
                <p className="font-fun text-2xl font-bold text-amber-300 mt-1">
                  {cacheStats?.hitRatio || 0}%
                </p>
                <span className="text-[10px] text-purple-300/80 block mt-1">
                  {cacheStats?.hits || 0} Hits / {cacheStats?.misses || 0} Misses
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-purple-950/50 border border-purple-500/20 text-center">
                <p className="text-[10px] text-purple-300 uppercase font-bold tracking-wider">Cached Items</p>
                <p className="font-fun text-2xl font-bold text-purple-200 mt-1">
                  {cacheStats?.entries || 0}
                </p>
                <span className="text-[10px] text-purple-300/80 block mt-1">
                  In-Memory Keys Active
                </span>
              </div>
            </div>
          </div>

          {/* Aggregate Cohort Overview Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-5 text-center space-y-1">
              <BookOpen size={20} className="mx-auto text-purple-400" />
              <p className="text-[10px] text-purple-300 uppercase font-bold">Total Quizzes</p>
              <p className="font-fun text-2xl font-black text-white">{metrics?.totalQuizzes || 0}</p>
            </div>

            <div className="glass-panel p-5 text-center space-y-1">
              <Layers size={20} className="mx-auto text-cyan-400" />
              <p className="text-[10px] text-purple-300 uppercase font-bold">Question Bank</p>
              <p className="font-fun text-2xl font-black text-white">{metrics?.totalQuestions || 0}</p>
            </div>

            <div className="glass-panel p-5 text-center space-y-1">
              <BarChart3 size={20} className="mx-auto text-emerald-400" />
              <p className="text-[10px] text-purple-300 uppercase font-bold">Total Student Attempts</p>
              <p className="font-fun text-2xl font-black text-white">{metrics?.totalAttempts || 0}</p>
            </div>

            <div className="glass-panel p-5 text-center space-y-1">
              <CheckCircle2 size={20} className="mx-auto text-amber-400" />
              <p className="text-[10px] text-purple-300 uppercase font-bold">Cohort Pass Rate</p>
              <p className="font-fun text-2xl font-black text-amber-300">{metrics?.passRate || 0}%</p>
            </div>
          </div>

        </div>
      )}

      {/* ----------------- SUBTAB 2: QUIZ & QUESTION CREATOR ----------------- */}
      {activeSubTab === 'creator' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Create Quiz Form */}
          <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <PlusCircle size={20} className="text-amber-400" />
              <h3 className="font-fun text-xl font-bold text-white">Create New Assessment</h3>
            </div>

            {creatorMsg && (
              <div className={`p-3 rounded-xl text-xs font-medium border ${
                creatorMsg.type === 'success'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
              }`}>
                {creatorMsg.text}
              </div>
            )}

            <form onSubmit={handleCreateQuiz} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Quiz Title</label>
                <input
                  type="text"
                  placeholder="e.g. Statistical Quality Control Tools"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Category</label>
                <input
                  type="text"
                  placeholder="e.g. Quality Management, Computer Science"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none focus:border-amber-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-purple-200 mb-1">Duration (Min)</label>
                  <input
                    type="number"
                    min="1"
                    max="180"
                    value={newDuration}
                    onChange={(e) => setNewDuration(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-purple-200 mb-1">Passing Score (%)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={newPassingScore}
                    onChange={(e) => setNewPassingScore(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none"
                  />
                </div>
              </div>

              <button type="submit" className="btn-push btn-push-amber w-full py-3 text-sm">
                Create Quiz Header
              </button>
            </form>
          </div>

          {/* Add Questions Form */}
          <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <Layers size={20} className="text-purple-400" />
              <h3 className="font-fun text-xl font-bold text-white">Add Question to Quiz</h3>
            </div>

            <form onSubmit={handleAddQuestion} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Target Quiz</label>
                <select
                  value={selectedQuizId}
                  onChange={(e) => setSelectedQuizId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none"
                >
                  {quizzesList.map((q) => (
                    <option key={q.id} value={q.id} className="bg-slate-900 text-white">
                      #{q.id} - {q.title} ({q.question_count} questions)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-purple-200 mb-1">Question Text</label>
                <textarea
                  rows="2"
                  placeholder="Enter the question prompt..."
                  value={qText}
                  onChange={(e) => setQText(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-purple-950/70 border border-purple-500/30 text-white text-sm focus:outline-none focus:border-purple-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <label className="text-rose-300 font-bold block mb-1">▲ Option A</label>
                  <input
                    type="text"
                    value={optA}
                    onChange={(e) => setOptA(e.target.value)}
                    placeholder="Option A text"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-purple-950/70 border border-rose-500/30 text-white"
                  />
                </div>

                <div>
                  <label className="text-blue-300 font-bold block mb-1">◆ Option B</label>
                  <input
                    type="text"
                    value={optB}
                    onChange={(e) => setOptB(e.target.value)}
                    placeholder="Option B text"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-purple-950/70 border border-blue-500/30 text-white"
                  />
                </div>

                <div>
                  <label className="text-amber-300 font-bold block mb-1">● Option C</label>
                  <input
                    type="text"
                    value={optC}
                    onChange={(e) => setOptC(e.target.value)}
                    placeholder="Option C text"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-purple-950/70 border border-amber-500/30 text-white"
                  />
                </div>

                <div>
                  <label className="text-emerald-300 font-bold block mb-1">■ Option D</label>
                  <input
                    type="text"
                    value={optD}
                    onChange={(e) => setOptD(e.target.value)}
                    placeholder="Option D text"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-purple-950/70 border border-emerald-500/30 text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="block text-xs font-semibold text-purple-200 mb-1">Correct Answer Key</label>
                  <div className="grid grid-cols-4 gap-1">
                    {['A', 'B', 'C', 'D'].map((key) => (
                      <button
                        type="button"
                        key={key}
                        onClick={() => setCorrectOpt(key)}
                        className={`py-1.5 rounded-lg font-fun text-xs font-bold border transition-all ${
                          correctOpt === key
                            ? 'bg-amber-400 text-slate-950 border-amber-300 shadow'
                            : 'bg-purple-950/40 text-purple-200 border-purple-500/20'
                        }`}
                      >
                        {key}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-purple-200 mb-1">Marks</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={marks}
                    onChange={(e) => setMarks(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-1.5 rounded-lg bg-purple-950/70 border border-purple-500/30 text-white text-xs"
                  />
                </div>
              </div>

              <button type="submit" className="btn-push btn-push-purple w-full py-2.5 text-xs font-fun mt-2">
                Add Question to Quiz
              </button>
            </form>
          </div>

        </div>
      )}

      {/* ----------------- SUBTAB 3: COHORT REPORTS (ADMIN FULL VIEW) ----------------- */}
      {activeSubTab === 'cohort' && (
        <div className="space-y-4">
          <div className="glass-panel p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-fun text-xl font-bold text-white">Full Cohort Attempt Records</h3>
              <p className="text-xs text-purple-300">
                Admin Privilege: You can view scores and attempt logs for all enrolled students.
              </p>
            </div>

            <div className="relative w-full sm:w-72">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-400" />
              <input
                type="text"
                placeholder="Filter by student or quiz..."
                value={cohortSearch}
                onChange={(e) => {
                  setCohortSearch(e.target.value);
                  fetchCohortReports(1, e.target.value);
                }}
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-purple-950/60 border border-purple-500/30 text-white text-xs"
              />
            </div>
          </div>

          {cohortData && (
            <div className="glass-panel overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-purple-950/80 border-b border-purple-500/20 text-purple-300 text-xs uppercase font-fun font-bold">
                    <tr>
                      <th className="py-3 px-4">Attempt #</th>
                      <th className="py-3 px-4">Student</th>
                      <th className="py-3 px-4">Quiz Title</th>
                      <th className="py-3 px-4 text-center">Score %</th>
                      <th className="py-3 px-4 text-center">Status</th>
                      <th className="py-3 px-4 text-center">Commit Latency</th>
                      <th className="py-3 px-4 text-right">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-purple-500/10 text-white font-medium">
                    {cohortData.records.map((r) => {
                      const isPass = r.status === 'PASSED';
                      return (
                        <tr key={r.attempt_id} className="hover:bg-purple-900/20">
                          <td className="py-3 px-4 font-mono text-xs text-purple-300">#{r.attempt_id}</td>
                          <td className="py-3 px-4 font-fun font-bold text-amber-300">{r.username}</td>
                          <td className="py-3 px-4">{r.quiz_title}</td>
                          <td className="py-3 px-4 text-center font-bold">
                            <span className={isPass ? 'text-emerald-400' : 'text-rose-400'}>
                              {r.score_percentage}%
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                              isPass ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                            }`}>
                              {r.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center font-mono text-xs text-cyan-300">
                            {r.latency_ms} ms
                          </td>
                          <td className="py-3 px-4 text-right text-xs text-purple-300 font-mono">
                            {r.created_at}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between p-4 border-t border-purple-500/20 text-xs">
                <span className="text-purple-300 font-mono">
                  Page {cohortData.page} of {cohortData.totalPages} ({cohortData.totalRecords} total)
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => fetchCohortReports(cohortPage - 1, cohortSearch)}
                    disabled={!cohortData.hasPrev}
                    className="btn-push btn-push-purple px-3 py-1.5 text-xs disabled:opacity-40"
                  >
                    <ChevronLeft size={14} />
                  </button>
                  <button
                    onClick={() => fetchCohortReports(cohortPage + 1, cohortSearch)}
                    disabled={!cohortData.hasNext}
                    className="btn-push btn-push-purple px-3 py-1.5 text-xs disabled:opacity-40"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ----------------- SUBTAB 4: AUDIT LOGS ----------------- */}
      {activeSubTab === 'audit' && (
        <div className="glass-panel overflow-hidden">
          <div className="p-4 bg-purple-950/80 border-b border-purple-500/20 flex items-center justify-between">
            <h3 className="font-fun text-xl font-bold text-white">System Transaction Audit Logs</h3>
            <span className="text-xs text-purple-300 font-mono">Live TQM Traceability</span>
          </div>

          <div className="divide-y divide-purple-500/10 max-h-[500px] overflow-y-auto">
            {auditLogs.map((log) => (
              <div key={log.id} className="p-3.5 hover:bg-purple-900/20 flex items-center justify-between gap-4 text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded font-mono font-bold bg-purple-900/50 text-amber-300 border border-purple-500/30">
                      {log.action}
                    </span>
                    <span className="font-fun font-bold text-white">
                      {log.username ? `User: ${log.username}` : 'System'}
                    </span>
                  </div>
                  <p className="text-purple-200 font-medium">{log.detail}</p>
                </div>

                <div className="text-right whitespace-nowrap font-mono text-[11px] text-purple-400">
                  <p>{log.created_at}</p>
                  {log.latency_ms > 0 && (
                    <p className="text-cyan-300">{log.latency_ms} ms</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ----------------- SUBTAB 5: B-TREE INDEX INSPECTOR ----------------- */}
      {activeSubTab === 'indexes' && benchmarks && (
        <div className="space-y-6">
          <div className="glass-panel p-6 space-y-4">
            <h3 className="font-fun text-xl font-bold text-white flex items-center gap-2">
              <Database size={20} className="text-cyan-400" />
              Active SQLite B-Tree Indexes (Q05-F4)
            </h3>
            <p className="text-xs text-purple-300">
              Eliminates full table scans to guarantee instantaneous queries under large dataset scaling.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {benchmarks.indexes?.map((idx) => (
                <div key={idx.name} className="p-3 rounded-2xl bg-purple-950/60 border border-purple-500/20 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-amber-300">{idx.name}</span>
                    <span className="badge-sla-pass text-[10px]">ACTIVE</span>
                  </div>
                  <p className="text-[11px] text-purple-300/80 font-mono">Table: {idx.tbl_name}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel p-6 space-y-4">
            <h3 className="font-fun text-xl font-bold text-white">
              Query Optimizer Execution Plans (EXPLAIN QUERY PLAN)
            </h3>
            <div className="space-y-3">
              {benchmarks.queryPlans?.map((qp, i) => (
                <div key={i} className="p-3.5 rounded-2xl bg-purple-950/60 border border-purple-500/20 flex items-center justify-between gap-4">
                  <div>
                    <p className="font-fun text-sm font-bold text-white">{qp.label}</p>
                    <p className="font-mono text-xs text-purple-300">{qp.details}</p>
                  </div>
                  <span className={qp.usesIndex ? 'badge-sla-pass' : 'badge-sla-warn'}>
                    {qp.usesIndex ? '✓ USING INDEX' : 'SCAN'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
