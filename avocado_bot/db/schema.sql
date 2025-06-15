PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS current_war(
  war_date TEXT, player_tag TEXT, name TEXT,
  decks_used INTEGER, fame INTEGER, score INTEGER, donations INTEGER,
  PRIMARY KEY(war_date,player_tag)
);
CREATE TABLE IF NOT EXISTS war_history AS SELECT * FROM current_war WHERE 0;