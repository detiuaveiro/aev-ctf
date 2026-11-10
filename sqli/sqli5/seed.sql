-- The Daily Byte archive.
-- Seeded from the FLAG env on every start (see seed.py); the editor's
-- note (vault) is only reachable through the tag filter's marker line.
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    tag TEXT NOT NULL,
    posted TEXT NOT NULL
);

DELETE FROM posts;
INSERT INTO posts (title, tag, posted) VALUES
    ('Why we keep the lab offline', 'net', '2026-09-30'),
    ('A week with the new rack', 'ops', '2026-09-27'),
    ('The printer incident', 'bytes', '2026-09-25'),
    ('Measuring what actually matters', 'bytes', '2026-09-21'),
    ('Cable management, a love letter', 'net', '2026-09-18'),
    ('On-call notes from a quiet month', 'ops', '2026-09-15'),
    ('The daily byte goes to print', 'bytes', '2026-09-11'),
    ('Switch firmware, one more time', 'net', '2026-09-08'),
    ('Restoring the tape archive', 'ops', '2026-09-04'),
    ('Small tools, sharp edges', 'bytes', '2026-09-01'),
    ('The fibre run under the stairwell', 'net', '2026-08-28'),
    ('What we broke on purpose (and learned)', 'ops', '2026-08-24');

CREATE TABLE IF NOT EXISTS vault (item TEXT, secret TEXT);
DELETE FROM vault;
INSERT INTO vault VALUES ('editor-note', '__FLAG__');
