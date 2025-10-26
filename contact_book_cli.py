from contact_book import ContactBook
from textwrap import dedent
from typing import Callable


class ContactBookCLI:
    """Консольный интерфейс для работы с телефонным справочником."""

    MENU = dedent('''\
        Доступные команды:
            1. Показать список всех контактов
            2. Создать новый контакт
            3. Редактировать контакт
            4. Найти контакт
            5. Удалить контакт
            6. Сохранить
            7. Выйти из справочника
        Введите номер команды: ''')

    SEARCH_MENU = dedent('''\
        Искать контакт по:
            1. Имени
            2. Телефону
            3. Комментарию
            4. Всем данным
        Введите номер команды: ''')

    SEARCH_FIELDS = {1: 'name', 2: 'phone_number', 3: 'comment', 4: 'all'}

    def __init__(self, filename: str):
        self.contact_book = ContactBook(filename)
        self.commands: dict[int, Callable] = {
            1: self.show_all,
            2: self.create_contact,
            3: self.edit_contact,
            4: self.find_contact,
            5: self.delete_contact,
            6: self.save,
            7: self.exit,
        }

    def run(self) -> None:
        print('Добро пожаловать в телефонный справочник.')

        while True:
            command = self._get_int_input(self.MENU, max(self.commands.keys()))
            if command is None:
                continue

            handler = self.commands.get(command)
            if handler is None:
                print('Введенная команда не поддерживается.')
                continue

            if handler() == 'exit':
                break

    @staticmethod
    def _get_int_input(prompt: str, number_of_options: int) -> int:
        """Получить целочисленный ввод с валидацией."""
        while True:
            user_input = input(prompt).strip()
            if not user_input.isdigit():
                print('Ввод должен быть положительным числом.')
                continue
            int_user_input = int(user_input)
            if int_user_input < 1 or int_user_input > number_of_options:
                print('Введенная команда не поддерживается.')
                continue
            return int_user_input

    @staticmethod
    def _get_phone_input(prompt: str = 'Введите телефон (без знака "+"): ') -> int:
        """Получить и валидировать номер телефона."""
        while True:
            phone = input(prompt).strip()
            if not phone:
                print('Номер не может быть пустым.')
                continue

            if not phone.isdigit():
                print('Номер должен содержать только цифры.')
                continue

            if not (7 <= len(phone) <= 15):
                print('Номер должен содержать от 7 до 15 цифр.')
                continue

            return int(phone)

    def show_all(self) -> None:
        """Показать все контакты."""
        self.contact_book.show_all_contacts()

    def create_contact(self) -> None:
        """Создать новый контакт."""
        name = input('Введите имя: ').strip()
        phone_number = self._get_phone_input()
        comment = input('Введите комментарий: ').strip()

        self.contact_book.add_contact({
            'name': name,
            'phone_number': phone_number,
            'comment': comment
        })
        print(f'Добавлен новый контакт {name}')

    def edit_contact(self) -> None:
        """Редактировать существующий контакт."""
        contact_id = self._get_int_input(
            'Введите ID контакта, который хотите изменить: '
        )

        contact = self.contact_book.get_contact(contact_id)
        if contact is None:
            print('Контакт не найден.')
            return

        new_name = input(f'Введите новое имя [{contact["name"]}]: ').strip()
        new_phone = self._get_phone_input(f'Введите новый телефон [{contact["phone_number"]}]: ')
        new_comment = input(f'Введите новый комментарий [{contact["comment"]}]: ').strip()

        updated_keys = {}
        if new_name:
            updated_keys['name'] = new_name
        if new_phone:
            updated_keys['phone_number'] = new_phone
        if new_comment:
            updated_keys['comment'] = new_comment

        if updated_keys:
            self.contact_book.edit_contact(contact_id, updated_keys)

    def find_contact(self) -> None:
        """Найти контакт по различным критериям."""
        mode = self._get_int_input(self.SEARCH_MENU, max(self.SEARCH_FIELDS.keys()))

        value = input('Введите значение: ').strip()
        contacts = self.contact_book.find_contact(value, self.SEARCH_FIELDS[mode])

        if not contacts:
            print('Совпадений не найдено.')
        else:
            self.contact_book.show_contact(contacts)

    def delete_contact(self) -> None:
        """Удалить один или несколько контактов."""
        contact_ids_str = input(
            'Введите ID контактов, которые хотите удалить '
            '(множественные ID вводите через запятую): '
        ).strip()

        try:
            contact_ids = [int(c.strip()) for c in contact_ids_str.split(',')]
            if contact_ids:
                self.contact_book.delete_contact(contact_ids)
        except ValueError:
            print('Допускаются только числовые значения, которые можно перечислить через запятые.')

    def save(self) -> None:
        """Сохранить изменения."""
        self.contact_book.save_file()

    def exit(self) -> str:
        """Выйти из приложения."""
        self.contact_book.save_file()
        return 'exit'


if __name__ == '__main__':
    pass
    # cli = ContactBookCLI('data.json')
    # cli.run()