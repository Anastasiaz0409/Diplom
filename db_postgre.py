# db_postgre.py

import datetime
import sqlalchemy as db
from sqlalchemy import Text  # Импорт для текстового поля

from Crypto.Random import get_random_bytes
import binascii

# Настройте подключение к PostgreSQL под свои параметры
engine = db.create_engine("postgresql://postgres:12345678@localhost:5432/ChatMCHS", echo=True)
conn = engine.connect()
Meta_data = db.MetaData() # для описания структуры таблиц


Users = db.Table('Users', Meta_data,
                 db.Column('user_id', db.Integer, primary_key=True),
                 db.Column('username', db.String(50)),
                 db.Column('password_hash', db.String(50)),
                 db.Column('role', db.String(50)),
                 db.Column('fio', db.String(50)),
                 db.Column('create_at', db.TIMESTAMP),
                 db.Column('update_at', db.TIMESTAMP),
                 )

Chats = db.Table('Chats', Meta_data,
                 db.Column('chat_id', db.Integer, primary_key=True),
                 db.Column('chat_name', db.String(100)),
                 db.Column('is_group', db.Boolean),
                 db.Column('created_by', db.Integer, db.ForeignKey('Users.user_id')),
                 db.Column('created_at', db.TIMESTAMP)
                 )

ChatPartic = db.Table('ChatPartic', Meta_data,
                      db.Column('chat_id', db.Integer, db.ForeignKey('Chats.chat_id')),
                      db.Column('user_id', db.Integer, db.ForeignKey('Users.user_id')),
                      db.Column('joined_at', db.TIMESTAMP)
                      )

Messages = db.Table('Messages', Meta_data,
                    db.Column('message_id', db.Integer, primary_key=True, autoincrement=True),
                    db.Column('chat_id', db.Integer, db.ForeignKey('Chats.chat_id')),
                    db.Column('user_id', db.Integer, db.ForeignKey('Users.user_id')),
                    db.Column('content', db.LargeBinary),
                    db.Column('timestamp', db.TIMESTAMP)
                    )

PublicKeys = db.Table('PublicKeys', Meta_data,
                      db.Column('user_id', db.Integer, db.ForeignKey('Users.user_id'), primary_key=True),
                      db.Column('public_key', db.Text),
                      db.Column('updated_at', db.TIMESTAMP)
                      )

# Изменили тип поля aes_key_enc на Text для хранения ключа в шестнадцатеричном формате.
ChatKeys = db.Table('ChatKeys', Meta_data,
                    db.Column('chat_id', db.Integer, db.ForeignKey('Chats.chat_id'), primary_key=True),
                    db.Column('aes_key', Text),
                    db.Column('created_at', db.TIMESTAMP)
                    )

Meta_data.create_all(engine)

#Загружает всех пользователей и возвращает их данные в виде словаря.
def logining():
    """
    Загружаем всех пользователей из таблицы Users.
    Ключ формируется как "<username> <password_hash>".
    Возвращаем словарь: ключ -> [user_id, role, fio, created_at, updated_at]
    """
    results = conn.execute(db.select(Users)).fetchall()
    login_pass = {}
    for r in results:
        key = r[1] + ' ' + r[2]
        login_pass[key] = [r[0], r[3], r[4], r[5], r[6]]
    return login_pass

# Сохраняет публичный ключ пользователя в таблицу PublicKeys.
# Если запись уже существует, обновления не выполняются.
def store_public_key(user_id, pubkey_str):
    now = datetime.datetime.now()
    sel = db.select(PublicKeys).where(PublicKeys.c.user_id == user_id)
    row = conn.execute(sel).fetchone()
    if row:
        # Запись уже существует – при необходимости можно обновлять
        pass
    else:
        ins = db.insert(PublicKeys).values(
            user_id=user_id,
            public_key=pubkey_str,
            updated_at=now
        )
        conn.execute(ins)
        conn.commit()
        print(f"Сохранён публичный ключ для user_id={user_id}")

# Возвращает публичный ключ пользователя по его user_id.
def get_public_key(user_id):
    sel = db.select(PublicKeys.c.public_key).where(PublicKeys.c.user_id == user_id)
    row = conn.execute(sel).fetchone()
    if row:
        return row[0]
    return None

# Возвращает список user_id участников чата.
def get_chat_participants(chat_id):
    sel = db.select(ChatPartic.c.user_id).where(ChatPartic.c.chat_id == chat_id)
    rows = conn.execute(sel).fetchall()
    return [r[0] for r in rows]

#Генерирует 32-байтовый ключ для чата, сохраняет его в таблицу ChatKeys в виде строки
def create_chat_key(chat_id):
    """
    Создаёт новый публичный ключ для группового чата:
     - Генерируется 32-байтный ключ.
     - Ключ преобразуется в шестнадцатеричную строку для хранения.
     - Сохраняется в таблицу ChatKeys.
    После создания функция возвращает сгенерированный ключ в виде байтов.
    Используется конструкция with engine.begin(), чтобы гарантировать commit транзакции.
    """
    now = datetime.datetime.now()
    raw_key = get_random_bytes(32)
    # Преобразуем ключ в шестнадцатеричное представление (тип str)
    key_hex = binascii.hexlify(raw_key).decode('utf-8')

    # Используем транзакцию для гарантированного commit
    with engine.begin() as connection:
        stmt = db.insert(ChatKeys).values(
            chat_id=chat_id,
            aes_key=key_hex,
            created_at=now
        )
        connection.execute(stmt)

    # Проверяем, что запись появилась
    sel = db.select(ChatKeys).where(ChatKeys.c.chat_id == chat_id)
    row = conn.execute(sel).fetchone()
    if row:
        print(f"[create_chat_key] Ключ для группового чата chat_id={chat_id} успешно создан.")
        return raw_key
    else:
        print(f"[create_chat_key] Ошибка: запись ключа не создана для chat_id={chat_id}.")
        return None

# Получает ключ для чата, преобразуя его из шестнадцатеричного формата обратно в байты.
def get_chat_key(chat_id):
    """
    Получает ключ для группового чата:
     - Извлекается шестнадцатеричная строка из таблицы ChatKeys.
     - Преобразуется обратно в байты.
    """
    sel = db.select(ChatKeys.c.aes_key).where(ChatKeys.c.chat_id == chat_id)
    row = conn.execute(sel).fetchone()
    if not row:
        return None
    key_hex = row[0]
    try:
        raw_key = binascii.unhexlify(key_hex)
        return raw_key
    except Exception as e:
        print(f"[get_chat_key] Ошибка преобразования ключа: {e}")
        return None

# Возвращает список чатов, где участвует пользователь, с их последними активностями
def chats_for_user(user_id):
    sql = db.select(Chats.c.chat_id, Chats.c.chat_name, Chats.c.is_group) \
        .select_from(Chats.join(ChatPartic)) \
        .where(ChatPartic.c.user_id == user_id)
    rows = conn.execute(sql).fetchall()
    result = []
    for (cid, cname, is_group) in rows:
        sel_ts = db.select(db.func.max(Messages.c.timestamp)).where(Messages.c.chat_id == cid)
        last_ts = conn.execute(sel_ts).scalar()
        if not last_ts:
            last_ts = datetime.datetime(1900, 1, 1)
        result.append((cid, cname, is_group, last_ts))
    result.sort(key=lambda x: x[3], reverse=True)
    return result

# Сохраняет зашифрованное сообщение в таблицу Messages.
def send_mess(chat_id, user_id, ciphertext, time_str):
    ins = db.insert(Messages).values(
        chat_id=chat_id,
        user_id=user_id,
        content=ciphertext,
        timestamp=time_str
    )
    conn.execute(ins)
    conn.commit()
    print(f"Отправлено сообщение в чат {chat_id} от user_id {user_id}")

# Извлекает все сообщения для указанного чата, упорядоченные по времени.
def get_messages(chat_id):
    sel = db.select(Messages.c.user_id, Messages.c.content, Messages.c.timestamp) \
        .where(Messages.c.chat_id == chat_id) \
        .order_by(Messages.c.timestamp.asc())
    rows = conn.execute(sel).fetchall()
    return rows
# отвечает за получение имени пользователя
def get_username(user_id):
    sel = db.select(Users.c.fio).where(Users.c.user_id == user_id)
    row = conn.execute(sel).fetchone()
    return row[0] if row else str(user_id)