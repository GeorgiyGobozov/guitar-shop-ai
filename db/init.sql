CREATE TABLE tickets (
    id              BIGSERIAL PRIMARY KEY,
    customer_name   VARCHAR(120) NOT NULL,
    customer_email  VARCHAR(120) NOT NULL,
    subject         VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,

    ml_category     VARCHAR(40),
    ml_priority     VARCHAR(20),
    ml_problem_type VARCHAR(40),
    ml_confidence   DOUBLE PRECISION,

    status          VARCHAR(20) NOT NULL DEFAULT 'NEW',
    assignee        VARCHAR(120),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tickets_status   ON tickets(status);
CREATE INDEX idx_tickets_category ON tickets(ml_category);

CREATE TABLE products (
    id     BIGSERIAL PRIMARY KEY,
    name   VARCHAR(200) NOT NULL,
    brand  VARCHAR(100),
    kind   VARCHAR(40),
    price  NUMERIC(10,2) NOT NULL,
    stock  INT NOT NULL DEFAULT 0
);

INSERT INTO products (name, brand, kind, price, stock) VALUES
  ('Fender Player Stratocaster', 'Fender',  'electric',  89990.00, 4),
  ('Gibson Les Paul Standard',   'Gibson',  'electric', 249990.00, 1),
  ('Yamaha F310',                'Yamaha',  'acoustic',  12990.00, 20),
  ('Taylor 114e',                'Taylor',  'acoustic',  74990.00, 3),
  ('Cordoba C5',                 'Cordoba', 'classical', 29990.00, 7),
  ('Ibanez SR300E',              'Ibanez',  'bass',      39990.00, 5),
  ('Dunlop Tortex 0.88',         'Dunlop',  'accessory',   120.00, 500);