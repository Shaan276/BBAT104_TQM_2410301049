import React, { useEffect, useState } from 'react';
import { Award, Clock, Calendar, CheckCircle2, XCircle, ChevronLeft, ChevronRight, Zap } from 'lucide-react';

export default function StudentHistory({ currentUser }) {
  const [reportsData, setReportsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const fetchHistory = async (pageNum = 1) => {
    if (!currentUser?.id) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/reports/attempts?user_id=${currentUser.id}&page=${pageNum}&page_size=8`);
      const data = await res.json();
      if (data.success) {
        setReportsData(data);
        setPage(data.page);
      }
    } catch (err) {
      console.error('Failed to fetch student history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(1);
  }, [currentUser?.id]);

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-fun text-3xl font-extrabold text-white flex items-center gap-2">
            📊 My Assessment History
          </h1>
          <p className="text-xs text-purple-300 font-medium">
            Student records for <strong className="text-amber-300">{currentUser?.username}</strong> &bull; Only your personal attempts are visible.
          </p>
        </div>

        {reportsData && (
          <div className="badge-sla-pass self-start sm:self-auto">
            Chunk Stream: <strong className="font-mono">{reportsData.latencyMs} ms</strong> (SLA &le; 50 ms)
          </div>
        )}
      </div>

      {/* History Table / Cards */}
      {loading ? (
        <div className="glass-panel p-12 text-center text-purple-300 font-fun text-sm animate-pulse">
          Loading your attempts from database...
        </div>
      ) : !reportsData || reportsData.records.length === 0 ? (
        <div className="glass-panel p-12 text-center space-y-3">
          <div className="text-4xl">🎯</div>
          <h3 className="font-fun text-xl font-bold text-white">No attempts yet</h3>
          <p className="text-xs text-purple-300 max-w-sm mx-auto">
            You haven't attempted any quizzes under this student account yet. Jump into the quiz arena and take your first challenge!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="glass-panel overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-purple-950/80 border-b border-purple-500/20 text-purple-300 text-xs uppercase font-fun font-bold">
                  <tr>
                    <th className="py-3 px-4">Attempt #</th>
                    <th className="py-3 px-4">Quiz Title</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4 text-center">Score</th>
                    <th className="py-3 px-4 text-center">Status</th>
                    <th className="py-3 px-4 text-center">Commit Latency</th>
                    <th className="py-3 px-4 text-right">Attempt Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-500/10 text-white font-medium">
                  {reportsData.records.map((r) => {
                    const isPass = r.status === 'PASSED';
                    return (
                      <tr key={r.attempt_id} className="hover:bg-purple-900/20 transition-colors">
                        <td className="py-3 px-4 font-mono text-xs text-purple-300">
                          #{r.attempt_id}
                        </td>
                        <td className="py-3 px-4 font-fun font-bold text-white">
                          {r.quiz_title}
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded-lg bg-purple-900/40 text-[11px] font-semibold text-purple-200 border border-purple-500/20">
                            {r.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`font-fun font-extrabold text-base ${isPass ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {r.score_percentage}%
                          </span>
                          <span className="text-[11px] text-purple-300/80 block">
                            ({r.correct_answers}/{r.total_questions})
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-fun font-bold ${
                            isPass ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          }`}>
                            {isPass ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
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
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between px-2 pt-2">
            <p className="text-xs text-purple-300 font-mono">
              Showing page <strong>{reportsData.page}</strong> of <strong>{reportsData.totalPages}</strong> ({reportsData.totalRecords} total attempts)
            </p>

            <div className="flex items-center gap-2">
              <button
                onClick={() => fetchHistory(page - 1)}
                disabled={!reportsData.hasPrev}
                className="btn-push btn-push-purple px-3 py-1.5 text-xs disabled:opacity-40 disabled:cursor-not-allowed gap-1"
              >
                <ChevronLeft size={14} /> Previous
              </button>

              <button
                onClick={() => fetchHistory(page + 1)}
                disabled={!reportsData.hasNext}
                className="btn-push btn-push-purple px-3 py-1.5 text-xs disabled:opacity-40 disabled:cursor-not-allowed gap-1"
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
