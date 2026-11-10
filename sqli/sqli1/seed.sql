-- Staff Portal roster.
-- Seeded from the FLAG env on every start (see seed.py); the admin row's
-- `notice` is the IT announcement that carries the flag.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    notice TEXT NOT NULL DEFAULT ''
);

DELETE FROM users;
INSERT INTO users (username, password, role, notice) VALUES
    ('admin', 'S3cret!2026', 'administrator', '__FLAG__'),
    ('mara', 'bluejay7', 'shift lead', 'Printer on the 3rd floor is back online.'),
    ('theo', 'kettle99', 'on-call', 'Patch window Friday 02:00-04:00.'),
    ('iris', 'lantern5', 'on-call', 'New badge reader in the north lobby.');
