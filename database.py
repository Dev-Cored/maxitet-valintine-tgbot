import sqlite3

#==========================================================================================================================================
#Запуск базы данных
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_key integer PRIMARY KEY UNIQUE,
        user_id INTEGER UNIQUE,
        user_name TEXT,
        user_ref TEXT UNIQUE,
        valentine_get_count INTEGER,
        valentine_sent_count INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS valentines (
        valentine_key INTEGER PRIMARY KEY UNIQUE,
        user_id_from INTEGER,
        user_id_to INTEGER,
        valentine_text TEXT,
        valentine_anonim BOOLEAN    
    )''')

    conn.commit()
    conn.close()


#==========================================================================================================================================
# Стартовые процедуры
def reg_start_user(user_id, user_name, ref_url):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (user_id, user_name, valentine_get_count, valentine_sent_count, user_ref) VALUES(?,?,?,?,?)",
                   (user_id, user_name, 0, 0, ref_url))

    conn.commit()
    conn.close()

def search_valentines_register(user_name, user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT valentine_key FROM valentines WHERE user_name = ?", (user_name,))
    val_keys = cursor.fetchall()

    for i in val_keys:
        cursor.execute("""
        UPDATE valentines
        SET user_id_to = user_id
        WHERE valentine_key = ?
        """), (i)

    conn.commit()
    conn.close()
#==========================================================================================================================================
# Обмен валентинками
def send_valentines(user_id_from, user_name_to, user_id_to, valentine_text, valentine_anonim: bool):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO valentines (user_id_from, user_name_to, user_id_to, valentine_text, valentine_anonim) VALUES(?,?,?,?,?)",
                   (user_id_from, user_name_to, user_id_to, valentine_text, valentine_anonim))

    cursor.execute("""
            UPDATE users
            SET valentine_sent_count = valentine_sent_count + 1
            WHERE user_id = ?;
        """, (user_id_from,))

    conn.commit()
    conn.close()