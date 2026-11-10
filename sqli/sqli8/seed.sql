-- TransferOps Console seed — loaded by entrypoint.sh as the 'app' DB user
-- over loopback TCP, with the live FLAG env interpolated into __FLAG__.
-- Contract: IDEMPOTENT (CREATE TABLE IF NOT EXISTS + delete/insert) so a
-- re-run within a container's lifetime is safe.
--
-- The console only ever shows the three fleet tables below. The writer,
-- however, takes the table name from the request — and there is one more
-- table in appdb that the console never renders.
CREATE TABLE IF NOT EXISTS transfers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route VARCHAR(64) NOT NULL,
    volume INT NOT NULL,
    status VARCHAR(16) NOT NULL
);
CREATE TABLE IF NOT EXISTS routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    region VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS queues (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    depth INT NOT NULL
);

DELETE FROM transfers;
INSERT INTO transfers (route, volume, status) VALUES
    ('fra -> ams', 812, 'done'),
    ('ams -> nyc', 224, 'done'),
    ('nyc -> sgp', 641, 'in-flight'),
    ('sgp -> syd', 133, 'done'),
    ('syd -> fra', 907, 'queued'),
    ('fra -> nyc', 455, 'done');

DELETE FROM routes;
INSERT INTO routes (name, region) VALUES
    ('trans-atlantic', 'nyc <-> ams'),
    ('trans-pacific',  'nyc <-> sgp'),
    ('europe-loop',    'fra <-> ams'),
    ('asia-loop',      'sgp <-> syd');

DELETE FROM queues;
INSERT INTO queues (name, depth) VALUES
    ('ingest', 12),
    ('normalise', 4),
    ('dispatch', 0),
    ('retry', 7);

CREATE TABLE IF NOT EXISTS vault (label VARCHAR(64), secret VARCHAR(128));
DELETE FROM vault;
INSERT INTO vault VALUES ('outbox', '__FLAG__');
