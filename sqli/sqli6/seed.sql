-- Guestbook entries.
-- Seeded from the FLAG env on every start (see entrypoint.sh); the
-- back-room secret (vault) is only reachable through the note insert.
CREATE TABLE IF NOT EXISTS guestbook (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    message TEXT,
    signed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DELETE FROM guestbook;
INSERT INTO guestbook (name, message, signed_at) VALUES
    ('Mara', 'Thanks for fixing the projector before the demo!', '2026-10-01 09:14:00'),
    ('Theo', 'The new coffee machine is a miracle of engineering.', '2026-10-03 16:42:00'),
    ('Iris', 'Quiet shift, no pager. Sign it and send it back.', '2026-10-07 22:05:00');

CREATE TABLE IF NOT EXISTS vault (item VARCHAR(64), secret VARCHAR(128));
DELETE FROM vault;
INSERT INTO vault VALUES ('back-room', '__FLAG__');
