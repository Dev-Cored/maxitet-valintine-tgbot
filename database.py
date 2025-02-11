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
            user_name_to TEXT,
            valentine_text TEXT,
            valentine_anonim BOOLEAN,
            valentine_delivered BOOLEAN
        )
    ''')

    conn.commit()
    conn.close()


#==========================================================================================================================================
#Стартовые процедуры
def reg_start_user(user_id, user_name, ref_url):
    resently_registred = False

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    # Проверяем, есть ли уже такой пользователь
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        # Добавляем нового пользователя
        cursor.execute("""
            INSERT INTO users (user_id, user_name, valentine_get_count, valentine_sent_count, user_ref) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, user_name, int(0), int(0), ref_url))
        conn.commit()
        resently_registred = True

    # Проверяем, есть ли "валентинки" для этого user_name
    cursor.execute("SELECT valentine_key FROM valentines WHERE user_name_to = ?", (user_name,))
    val_keys = cursor.fetchall()

    for key in val_keys:
        cursor.execute("""
            UPDATE valentines
            SET user_id_to = ?
            WHERE valentine_key = ?
        """, (user_id, key[0]))  # key - это кортеж, поэтому берём key[0]

    conn.commit()
    conn.close()
    return resently_registred

#==========================================================================================================================================
# Инструменты
def get_user_ref(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_ref FROM users WHERE user_id = ?", (user_id,))
    ref = cursor.fetchone()
    return ref[0]

    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()



    cursor.execute("SELECT valentine_sent_count FROM users WHERE user_id = ?", (user_id,))
    sent_count = cursor.fetchone()
    cursor.execute("SELECT valentine_get_count FROM users WHERE user_id = ?", (user_id,))
    get_count = cursor.fetchone()

    conn.close()
    return sent_count[0], get_count[0]

def check_user_id_db(user_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (user_name,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        return False
    else:
        return True
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

