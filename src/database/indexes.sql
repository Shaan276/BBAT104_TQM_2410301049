-- ====================================================================
-- Specialized B-Tree Index Definitions (Quality Goal Q05)
-- Purpose: Eliminate full table scans and achieve <30ms query latency
-- ====================================================================

-- 1. Fast category and quiz title search indexing (Q05-F1 Fast Search)
CREATE INDEX IF NOT EXISTS idx_quizzes_category_title 
ON quizzes (category, title);

-- 2. Instant foreign-key question retrieval by quiz ID
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id 
ON questions (quiz_id);

-- 3. Composite index for candidate attempt verification & reporting
CREATE INDEX IF NOT EXISTS idx_attempts_quiz_user 
ON attempts (quiz_id, user_id);

-- 4. Reverse chronological index for paginated report streaming (Q05-F5)
CREATE INDEX IF NOT EXISTS idx_attempts_created_at_desc 
ON attempts (created_at DESC);
