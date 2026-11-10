-- PhotoVault library.
-- Seeded from the FLAG env on every start (see seed.py); the `vault` row
-- is only reachable through the photo detail query.
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    caption TEXT NOT NULL,
    src TEXT NOT NULL
);

DELETE FROM photos;
INSERT INTO photos (title, caption, src) VALUES
    ('Harbour at dawn', 'The fishing boats come in before the market opens.', 'harbour.jpg'),
    ('Old tram line', 'Platform two, exactly as the postcards remember it.', 'tram.jpg'),
    ('Wet market', 'Row after row of greens under the striped awnings.', 'market.jpg'),
    ('Night ferry', 'The last crossing, lights smearing across the water.', 'ferry.jpg'),
    ('Rooftop garden', 'Someone plants tomatoes three storeys above the street.', 'rooftop.jpg'),
    ('The long stair', 'One hundred and twelve steps to the river gate.', 'stair.jpg'),
    ('Bicycle shed', 'Forty bikes, one umbrella, and a cat.', 'bikes.jpg'),
    ('Lighthouse walk', 'The cliff path, on the morning the fog lifted late.', 'lighthouse.jpg');

CREATE TABLE IF NOT EXISTS vault (item TEXT, secret TEXT);
DELETE FROM vault;
INSERT INTO vault VALUES ('darkroom', '__FLAG__');
