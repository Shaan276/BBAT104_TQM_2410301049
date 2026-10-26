const express = require('express');
const cors = require('cors');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Resolve DB path
const DB_PATH = path.resolve(__dirname, '../../data/quiz_system.db');

// Ensure data folder exists
const dataDir = path.dirname(DB_PATH);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Open SQLite connection
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Failed to connect to SQLite database:', err.message);
  } else {
    console.log(`Connected to SQLite database at: ${DB_PATH}`);
    db.run("PRAGMA journal_mode = WAL;");
    db.run("PRAGMA synchronous = NORMAL;");
    db.run("PRAGMA foreign_keys = ON;");
  }
});

// Helper for promise-based db.all / db.get / db.run
const dbAll = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
};

const dbGet = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
};

const dbRun = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
};

// -------------------------------------------------------------
// Quality Specifications & In-Memory TTL Cache (Q05-F3)
// -------------------------------------------------------------
const SLA_LIMITS = {
  SEARCH_LATENCY_MS: 40.0,
  LOAD_QUIZ_LATENCY_MS: 50.0,
  SUBMIT_LATENCY_MS: 100.0,
  CACHE_READ_MS: 15.0,
  PAGE_CHUNK_MS: 50.0
};

class MemoryCache {
  constructor(defaultTTLSeconds = 60) {
    this.store = new Map();
    this.defaultTTL = defaultTTLSeconds * 1000;
    this.hits = 0;
    this.misses = 0;
  }

  get(key) {
    const start = process.hrtime.bigint();
    const item = this.store.get(key);
    if (item && item.expiresAt > Date.now()) {
      this.hits++;
      const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
      return { value: item.value, latencyMs: Number(latencyMs.toFixed(3)), isHit: true };
    }
    this.misses++;
    if (item) this.store.delete(key);
    const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
    return { value: null, latencyMs: Number(latencyMs.toFixed(3)), isHit: false };
  }

  set(key, value, ttlSeconds = null) {
    const ttl = (ttlSeconds ? ttlSeconds * 1000 : this.defaultTTL);
    this.store.set(key, {
      value,
      expiresAt: Date.now() + ttl
    });
  }

  invalidate(key = null) {
    if (key) {
      this.store.delete(key);
    } else {
      this.store.clear();
    }
  }

  getStats() {
    return {
      entries: this.store.size,
      hits: this.hits,
      misses: this.misses,
      hitRatio: this.hits + this.misses > 0 
        ? Number(((this.hits / (this.hits + this.misses)) * 100).toFixed(1)) 
        : 0.0
    };
  }
}

const cacheManager = new MemoryCache(60);

// Audit & Error Logger
const logAudit = async (action, detail, userId = null, latencyMs = 0.0) => {
  try {
    await dbRun(
      `INSERT INTO audit_logs (user_id, action, detail, latency_ms) VALUES (?, ?, ?, ?)`,
      [userId, action.toUpperCase(), detail, Number(latencyMs.toFixed(2))]
    );
  } catch (err) {
    console.error('Audit log write error:', err.message);
  }
};

const logErrorMode = async (errorCode, problem, context = "") => {
  try {
    await dbRun(
      `INSERT INTO error_logs (error_code, problem, context) VALUES (?, ?, ?)`,
      [errorCode.toUpperCase(), problem, context]
    );
  } catch (err) {
    console.error('Error log write error:', err.message);
  }
};

// -------------------------------------------------------------
// API Endpoints
// -------------------------------------------------------------

// 1. Users & Authentication (FR-01)
app.get('/api/users', async (req, res) => {
  try {
    const users = await dbAll('SELECT id, username, role, created_at FROM users ORDER BY id ASC');
    res.json({ success: true, users });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/users', async (req, res) => {
  try {
    const { username, role } = req.body;
    if (!username || !username.trim()) {
      await logErrorMode('ERR_USER_EMPTY', 'Attempted to create user with empty username');
      return res.status(400).json({ success: false, error: 'Username cannot be blank (Poka-Yoke intercept)' });
    }
    const cleanUser = username.trim().toLowerCase();
    const cleanRole = (role || 'STUDENT').toUpperCase();
    if (!['ADMIN', 'STUDENT'].includes(cleanRole)) {
      return res.status(400).json({ success: false, error: 'Role must be ADMIN or STUDENT' });
    }

    const result = await dbRun('INSERT INTO users (username, role) VALUES (?, ?)', [cleanUser, cleanRole]);
    await logAudit('ADD_USER', `Created user '${cleanUser}' with role ${cleanRole}`, result.lastID);
    res.json({ success: true, user: { id: result.lastID, username: cleanUser, role: cleanRole } });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      return res.status(400).json({ success: false, error: 'Username already exists. Please choose another.' });
    }
    res.status(500).json({ success: false, error: err.message });
  }
});

// 2. Quizzes & Fast Search (Q05-F1 & FR-02)
app.get('/api/quizzes', async (req, res) => {
  const start = process.hrtime.bigint();
  try {
    const { query = '', category = '', sort = 'id_asc' } = req.query;
    let sql = 'SELECT * FROM quizzes WHERE 1=1';
    const params = [];

    if (category && category.toLowerCase() !== 'all') {
      sql += ' AND category = ?';
      params.push(category.trim());
    }

    if (query && query.trim()) {
      sql += ' AND (title LIKE ? OR category LIKE ?)';
      const wildcard = `%${query.trim()}%`;
      params.push(wildcard, wildcard);
    }

    // Sort mappings
    let orderClause = 'id ASC';
    const s = sort.toLowerCase();
    if (s.includes('title')) orderClause = s.includes('desc') ? 'title COLLATE NOCASE DESC' : 'title COLLATE NOCASE ASC';
    else if (s.includes('category')) orderClause = 'category COLLATE NOCASE ASC, title ASC';
    else if (s.includes('duration')) orderClause = s.includes('desc') ? 'duration_minutes DESC' : 'duration_minutes ASC';
    else if (s.includes('pass')) orderClause = s.includes('desc') ? 'passing_score DESC' : 'passing_score ASC';
    else if (s.includes('id_desc')) orderClause = 'id DESC';

    sql += ` ORDER BY ${orderClause}`;

    const quizzes = await dbAll(sql, params);

    // Also get question count for each quiz
    const counts = await dbAll('SELECT quiz_id, COUNT(*) as count FROM questions GROUP BY quiz_id');
    const countMap = {};
    counts.forEach(c => { countMap[c.quiz_id] = c.count; });

    const enriched = quizzes.map(q => ({
      ...q,
      question_count: countMap[q.id] || 0
    }));

    const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
    const withinSla = latencyMs <= SLA_LIMITS.SEARCH_LATENCY_MS;

    res.json({
      success: true,
      quizzes: enriched,
      latencyMs: Number(latencyMs.toFixed(3)),
      withinSla,
      slaLimitMs: SLA_LIMITS.SEARCH_LATENCY_MS
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Categories list
app.get('/api/quizzes/categories', async (req, res) => {
  try {
    const rows = await dbAll('SELECT DISTINCT category FROM quizzes ORDER BY category ASC');
    const categories = rows.map(r => r.category).filter(Boolean);
    res.json({ success: true, categories });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create Quiz (with Poka-Yoke)
app.post('/api/quizzes', async (req, res) => {
  try {
    const { title, category, duration_minutes = 10, passing_score = 60, questions = [] } = req.body;

    // Poka-Yoke validation
    if (!title || !title.trim()) {
      await logErrorMode('ERR_QUIZ_EMPTY_TITLE', 'Attempted to create quiz without a title');
      return res.status(400).json({ success: false, error: 'Poka-Yoke: Quiz title cannot be empty.' });
    }
    if (!category || !category.trim()) {
      await logErrorMode('ERR_QUIZ_EMPTY_CAT', 'Attempted to create quiz without a category');
      return res.status(400).json({ success: false, error: 'Poka-Yoke: Category is required.' });
    }
    const duration = parseInt(duration_minutes, 10);
    const pass = parseInt(passing_score, 10);
    if (isNaN(duration) || duration <= 0 || isNaN(pass) || pass <= 0 || pass > 100) {
      await logErrorMode('ERR_QUIZ_INVALID_SETTINGS', `Invalid duration (${duration}) or passing score (${pass})`);
      return res.status(400).json({ success: false, error: 'Poka-Yoke: Duration must be > 0 min and Passing Score between 1-100%.' });
    }

    const result = await dbRun(
      'INSERT INTO quizzes (title, category, duration_minutes, passing_score) VALUES (?, ?, ?, ?)',
      [title.trim(), category.trim(), duration, pass]
    );
    const quizId = result.lastID;

    // If initial questions provided, insert them
    if (Array.isArray(questions) && questions.length > 0) {
      for (const q of questions) {
        if (q.question_text && q.option_a && q.option_b && q.option_c && q.option_d && q.correct_option) {
          await dbRun(
            `INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
            [quizId, q.question_text.trim(), q.option_a.trim(), q.option_b.trim(), q.option_c.trim(), q.option_d.trim(), q.correct_option.toUpperCase(), q.marks || 1]
          );
        }
      }
    }

    cacheManager.invalidate('dashboard_metrics');
    await logAudit('CREATE_QUIZ', `Created quiz #${quizId}: '${title.trim()}' with ${questions.length} questions`);

    res.json({ success: true, quizId, message: 'Quiz created successfully!' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete Quiz
app.delete('/api/quizzes/:id', async (req, res) => {
  try {
    const quizId = req.params.id;
    const quiz = await dbGet('SELECT title FROM quizzes WHERE id = ?', [quizId]);
    if (!quiz) {
      return res.status(404).json({ success: false, error: 'Quiz not found' });
    }
    await dbRun('DELETE FROM quizzes WHERE id = ?', [quizId]);
    cacheManager.invalidate('dashboard_metrics');
    await logAudit('DELETE_QUIZ', `Deleted quiz #${quizId} ('${quiz.title}')`);
    res.json({ success: true, message: `Quiz #${quizId} deleted` });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Add Question to Quiz (Poka-Yoke)
app.post('/api/quizzes/:id/questions', async (req, res) => {
  try {
    const quizId = req.params.id;
    const { question_text, option_a, option_b, option_c, option_d, correct_option, marks = 1 } = req.body;

    if (!question_text || !option_a || !option_b || !option_c || !option_d || !correct_option) {
      await logErrorMode('ERR_Q_INCOMPLETE', `Attempted incomplete question creation for quiz #${quizId}`);
      return res.status(400).json({ success: false, error: 'Poka-Yoke: Question text and all 4 options (A, B, C, D) are required.' });
    }

    const corr = correct_option.trim().toUpperCase();
    if (!['A', 'B', 'C', 'D'].includes(corr)) {
      await logErrorMode('ERR_Q_INVALID_KEY', `Invalid correct option key '${corr}'`);
      return res.status(400).json({ success: false, error: 'Poka-Yoke: Correct option must be A, B, C, or D.' });
    }

    const result = await dbRun(
      `INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [quizId, question_text.trim(), option_a.trim(), option_b.trim(), option_c.trim(), option_d.trim(), corr, parseInt(marks, 10) || 1]
    );

    cacheManager.invalidate('dashboard_metrics');
    await logAudit('ADD_QUESTION', `Added question #${result.lastID} to quiz #${quizId}`);
    res.json({ success: true, questionId: result.lastID });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 3. Load Quiz Session (Q05-F2 & FR-04)
app.get('/api/quizzes/:id', async (req, res) => {
  const start = process.hrtime.bigint();
  try {
    const quizId = req.params.id;
    const quiz = await dbGet('SELECT * FROM quizzes WHERE id = ?', [quizId]);
    if (!quiz) {
      return res.status(404).json({ success: false, error: `Quiz #${quizId} not found` });
    }

    // Utilizes B-Tree index idx_questions_quiz_id
    const questions = await dbAll(
      `SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks
       FROM questions WHERE quiz_id = ? ORDER BY id ASC`,
      [quizId]
    );

    const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
    const withinSla = latencyMs <= SLA_LIMITS.LOAD_QUIZ_LATENCY_MS;

    res.json({
      success: true,
      quiz,
      questions,
      latencyMs: Number(latencyMs.toFixed(3)),
      withinSla,
      slaLimitMs: SLA_LIMITS.LOAD_QUIZ_LATENCY_MS
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 4. Submit Attempt & Auto-Grading (FR-04)
app.post('/api/quizzes/:id/submit', async (req, res) => {
  const start = process.hrtime.bigint();
  try {
    const quizId = req.params.id;
    const { user_id, answers = {}, time_taken_seconds = 0 } = req.body;

    if (!user_id) {
      return res.status(400).json({ success: false, error: 'User ID is required to submit attempt.' });
    }

    const quiz = await dbGet('SELECT title, passing_score FROM quizzes WHERE id = ?', [quizId]);
    if (!quiz) {
      return res.status(404).json({ success: false, error: 'Quiz not found' });
    }

    const questions = await dbAll('SELECT id, correct_option, marks FROM questions WHERE quiz_id = ?', [quizId]);
    if (questions.length === 0) {
      return res.status(400).json({ success: false, error: 'Cannot submit attempt for quiz with no questions.' });
    }

    let correctCount = 0;
    let earnedMarks = 0;
    let totalMarks = 0;
    const itemDetails = [];

    for (const q of questions) {
      totalMarks += q.marks;
      const selected = (answers[q.id] || 'NONE').toUpperCase();
      const isCorrect = selected === q.correct_option.toUpperCase() ? 1 : 0;
      if (isCorrect) {
        correctCount += 1;
        earnedMarks += q.marks;
      }
      itemDetails.push({ questionId: q.id, selected, isCorrect });
    }

    const scorePercentage = totalMarks > 0 ? Number(((earnedMarks / totalMarks) * 100).toFixed(1)) : 0.0;
    const status = scorePercentage >= quiz.passing_score ? 'PASSED' : 'FAILED';

    const calcLatencyMs = Number(process.hrtime.bigint() - start) / 1e6;

    // Insert attempt atomically
    const attemptResult = await dbRun(
      `INSERT INTO attempts (quiz_id, user_id, total_questions, correct_answers, score_percentage, status, latency_ms)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [quizId, user_id, questions.length, correctCount, scorePercentage, status, Number(calcLatencyMs.toFixed(2))]
    );
    const attemptId = attemptResult.lastID;

    // Insert item details
    for (const item of itemDetails) {
      await dbRun(
        `INSERT INTO attempt_answers (attempt_id, question_id, selected_option, is_correct)
         VALUES (?, ?, ?, ?)`,
        [attemptId, item.questionId, item.selected, item.isCorrect]
      );
    }

    // Invalidate dashboard metrics cache
    cacheManager.invalidate('dashboard_metrics');

    const totalElapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
    const withinSla = totalElapsedMs <= SLA_LIMITS.SUBMIT_LATENCY_MS;

    await logAudit(
      'SUBMIT_ATTEMPT',
      `Quiz #${quizId} ('${quiz.title}'): Score ${scorePercentage}% (${correctCount}/${questions.length}) - ${status}`,
      user_id,
      totalElapsedMs
    );

    res.json({
      success: true,
      summary: {
        attemptId,
        quizId,
        quizTitle: quiz.title,
        totalQuestions: questions.length,
        correctAnswers: correctCount,
        earnedMarks,
        totalMarks,
        scorePercentage,
        passingScore: quiz.passing_score,
        status,
        latencyMs: Number(totalElapsedMs.toFixed(3)),
        withinSla,
        slaLimitMs: SLA_LIMITS.SUBMIT_LATENCY_MS,
        itemDetails
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5. Dashboard Metrics & Cached DB (Q05-F3)
app.get('/api/dashboard/metrics', async (req, res) => {
  const { force_refresh = 'false' } = req.query;
  const force = force_refresh === 'true';

  if (!force) {
    const cached = cacheManager.get('dashboard_metrics');
    if (cached.isHit) {
      return res.json({
        success: true,
        metrics: cached.value,
        latencyMs: cached.latencyMs,
        isCached: true,
        withinSla: cached.latencyMs <= SLA_LIMITS.CACHE_READ_MS,
        cacheStats: cacheManager.getStats()
      });
    }
  }

  // Cache miss or force refresh: fetch from DB
  const start = process.hrtime.bigint();
  try {
    const totalQuizzes = (await dbGet('SELECT COUNT(*) as c FROM quizzes')).c;
    const totalQuestions = (await dbGet('SELECT COUNT(*) as c FROM questions')).c;
    const totalAttempts = (await dbGet('SELECT COUNT(*) as c FROM attempts')).c;
    const totalUsers = (await dbGet('SELECT COUNT(*) as c FROM users')).c;

    const passStats = await dbGet(`
      SELECT 
        COUNT(CASE WHEN status = 'PASSED' THEN 1 END) as passed_count,
        AVG(score_percentage) as avg_score,
        AVG(latency_ms) as avg_latency
      FROM attempts
    `);

    const metrics = {
      totalQuizzes,
      totalQuestions,
      totalAttempts,
      totalUsers,
      passedCount: passStats.passed_count || 0,
      passRate: totalAttempts > 0 ? Number(((passStats.passed_count / totalAttempts) * 100).toFixed(1)) : 0.0,
      avgScore: passStats.avg_score ? Number(passStats.avg_score.toFixed(1)) : 0.0,
      avgLatencyMs: passStats.avg_latency ? Number(passStats.avg_latency.toFixed(2)) : 0.0,
      cachedAt: new Date().toISOString()
    };

    cacheManager.set('dashboard_metrics', metrics, 60);

    const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;

    res.json({
      success: true,
      metrics,
      latencyMs: Number(latencyMs.toFixed(3)),
      isCached: false,
      withinSla: latencyMs <= SLA_LIMITS.CACHE_READ_MS,
      cacheStats: cacheManager.getStats()
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Cache Flush endpoint
app.post('/api/dashboard/cache/flush', (req, res) => {
  const start = process.hrtime.bigint();
  cacheManager.invalidate('dashboard_metrics');
  const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
  res.json({
    success: true,
    message: 'In-memory dashboard metrics cache flushed successfully!',
    latencyMs: Number(elapsedMs.toFixed(3))
  });
});

// 6. Paginated Historical Reports (Q05-F5)
app.get('/api/reports/attempts', async (req, res) => {
  const start = process.hrtime.bigint();
  try {
    const page = Math.max(1, parseInt(req.query.page, 10) || 1);
    const pageSize = Math.max(1, Math.min(parseInt(req.query.page_size, 10) || 10, 100));
    const offset = (page - 1) * pageSize;
    const userId = req.query.user_id ? parseInt(req.query.user_id, 10) : null;
    const query = req.query.query ? req.query.query.trim().toLowerCase() : '';

    let whereClauses = ['1=1'];
    const params = [];

    if (userId) {
      whereClauses.push('a.user_id = ?');
      params.push(userId);
    }

    if (query) {
      whereClauses.push('(u.username LIKE ? OR q.title LIKE ?)');
      params.push(`%${query}%`, `%${query}%`);
    }

    const whereSql = whereClauses.join(' AND ');

    // Total count
    const countSql = `
      SELECT COUNT(*) as total
      FROM attempts a
      JOIN users u ON a.user_id = u.id
      JOIN quizzes q ON a.quiz_id = q.id
      WHERE ${whereSql}
    `;
    const countRow = await dbGet(countSql, params);
    const totalRecords = countRow ? countRow.total : 0;
    const totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));

    // Chunked paginated query (utilizing indexed ORDER BY)
    const dataSql = `
      SELECT 
        a.id as attempt_id,
        a.quiz_id,
        q.title as quiz_title,
        q.category,
        a.user_id,
        u.username,
        a.total_questions,
        a.correct_answers,
        a.score_percentage,
        a.status,
        a.latency_ms,
        a.created_at
      FROM attempts a
      JOIN users u ON a.user_id = u.id
      JOIN quizzes q ON a.quiz_id = q.id
      WHERE ${whereSql}
      ORDER BY a.created_at DESC
      LIMIT ? OFFSET ?
    `;

    const records = await dbAll(dataSql, [...params, pageSize, offset]);

    const latencyMs = Number(process.hrtime.bigint() - start) / 1e6;
    const withinSla = latencyMs <= SLA_LIMITS.PAGE_CHUNK_MS;

    res.json({
      success: true,
      page,
      pageSize,
      totalRecords,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1,
      records,
      latencyMs: Number(latencyMs.toFixed(3)),
      withinSla,
      slaLimitMs: SLA_LIMITS.PAGE_CHUNK_MS
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 7. Audit Logs
app.get('/api/audit-logs', async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit, 10) || 50, 100);
    const logs = await dbAll(`
      SELECT a.id, a.user_id, u.username, a.action, a.detail, a.latency_ms, a.created_at
      FROM audit_logs a
      LEFT JOIN users u ON a.user_id = u.id
      ORDER BY a.created_at DESC LIMIT ?
    `, [limit]);
    res.json({ success: true, logs });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 8. TQM Verification Benchmarks & Database Index Inspector (Q05-F4)
app.get('/api/tqm/benchmarks', async (req, res) => {
  try {
    const indexes = await dbAll(`
      SELECT name, tbl_name, sql FROM sqlite_master 
      WHERE type = 'index' AND name NOT LIKE 'sqlite_autoindex%'
      ORDER BY tbl_name, name
    `);

    // EXPLAIN QUERY PLAN benchmarks
    const testPlans = [
      { label: 'Catalog Search', sql: "EXPLAIN QUERY PLAN SELECT * FROM quizzes WHERE category = 'Quality Management' AND title LIKE '%TQM%'" },
      { label: 'Question Bank Load', sql: "EXPLAIN QUERY PLAN SELECT * FROM questions WHERE quiz_id = 1 ORDER BY id ASC" },
      { label: 'Student Attempt Filter', sql: "EXPLAIN QUERY PLAN SELECT * FROM attempts WHERE user_id = 2 ORDER BY created_at DESC" }
    ];

    const planResults = [];
    for (const test of testPlans) {
      const rows = await dbAll(test.sql);
      const details = rows.map(r => r.detail).join('; ');
      const usesIndex = details.toUpperCase().includes('USING INDEX');
      planResults.push({
        label: test.label,
        details,
        usesIndex
      });
    }

    res.json({
      success: true,
      indexes,
      queryPlans: planResults,
      slaLimits: SLA_LIMITS
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Fallback serve static React app if built
const frontendDist = path.resolve(__dirname, '../frontend/dist');
if (fs.existsSync(frontendDist)) {
  app.use(express.static(frontendDist));
  app.use((req, res) => {
    res.sendFile(path.join(frontendDist, 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`Kahoot/Quizizz TQM Web Server running at http://localhost:${PORT}`);
});
