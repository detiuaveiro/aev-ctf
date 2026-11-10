-- DropLite transfer index.
-- Seeded from the FLAG env on every start (see seed.py); the target file's
-- content is only reachable through the search match-count.
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    size INTEGER NOT NULL,
    content TEXT NOT NULL
);

DELETE FROM files;
INSERT INTO files (name, size, content) VALUES
    ('team-photo-pack.zip', 4821135, 'PK zip archive of the offsite photos'),
    ('invoice-2026-0114.pdf', 88213, 'PDF invoice, net 30, office supplies'),
    ('meeting-notes.docx', 24177, 'Docx notes from the planning meeting'),
    ('quarterly-keys.txt', 61, '__FLAG__'),
    ('site-walkthrough.mp4', 15728640, 'MP4 walkthrough of the new site'),
    ('vendor-contract-draft.docx', 51230, 'Docx draft contract, redlines inline');
