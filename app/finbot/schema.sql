-- Version 1 schema. Later columns (such as pots.goal_month) and tables (such as budgets)
-- come from the migrations in db.py, not here.
CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('expense','income')), position INTEGER NOT NULL);
CREATE TABLE keywords (word TEXT PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories(id));
CREATE TABLE rates (id INTEGER PRIMARY KEY, currency TEXT NOT NULL CHECK (currency IN ('USD','UAH')),
  eur_per_unit TEXT NOT NULL, set_on TEXT NOT NULL);
CREATE TABLE pots (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, goal_cents INTEGER CHECK (goal_cents > 0));
CREATE TABLE entries (id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('expense','income','save','take')),
  amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
  currency TEXT NOT NULL CHECK (currency IN ('EUR','USD','UAH')),
  rate TEXT, eur_cents INTEGER,
  category_id INTEGER REFERENCES categories(id), pot_id INTEGER REFERENCES pots(id),
  keyword TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '',
  occurred_on TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  deleted_at TEXT,
  CHECK ((kind IN ('save','take')) = (pot_id IS NOT NULL)));
CREATE INDEX entries_on ON entries(occurred_on) WHERE deleted_at IS NULL;
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

INSERT INTO categories (name, kind, position) VALUES
  ('Groceries', 'expense', 1),
  ('Eating out', 'expense', 2),
  ('Transport', 'expense', 3),
  ('Housing', 'expense', 4),
  ('Utilities', 'expense', 5),
  ('Health', 'expense', 6),
  ('Shopping', 'expense', 7),
  ('Entertainment', 'expense', 8),
  ('Travel', 'expense', 9),
  ('Subscriptions', 'expense', 10),
  ('Gifts', 'expense', 11),
  ('Other', 'expense', 12),
  ('Salary', 'income', 1),
  ('Freelance', 'income', 2),
  ('Other income', 'income', 3);
