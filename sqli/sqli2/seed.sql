-- TechBazaar counter stock.
-- Seeded from the FLAG env on every start (see entrypoint.sh); the
-- back-room stock list (vault) is only reachable through search errors.
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    description VARCHAR(255) NOT NULL
);

DELETE FROM products;
INSERT INTO products (name, price, description) VALUES
    ('Bench PSU 12V 5A', 18.90, 'Regulated lab power supply, 12 V at 5 A.'),
    ('Breadboard, 830 tie', 6.40, 'Solderless prototype board, 830 contact points.'),
    ('Soldering iron 60W', 24.50, 'Adjustable-temperature iron with stand.'),
    ('Flux pen, rosin core', 3.20, 'No-clean flux for 0.6-1.0 mm joints.'),
    ('Relay 5V 10A DPDT', 2.85, 'Signal relay, 5 V coil, 10 A contacts.'),
    ('Potentiometer 10k linear', 0.75, 'Panel pot, linear taper, 3-pin.'),
    ('USB-C breakout board', 12.30, 'USB-C to USB 2.0 signals, test points.'),
    ('Terminal block 4-way', 1.10, 'Screw clamp, 4 positions, 21 AWG.'),
    ('Capacitor kit, 100 pcs', 14.95, 'Ceramic and film values, 0.1 uF to 47 uF.'),
    ('Multimeter, true RMS', 42.00, 'Digital multimeter, 6000 counts, RMS.'),
    ('Cable gland M20', 0.95, 'Nylon gland, M20 x 1.5, IP66.'),
    ('Heat shrink, 2:1 set', 8.60, 'Assorted ratios and colours, 200 pieces.');

CREATE TABLE IF NOT EXISTS vault (item VARCHAR(64), secret VARCHAR(128));
DELETE FROM vault;
INSERT INTO vault VALUES ('back-room', '__FLAG__');
