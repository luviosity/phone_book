from pathlib import Path
from typing import Literal
import re
from custom_types import Contact, ContactAdd, ContactUpdate
from tools.file_reader import FileReader
from tools.file_writer import FileWriter
from custom_errors import SaveFileError


class ContactBookModel:
    SEARCH_FIELDS = {1: 'name', 2: 'phone_number', 3: 'comment', 4: 'all'}

    def __init__(self, filename: str):
        self.data: list[Contact] = []
        self._changed: bool = False
        self.file_path: Path = Path(filename)
        self.reader = FileReader(self.file_path)
        self.writer = FileWriter(self.file_path)

    def load_data(self) -> None:
        """Загружает данные с обработкой ошибок"""
        try:
            self.data = self.reader.read()
        except FileNotFoundError:
            # Файл еще не создан
            pass
        except Exception:
            raise

    def get_contact(self, cid: int) -> Contact | None:
        for contact in self.data:
            if cid == contact.id:
                return contact
        return None

    def get_contact_ids(self) -> list[int]:
        return [c.id for c in self.data]

    def find_contact(self,
                     search_term: str,
                     mode_id: Literal['1', '2', '3', '4'] = '4') -> list[Contact]:
        """Поиск контактов с регулярными выражениями"""
        if not search_term.strip():
            return []

        try:
            pattern = re.compile(search_term, re.IGNORECASE)
        except re.error:
            # Если не валидное regex, ищем как подстроку
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)

        def matches(contact: Contact) -> bool:
            mode = self.SEARCH_FIELDS[int(mode_id)]
            if mode == 'all':
                fields = [contact.name, str(contact.phone_number), contact.comment]
                return any(pattern.search(str(field)) for field in fields)
            else:
                value = getattr(contact, mode)
                return bool(pattern.search(str(value)))

        return [contact for contact in self.data if matches(contact)]

    def save_file(self) -> None:
        try:
            self.writer.write(self.data)
            self._changed = False
        except SaveFileError:
            raise

    def is_changed(self) -> bool:
        return self._changed

    def exit_and_save_file(self) -> None:
        if not self._changed:
            return
        save_changes = input('Изменения не сохранены. Сохранить? (Y/n): ') or 'Y'
        if save_changes.lower() == 'y':
            self.save_file()

    def get_all_contacts(self) -> list[Contact]:
        return self.data

    def add_contact(self, contact: ContactAdd) -> None:
        new_id = self.data[-1].id + 1 if self.data else 1
        new_contact = Contact(
            id=new_id,
            name=contact['name'],
            phone_number=contact['phone_number'],
            comment=contact['comment'],
        )
        self.data.append(new_contact)
        self._changed = True

    def edit_contact(self, cid: int, updated_keys: ContactUpdate) -> None:
        contact = self.get_contact(cid)
        if contact is None:
            return

        if 'name' in updated_keys:
            contact.name = updated_keys['name']
            self._changed = True
        if 'phone_number' in updated_keys:
            contact.phone_number = updated_keys['phone_number']
            self._changed = True
        if 'comment' in updated_keys:
            contact.comment = updated_keys['comment']
            self._changed = True


    def delete_contact(self, cid: int) -> None:
        self.data = [c for c in self.data if c.id != cid]
        self._changed = True
