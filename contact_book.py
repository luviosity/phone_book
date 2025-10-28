import json
from pathlib import Path
from typing import TypedDict, NotRequired, Literal
from textwrap import dedent
import re


class Contact(TypedDict):
    id: int
    name: str
    phone_number: int
    comment: str

class ContactUpdate(TypedDict):
    name: NotRequired[str]
    phone_number: NotRequired[int]
    comment: NotRequired[str]

class ContactAdd(TypedDict):
    name: str
    phone_number: int
    comment: str

class SaveFileError(Exception):
    pass

class CreateEmptyBookError(Exception):
    pass


class ContactBook:
    def __init__(self, filename: str):
        self.data: list[Contact] = []
        self.changed: bool = False
        self.file_path: Path = Path(filename)
        self._ensure_file_exists()
        self.data = self._read_data()

    def _ensure_file_exists(self) -> None:
        """Создает пустой справочник, если он еще не существует"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                self.file_path.touch()
                print(f"Пустой справочник создан по пути: {self.file_path}")
        except OSError as e:
            raise CreateEmptyBookError(f"Ошибка в создании пустого справочника по пути {self.file_path}.\n {e}")

    def get_contact(self, cid: int) -> Contact | None:
        for contact in self.data:
            if cid == contact['id']:
                return contact
        return None

    def get_contact_ids(self):
        return [c['id'] for c in self.data]

    def find_contact(self, search_term: str,
                     mode: Literal['name', 'phone_number', 'comment', 'all'] = 'all') -> list[Contact]:
        """Поиск контактов с регулярными выражениями"""
        if not search_term.strip():
            return []

        try:
            pattern = re.compile(search_term, re.IGNORECASE)
        except re.error:
            # Если не валидное regex, ищем как подстроку
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)

        def matches(contact: Contact) -> bool:
            if mode == 'all':
                fields = [str(contact['name']), str(contact['phone_number']), str(contact['comment'])]
                return any(pattern.search(str(field)) for field in fields)
            else:
                return bool(pattern.search(str(contact[mode])))

        return [contact for contact in self.data if matches(contact)]

    def _read_data(self) -> list[Contact]:
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print('Файл поврежден или пуст.')
            return []

    def save_file(self) -> None:
        self._ensure_file_exists()
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file, ensure_ascii=False)
            print('Файл сохранен.')
            self.changed = False
        except Exception as e:
            raise SaveFileError(f'Невозможно сохранить файл.\n {e}')

    def exit_and_save_file(self) -> None:
        if not self.changed:
            return
        save_changes = input('Изменения не сохранены. Сохранить? (Y/n): ') or 'Y'
        if save_changes.lower() == 'y':
            self.save_file()

    @staticmethod
    def show_contact(contacts: Contact | list[Contact]) -> None:
        if isinstance(contacts, dict):
            contacts = [contacts]
        tmp: str = dedent('''
            ID: {id}
            Имя: {name}
            Телефон: {phone_number}
            Комментарий: {comment}
        ''')
        print('\n***\n'.join([tmp.format(**c) for c in contacts]))

    def show_all_contacts(self) -> None:
        self.show_contact(self.data)

    def add_contact(self, contact: ContactAdd) -> None:
        contact['id'] = self.data[-1]['id'] + 1 if self.data else 1
        self.data.append(contact)
        print('Новый контакт добавлен.')
        self.changed = True

    def edit_contact(self, cid: int, updated_keys: ContactUpdate) -> None:
        contact = self.get_contact(cid)
        contact.update(updated_keys)
        print(f'Контакт c ID {cid} обновлен.')
        self.changed = True

    def delete_contact(self, cids: int | list[int]) -> None:
        if isinstance(cids, int):
            cids = [cids]

        cids_set = set(cids)
        initial_count = len(self.data)
        self.data = [c for c in self.data if c['id'] not in cids_set]
        deleted_count = initial_count - len(self.data)

        print(f'Удалено контактов: {deleted_count}')
        if deleted_count > 0:
            self.changed = True
