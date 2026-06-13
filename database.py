import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            is_ai BOOLEAN DEFAULT FALSE,
            elo INTEGER DEFAULT 1000,
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            corrupt_count INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            winner TEXT,
            winner_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_players (
            game_id INTEGER,
            user_id TEXT,
            role TEXT,
            is_alive BOOLEAN DEFAULT TRUE,
            died_at_round INTEGER,
            elo_change INTEGER DEFAULT 0,
            PRIMARY KEY (game_id, user_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (user_id) REFERENCES players(user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            round_num INTEGER,
            event_type TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_memories (
            bot_id TEXT,
            target_id INTEGER,
            suspicion_score REAL DEFAULT 0.0,
            last_interaction TIMESTAMP,
            PRIMARY KEY (bot_id, target_id)
        )
    ''')
    
    conn.commit()
    migrate_schema(conn)
    conn.close()

def migrate_schema(conn):
    cursor = conn.cursor()

    cols = {row[1]: row[2] for row in cursor.execute('PRAGMA table_info(players)')}
    if cols.get('user_id') != 'TEXT':
        cursor.execute('''
            CREATE TABLE players_new (
                user_id TEXT PRIMARY KEY, username TEXT, is_ai BOOLEAN DEFAULT FALSE,
                elo INTEGER DEFAULT 1000, games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('INSERT INTO players_new SELECT * FROM players')
        cursor.execute('DROP TABLE players')
        cursor.execute('ALTER TABLE players_new RENAME TO players')

    cols = {row[1]: row[2] for row in cursor.execute('PRAGMA table_info(game_players)')}
    if cols.get('user_id') != 'TEXT':
        cursor.execute('''
            CREATE TABLE game_players_new (
                game_id INTEGER, user_id TEXT, role TEXT,
                is_alive BOOLEAN DEFAULT TRUE, died_at_round INTEGER,
                elo_change INTEGER DEFAULT 0,
                PRIMARY KEY (game_id, user_id),
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        cursor.execute('INSERT INTO game_players_new SELECT * FROM game_players')
        cursor.execute('DROP TABLE game_players')
        cursor.execute('ALTER TABLE game_players_new RENAME TO game_players')

    cols = {row[1]: row[2] for row in cursor.execute('PRAGMA table_info(games)')}
    if cols.get('winner_id') != 'TEXT':
        cursor.execute('''
            CREATE TABLE games_new (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER,
                corrupt_count INTEGER, start_time TIMESTAMP, end_time TIMESTAMP,
                winner TEXT, winner_id TEXT
            )
        ''')
        cursor.execute('INSERT INTO games_new SELECT * FROM games')
        cursor.execute('DROP TABLE games')
        cursor.execute('ALTER TABLE games_new RENAME TO games')

    conn.commit()

def save_player(user_id, username, is_ai=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO players (user_id, username, is_ai)
        VALUES (?, ?, ?)
    ''', (str(user_id), username, is_ai))
    conn.commit()
    conn.close()

def update_player_elo(user_id, elo_change):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE players SET elo = elo + ? WHERE user_id = ?', (elo_change, str(user_id)))
    conn.commit()
    conn.close()

def increment_player_stats(user_id, won):
    conn = get_connection()
    cursor = conn.cursor()
    if won:
        cursor.execute('''
            UPDATE players SET games_played = games_played + 1, wins = wins + 1 
            WHERE user_id = ?
        ''', (str(user_id),))
    else:
        cursor.execute('UPDATE players SET games_played = games_played + 1 WHERE user_id = ?', (str(user_id),))
    conn.commit()
    conn.close()

def get_player(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (str(user_id),))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_leaderboard(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, elo, games_played, wins 
        FROM players 
        WHERE is_ai = FALSE 
        ORDER BY elo DESC 
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def create_game(chat_id, corrupt_count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO games (chat_id, corrupt_count, start_time)
        VALUES (?, ?, ?)
    ''', (chat_id, corrupt_count, datetime.now()))
    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return game_id

def end_game(game_id, winner, winner_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE games SET end_time = ?, winner = ?, winner_id = ?
        WHERE game_id = ?
    ''', (datetime.now(), winner, str(winner_id) if winner_id else None, game_id))
    conn.commit()
    conn.close()

def add_game_player(game_id, user_id, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_players (game_id, user_id, role)
        VALUES (?, ?, ?)
    ''', (game_id, str(user_id), role))
    conn.commit()
    conn.close()

def kill_player(game_id, user_id, round_num):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_players SET is_alive = FALSE, died_at_round = ?
        WHERE game_id = ? AND user_id = ?
    ''', (round_num, game_id, str(user_id)))
    conn.commit()
    conn.close()

def get_game_players(game_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT gp.*, p.username, p.is_ai
        FROM game_players gp
        JOIN players p ON gp.user_id = p.user_id
        WHERE gp.game_id = ?
    ''', (game_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def get_alive_players(game_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT gp.*, p.username, p.is_ai
        FROM game_players gp
        JOIN players p ON gp.user_id = p.user_id
        WHERE gp.game_id = ? AND gp.is_alive = TRUE
    ''', (game_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def get_alive_corrupt(game_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT gp.*, p.username, p.is_ai
        FROM game_players gp
        JOIN players p ON gp.user_id = p.user_id
        WHERE gp.game_id = ? AND gp.is_alive = TRUE 
        AND gp.role IN ('Blackout', 'Razor', 'Phantom', 'Thug')
    ''', (game_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def log_game_event(game_id, round_num, event_type, details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_log (game_id, round_num, event_type, details)
        VALUES (?, ?, ?, ?)
    ''', (game_id, round_num, event_type, json.dumps(details)))
    conn.commit()
    conn.close()

def get_game_log(game_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM game_log WHERE game_id = ? ORDER BY round_num, timestamp
    ''', (game_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def update_ai_memory(bot_id, target_id, suspicion_delta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_memories (bot_id, target_id, suspicion_score, last_interaction)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(bot_id, target_id) 
        DO UPDATE SET suspicion_score = suspicion_score + ?,
                     last_interaction = ?
    ''', (bot_id, target_id, suspicion_delta, datetime.now(), suspicion_delta, datetime.now()))
    conn.commit()
    conn.close()

def get_ai_memories(bot_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT target_id, suspicion_score FROM ai_memories WHERE bot_id = ?', (bot_id,))
    results = cursor.fetchall()
    conn.close()
    return {str(r['target_id']): r['suspicion_score'] for r in results}

def get_player_game_history(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.*, gp.role, gp.is_alive, gp.died_at_round, gp.elo_change
        FROM games g
        JOIN game_players gp ON g.game_id = gp.game_id
        WHERE gp.user_id = ?
        ORDER BY g.start_time DESC
        LIMIT ?
    ''', (str(user_id), limit))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")