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

        try:
            while True:
                command = self._get_int_input(self.MENU, range(1, max(self.commands.keys()) + 1))
                if command is None:
                    continue

                handler = self.commands.get(command)
                if handler is None:
                    print('Введенная команда не поддерживается.')
                    continue

                if handler() == 'exit':
                    break
        except KeyboardInterrupt:
            print()
            self.exit()

    @staticmethod
    def keyboard_interrupt_handler(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                print('Чтобы выйти назад нажмите Ctrl+C в терминале.')
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print()
                return None
        return wrapper

    @staticmethod
    def _get_int_input(prompt: str, options: list[int], error_msg = 'Введенная команда не поддерживается.') -> int:
        """Получить целочисленный ввод с валидацией."""
        while True:
            user_input = input(prompt).strip()
            if not user_input.isdigit():
                print('Ввод должен быть положительным числом.')
                continue
            int_user_input = int(user_input)
            if int_user_input not in options:
                print(error_msg)
                continue
            return int_user_input

    @staticmethod
    def _get_phone_input(prompt: str = 'Введите телефон (без знака "+"): ', allow_empty: bool = False) -> int:
        """Получить и валидировать номер телефона."""
        while True:
            phone = input(prompt).strip()
            if allow_empty and phone == '':
                return phone
            else:
                if phone == '':
                    print('Значение не может быть пустым.')
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

    @keyboard_interrupt_handler
    def create_contact(self) -> None:
        """Создать новый контакт."""
        while True:
            name = input('Введите имя: ').strip()
            if name == '':
                print('Значение не может быть пустым.')
                continue
            break
        phone_number = self._get_phone_input()
        comment = input('Введите комментарий: ').strip()

        self.contact_book.add_contact({
            'name': name,
            'phone_number': phone_number,
            'comment': comment
        })
        print(f'Добавлен новый контакт {name}')

    @keyboard_interrupt_handler
    def edit_contact(self) -> None:
        """Редактировать существующий контакт."""
        contact_id = self._get_int_input(
            'Введите ID контакта, который хотите изменить: ',
            options=self.contact_book.get_contact_ids(),
            error_msg='Данный ID не найден.'
        )

        contact = self.contact_book.get_contact(contact_id)
        if contact is None:
            print('Контакт не найден.')
            return

        new_name = input(f'Введите новое имя [{contact["name"]}]: ').strip()
        new_phone = self._get_phone_input(f'Введите новый телефон [{contact["phone_number"]}]: ', allow_empty=True)
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

    @keyboard_interrupt_handler
    def find_contact(self) -> None:
        """Найти контакт по различным критериям."""
        mode = self._get_int_input(self.SEARCH_MENU, range(1, max(self.SEARCH_FIELDS.keys()) + 1))

        value = input('Введите значение: ').strip()
        contacts = self.contact_book.find_contact(value, self.SEARCH_FIELDS[mode])

        if not contacts:
            print('Совпадений не найдено.')
        else:
            self.contact_book.show_contact(contacts)

    @keyboard_interrupt_handler
    def delete_contact(self) -> None:
        """Удалить контакт."""
        contact_id = self._get_int_input(
            'Введите ID контакта, который хотите удалить: ',
            options=self.contact_book.get_contact_ids(),
            error_msg='Данный ID не найден.'
        )

        self.contact_book.delete_contact(contact_id)

    def save(self) -> None:
        """Сохранить изменения."""
        self.contact_book.save_file()

    def exit(self) -> str:
        """Выйти из приложения."""
        self.contact_book.exit_and_save_file()
        return 'exit'


if __name__ == '__main__':
    cli = ContactBookCLI('data.json')
    cli.run()