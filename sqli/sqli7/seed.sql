-- Linkly's saved links.
-- Seeded from the FLAG env on every start (see seed.py); the vault row is
-- only reachable through the preview query.
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);

DELETE FROM links;
INSERT INTO links (url, note) VALUES
    ('https://example.com/', 'The example domain, for testing'),
    ('https://www.ietf.org/', 'IETF homepage'),
    ('https://sqlite.org/', 'SQLite documentation');

CREATE TABLE IF NOT EXISTS vault (item TEXT, secret TEXT);
DELETE FROM vault;
INSERT INTO vault VALUES ('outbox', '__FLAG__');
