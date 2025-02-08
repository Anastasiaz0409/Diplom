import os
import xml.etree.ElementTree as ET
from diffie_hellman import generate_dh_keypair, G, P

XML_FILENAME = "dh_keys.xml"
# Загружает или создает XML-файл для хранения ключей.
def load_keys_xml():
    """
    Загружаем или создаём XML-файл dh_keys.xml со структурой:
      <Keys>
        <User id="X">
          <PrivateKey>...</PrivateKey>
        </User>
        ...
      </Keys>
    Возвращаем корневой элемент (Element).
    """
    if os.path.isfile(XML_FILENAME):
        try:
            tree = ET.parse(XML_FILENAME)
            root = tree.getroot()
        except Exception as e:
            print("Ошибка парсинга XML, создаём новый файл.", e)
            root = ET.Element("Keys")
            tree = ET.ElementTree(root)
            tree.write(XML_FILENAME, encoding="utf-8", xml_declaration=True)
    else:
        root = ET.Element("Keys")
        tree = ET.ElementTree(root)
        tree.write(XML_FILENAME, encoding="utf-8", xml_declaration=True)
    return root
# Сохраняет изменения в XML-файле.
def save_keys_xml(root):
    """
    Сохраняем переданный root (Element) в dh_keys.xml
    """
    tree = ET.ElementTree(root)
    tree.write(XML_FILENAME, encoding="utf-8", xml_declaration=True)
# Ищет данные пользователя в XML-файле.
def find_user_element(root, user_id):
    """
    Ищем <User id="user_id"> в XML
    """
    for user_el in root.findall("User"):
        if user_el.get("id") == str(user_id):
            return user_el
    return None
# Проверяет наличие приватного ключа для пользователя.
# Если ключа нет, генерирует новый и сохраняет его в XML.
def load_or_create_private_key_in_xml(user_id):
    """
    Ищем приватный ключ для user_id в dh_keys.xml.
    Если нет, генерируем (priv, pub) и записываем.
    Возвращаем (priv, pub).
    """
    root = load_keys_xml()

    user_el = find_user_element(root, user_id)
    if user_el is not None:
        priv_str = user_el.find("PrivateKey").text
        priv = int(priv_str)
        pub = pow(G, priv, P)
        return priv, pub
    else:
        priv, pub = generate_dh_keypair()
        user_el = ET.SubElement(root, "User", attrib={"id": str(user_id)})
        pk_el = ET.SubElement(user_el, "PrivateKey")
        pk_el.text = str(priv)
        save_keys_xml(root)
        return priv, pub