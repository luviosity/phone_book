from textwrap import dedent
from custom_types import Contact
from typing import Iterable


class ContactBookView:
    @staticmethod
    def greeting() -> None:
        print('Добро пожаловать в телефонный справочник.')

    @staticmethod
    def show_menu(command_dict: dict[int, str]) -> None:
        menu_items = '\n    '.join([f'{key}. {value}' for key, value in command_dict.items()])
        text = f'''\
Доступные команды:
    {menu_items}
'''
        print(text)

    @staticmethod
    def _get_user_input(text: str) -> str:
        return input(text).strip()

    def get_menu_command(self):
        return self._get_user_input('Введите номер команды: ')

    def get_contact_name(self, edit_value: str | None = None) -> str:
        base = 'Введите имя'
        suffix = f' [{edit_value}]' if edit_value else ''
        return self._get_user_input(f'{base}{suffix}: ')

    def get_contact_comment(self, edit_value: str | None = None) -> str:
        base = 'Введите комментарий'
        suffix = f' [{edit_value}]' if edit_value else ''
        return self._get_user_input(f'{base}{suffix}: ')

    def get_contact_phone_number(self, edit_value: int | None = None) -> str:
        base = 'Введите телефон (без знака "+")'
        suffix = f' [{edit_value}]' if edit_value else ''
        return self._get_user_input(f'{base}{suffix}: ')

    def get_contact_id_to_delete(self) -> str:
        return self._get_user_input('Введите ID контакта, который хотите удалить: ')

    def get_contact_id_to_edit(self) -> str:
        return self._get_user_input('Введите ID контакта, который хотите изменить: ')

    def get_search_term(self) -> str:
        return self._get_user_input('Введите значение для поиска: ')

    def get_save_file_decision(self) -> str:
        return self._get_user_input('Изменения не сохранены. Сохранить? (Y/n): ')

    @staticmethod
    def show_message(message: str) -> None:
        print(message)

    @staticmethod
    def show_contacts(contacts: Iterable[Contact]) -> None:
        if not contacts:
            print('Список контактов пуст')
        tmp: str = dedent('''
            ID: {id}
            Имя: {name}
            Телефон: {phone_number}
            Комментарий: {comment}
        ''')
        print('\n***\n'.join([tmp.format(**c.to_dict()) for c in contacts]))
