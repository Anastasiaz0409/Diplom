# main.py

import sys
import datetime

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget

import db_postgre
from Main_logining import Ui_Logining
from Messager import Ui_Form_Mess
from diffie_hellman import compute_shared_secret, derive_aes_key
from crypto_AES import encrypt_gost_AES, decrypt_gost_AES
from key_storage import load_or_create_private_key_in_xml  # Единый файл для всех приватных ключей

# Глобальные переменные для идентификатора пользователя и его приватного ключа
user_id = 0
MY_PRIVATE_KEY = None  # Приватный ключ текущего пользователя

def dat_time():
    return str(datetime.datetime.now()).split('.')[0]
#  реализует окно входа в систему.
class App_mess(QWidget):
    # Инициализирует окно мессенджера.
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form_Mess()
        self.ui.setupUi(self)

        self.ui.but_Find_chat.clicked.connect(self.findChats)
        self.ui.but_Find_mess.clicked.connect(self.findMess)
        self.ui.but_Send.clicked.connect(self.sending)

        self.chats_model = QtGui.QStandardItemModel()
        self.ui.list_Compan.setModel(self.chats_model)
        self.ui.list_Compan.clicked.connect(self.select_chat)

        self.msgs_model = QtGui.QStandardItemModel()
        self.ui.list_Chat.setModel(self.msgs_model)

        self.ui.find_Companion.setPlaceholderText('найти чат')
        self.ui.find_Chat.setPlaceholderText('найти сообщение')
        self.ui.messages.setPlaceholderText('пишите сообщение')

        self.current_chat_id = None
        self.dict_chat_keys = {}  # словарь: chat_id -> AES-ключ

        self.load_chats()

    def load_chats(self):
        print("Загрузка списка чатов...")
        self.chats_model.clear()
        c_list = db_postgre.chats_for_user(user_id)
        for (cid, cname, is_group, last_ts) in c_list:
            txt = f"{cname} [{'GROUP' if is_group else '2P'}] {last_ts}"
            item = QtGui.QStandardItem(txt)
            item.setData((cid, cname, is_group))
            self.chats_model.appendRow(item)
# Обрабатывает выбор чата.
    def select_chat(self, index):
        item = self.chats_model.itemFromIndex(index)
        if not item:
            return
        (chat_id_, chat_name, is_group) = item.data()
        self.current_chat_id = chat_id_
        print(f"Выбран чат: {chat_name} (id={chat_id_}, group={is_group})")

        # 1) Гарантируем что у всех участников есть (priv, pub)
        participants = db_postgre.get_chat_participants(chat_id_)
        print(f"Участники чата: {participants}")

        for pid in participants:
            exist_pub = db_postgre.get_public_key(pid)
            if not exist_pub:
                # Загружаем или создаём ключи (используем user_id из БД)
                priv_, pub_ = load_or_create_private_key_in_xml(pid)
                db_postgre.store_public_key(pid, str(pub_))
                print(f"Автоматически созданы ключи для user_id={pid}")
            else:
                # Даже если публичный ключ есть, для демонстрации пытаемся загрузить приватный
                priv_, pub_ = load_or_create_private_key_in_xml(pid)
                # Не выводим сообщение для остальных

        # 2) Формирование AES-ключа для данного чата
        if chat_id_ not in self.dict_chat_keys:
            if not is_group and len(participants) == 2:
                # Двусторонний чат: вычисляем E2E-ключ
                other = participants[0] if participants[0] != user_id else participants[1]
                other_pub_str = db_postgre.get_public_key(other)
                if not other_pub_str:
                    print("У второго участника отсутствует публичный ключ!")
                    return
                other_pub = int(other_pub_str)
                global MY_PRIVATE_KEY
                shared = compute_shared_secret(MY_PRIVATE_KEY, other_pub)
                aes_key = derive_aes_key(shared)
                self.dict_chat_keys[chat_id_] = aes_key
                print(f"Сформирован E2E-ключ для чата {chat_id_}")
            else:
                # Групповой чат: ключ больше не шифруется
                k = db_postgre.get_chat_key(chat_id_)
                if not k:
                    k = db_postgre.create_chat_key(chat_id_)
                self.dict_chat_keys[chat_id_] = k
                print(f"Получен (или создан) общий публичный ключ для группового чата {chat_id_}")

        self.load_messages()
# Загружает список чатов пользователя.
    def load_messages(self):
        self.msgs_model.clear()
        if not self.current_chat_id:
            return
        aes_key = self.dict_chat_keys.get(self.current_chat_id)
        if not aes_key:
            print("Нет ключа для чата, не могу расшифровать сообщения")
            return
        msgs = db_postgre.get_messages(self.current_chat_id)
        for (uid, enc_content, ts) in msgs:
            try:
                dec_data = decrypt_gost_AES(aes_key, enc_content)
                text = dec_data.decode('utf-8')
            except Exception as e:
                text = "[Ошибка расшифровки]"
            username = db_postgre.get_username(uid)
            item = QtGui.QStandardItem(f"{username}\n{ts}\n{text}")
            self.msgs_model.appendRow(item)

    def sending(self):
        if not self.current_chat_id:
            print("Чат не выбран, сообщение не отправляется.")
            return
        aes_key = self.dict_chat_keys.get(self.current_chat_id)
        if not aes_key:
            print("Нет ключа для чата, сообщение не отправляется!")
            return
        msg_text = self.ui.messages.toPlainText().strip()
        if not msg_text:
            return
        ct = encrypt_gost_AES(aes_key, msg_text.encode('utf-8'))
        db_postgre.send_mess(self.current_chat_id, user_id, ct, dat_time())
        self.ui.messages.clear()
        self.load_messages()

    def findChats(self):
        val = self.ui.find_Companion.text().lower()
        for r in range(self.chats_model.rowCount()):
            it = self.chats_model.item(r)
            if val in it.text().lower():
                idx = self.chats_model.indexFromItem(it)
                self.ui.list_Compan.setCurrentIndex(idx)
                self.select_chat(idx)
                return

    def findMess(self):
        val = self.ui.find_Chat.text().lower()
        for r in range(self.msgs_model.rowCount()):
            it = self.msgs_model.item(r)
            if val in it.text().lower():
                idx = self.msgs_model.indexFromItem(it)
                self.ui.list_Chat.setCurrentIndex(idx)
                return
# Инициализирует окно мессенджера.
class App_main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Logining()
        self.ui.setupUi(self)
        self.ui.But_entr.clicked.connect(self.buttonClicked)
        self.ui.Login.setPlaceholderText('логин')
        self.ui.Password.setPlaceholderText('пароль')
# Обрабатывает вход пользователя.
    def buttonClicked(self):
        global user_id, MY_PRIVATE_KEY
        login_text = self.ui.Login.text().strip()
        pass_text = self.ui.Password.text().strip()
        key_for_check = login_text + ' ' + pass_text
        print(f"Попытка входа: {key_for_check}")

        try:
            login_pass = db_postgre.logining()
            if key_for_check in login_pass:
                dd = login_pass[key_for_check]
                user_id_ = dd[0]
                user_id = user_id_
                print(f"Успешный вход, user_id={user_id_}")

                # 1) Загружаем или создаём приватный ключ для пользователя (xml-файл использует id из БД)
                priv, pub = load_or_create_private_key_in_xml(user_id_)
                MY_PRIVATE_KEY = priv

                # 2) Если в БД отсутствует публичный ключ, сохраняем его
                exist_pub = db_postgre.get_public_key(user_id_)
                if not exist_pub:
                    db_postgre.store_public_key(user_id_, str(pub))
                    print(f"Публичный ключ для user_id={user_id_} сохранён: {pub}")
                else:
                    print(f"Публичный ключ для user_id={user_id_} уже присутствует.")

                # После успешного входа скрываем окно логина и открываем окно мессенджера
                self.hide()
                self.mess = App_mess()
                self.mess.show()
            else:
                self.ui.label_error.setText("Неверный логин или пароль!")
                print("Неверный логин или пароль!")
        except Exception as e:
            print("Ошибка при входе:", e)
            self.ui.label_error.setText("Ошибка при входе! Смотрите консоль.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = App_main()
    main_window.show()
    sys.exit(app.exec_())
