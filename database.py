import sqlite3

#==========================================================================================================================================
#Другие данные

valentine_random_text = [
    "Самому светлому человечку",
    "Ты моя прелесть",
    "Свети всегда, Свети везде!",
    "Моей путеводной звезде!",
    "Улыбайся! И будет тебе счастье!",
    "Самому солнечному Человеку!",
    "Рядом с тобой мир становится ярче!",
    "С тобой каждый день — праздник!",
    "Maxitet! Ты – лучшее, что когда-либо случалось со мной!",
    "Спасибо за то, что ты есть!",
    "Ты лучше всех!",
    "Генератору идей",
    "Главному двигателю прогресса!",
    "Не останавливайся на достигнутом!",
    "Самому прекрасному человечку!",
    "От всего большого сердца!",
    "С наилучшими пожеланиями!",
    "От меня тебе!",
    "Потусим?)"
    ]


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
            user_name_from TEXT,
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
        """, (user_id, key[0]))

    conn.commit()
    conn.close()
    return resently_registred, val_keys

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
        return False, None
    else:
        return True, existing_user[0]

def check_ref_user_in_db(ref_url):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_ref = ?", (ref_url,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        return None
    else:
        return existing_user[0],

def get_user_id_by_name(user_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_name = ?", (user_name,))
    existing_user_id = cursor.fetchone()
    if existing_user_id is None:
        return None
    else:
        return existing_user_id[0]

def get_valentine_by_key(valentine_key):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT valentine_text FROM valentines WHERE valentine_key = ?""", (valentine_key,))
    valentine_text = cursor.fetchall()

    cursor.execute("""
    SELECT user_name_from FROM valentines WHERE valentine_key = ?""", (valentine_key,))
    valentine_name_from = cursor.fetchall()

    cursor.execute("""
    SELECT user_id_from FROM valentines WHERE valentine_key = ?""", (valentine_key,))
    user_id_from = cursor.fetchall()

    conn.close()
    return (
        valentine_name_from[0] if valentine_name_from else None,
        valentine_text[0] if valentine_text else None,
        user_id_from[0] if user_id_from else None
    )

def set_state_valentine_delivered(valentine_key):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE valentines
    SET valentine_delivered = True
    WHERE valentine_key = ?""", (valentine_key,))

    conn.commit()
    conn.close()

#==========================================================================================================================================
# Обмен валентинками
def send_valentine_to_db(user_id_from, user_name_to, valentine_text, valentine_anonim: bool, valentine_delivered: bool, user_name_from, user_id_to: None):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    if isinstance(user_name_to, tuple):
        user_name_to = user_name_to[0]
    if isinstance(user_id_from, tuple):
        user_id_from = user_id_from[0]
    if isinstance(user_id_to, tuple):
        user_id_to = user_id_to[0]
    if isinstance(user_name_from, tuple):
        user_name_from = user_name_from[0]

    cursor.execute("INSERT INTO valentines (user_id_from, user_name_to, user_id_to, valentine_text, valentine_anonim, valentine_delivered, user_name_from) VALUES(?,?,?,?,?,?,?)",
                   (user_id_from, user_name_to, user_id_to, valentine_text, valentine_anonim, valentine_delivered, user_name_from))

    cursor.execute("""
            UPDATE users
            SET valentine_sent_count = valentine_sent_count + 1
            WHERE user_id = ?;
        """, (user_id_from,))

    conn.commit()
    conn.close()

#==========================================================================================================================================
# Счетчики

def add_counter_sent(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET valentine_sent_count = valentine_sent_count + 1
    WHERE user_id = ?;
    """, (user_id,))

    conn.commit()
    conn.close()

def add_counter_get(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET valentine_get_count = valentine_get_count + 1
    WHERE user_id = ?;""", (user_id,))

    conn.commit()
    conn.close()


# print(len(valentine_random_text))
