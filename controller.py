from typing import Iterable, Any, Callable
from model import ContactBookModel
from view import ContactBookView
from custom_errors import (
    EmptyValueInInputError,
    NotADigitValueError,
    UnsupportedCommandError,
    FileCorruptedError,
    InvalidFileFormatError,
    ContactLoadError,
    SaveFileError,
    InvalidPhoneNumberError,
    WrongContactIdError
)
from custom_types import Contact


class ContactBookController:
    MAIN_MENU_DICT = {
        1: 'Показать список всех контактов',
        2: 'Создать новый контакт',
        3: 'Редактировать контакт',
        4: 'Найти контакт',
        5: 'Удалить контакт',
        6: 'Сохранить',
        7: 'Выйти из справочника',
        8: 'Показать список доступных команд'
    }

    SEARCH_MENU_DICT = {
        1: 'Имени',
        2: 'Телефону',
        3: 'Комментарию',
        4: 'Всем данным'
    }

    MENU_COMMAND = '/menu'

    def __init__(self, model: ContactBookModel, view: ContactBookView):
        self.model = model
        self.view = view

    def run(self) -> None:
        try:
            self.model.load_data()
        except (FileCorruptedError, InvalidFileFormatError) as e:
            self.view.show_message(f'Ошибка при загрузке справочника: {e}')
            return None
        except ContactLoadError as e:
            self.view.show_message(f'Ошибка при загрузке контактов:\n{e}')
            return None

        self.view.greeting()
        self.view.show_menu(self.MAIN_MENU_DICT)

        while (value := self.view.get_menu_command()) != '7':
            command_options = [str(k) for k in self.MAIN_MENU_DICT]
            try:
                command = self.parse_command_input(value, command_options)
            except (NotADigitValueError, UnsupportedCommandError) as e:
                self.view.show_message(str(e))
                continue

            if command == 1:
                self._handle_show_all_contacts()

            elif command == 2:
                self._handle_add_contact()

            elif command == 3:
                self._handle_edit_contact()

            elif command == 4:
                self._handle_search_contacts()

            elif command == 5:
                self._handle_delete_contact()

            elif command == 6:
                self._handle_save()

            elif command == 8:
                self.view.show_menu(self.MAIN_MENU_DICT)
        else:
            # Выход из приложения
            if self.model.is_changed():
                save = self.view.get_save_file_decision() or 'n'
                if save.lower() == 'y':
                    try:
                        self.model.save_file()
                    except SaveFileError as e:
                        self.view.show_message(f'Упс, что-то пошло не так\n{str(e)}')
                    else:
                        self.view.show_message('Справочник успешно сохранен.')
        return None

    # --------- Обработчики команд (без дублирования логики ввода) ---------

    def _handle_show_all_contacts(self) -> None:
        contacts = self.model.get_all_contacts()
        self.view.show_contacts(contacts)

    def _handle_add_contact(self) -> None:
        """Создание нового контакта с поддержкой /menu на каждом шаге."""
        name = self._input_contact_name()
        if name is None:
            return

        phone_number = self._input_contact_phone_number()
        if phone_number is None:
            return

        comment = self._input_contact_comment()
        if comment is None:
            return

        self.model.add_contact({
            'name': name,
            'phone_number': phone_number,
            'comment': comment
        })
        self.view.show_message(f'Добавлен новый контакт {name}')

    def _handle_edit_contact(self) -> None:
        """Редактирование контакта с возможностью вернуться назад в любой момент."""
        contact_id = self._input_existing_contact_id(self.view.get_contact_id_to_edit)
        if contact_id is None:
            return

        contact = self.model.get_contact(contact_id)
        if contact is None:
            self.view.show_message('Контакт не найден, потому что был удален.')
            return

        new_name = self._input_contact_name(edit_value=contact.name, allow_empty=True)
        if new_name is None:
            return

        new_phone = self._input_contact_phone_number(
            edit_value=contact.phone_number,
            allow_empty=True
        )
        if new_phone is None:
            return

        new_comment = self._input_contact_comment(edit_value=contact.comment, allow_empty=True)
        if new_comment is None:
            return

        updated_keys: dict[str, Any] = {}
        if new_name:
            updated_keys['name'] = new_name
        if new_phone not in (None, ''):
            updated_keys['phone_number'] = new_phone
        if new_comment:
            updated_keys['comment'] = new_comment

        if updated_keys:
            self.model.edit_contact(contact_id, updated_keys)
            self.view.show_message(f'Контакт c ID {contact_id} обновлен.')

    def _handle_search_contacts(self) -> None:
        """Поиск контактов по выбранному полю. /menu доступен везде."""
        self.view.show_menu(self.SEARCH_MENU_DICT)

        search_mode = self._input_search_mode()
        if search_mode is None:
            return

        search_term = self._input_search_term()
        if search_term is None:
            return

        contacts = self.model.find_contact(search_term, search_mode)
        if not contacts:
            self.view.show_message('Совпадений не найдено.')
        else:
            self.view.show_contacts(contacts)

    def _handle_delete_contact(self) -> None:
        """Удаление контакта с поддержкой /menu."""
        contact_id = self._input_existing_contact_id(self.view.get_contact_id_to_delete)
        if contact_id is None:
            return

        contact = self.model.get_contact(contact_id)
        if contact is None:
            self.view.show_message('Контакт не найден, потому что был удален.')
            return

        self.model.delete_contact(contact_id)
        self.view.show_message(f'Контакт с ID {contact_id} успешно удален.')

    def _handle_save(self) -> None:
        try:
            self.model.save_file()
        except SaveFileError as e:
            self.view.show_message(f'Упс, что-то пошло не так\n{str(e)}')
        else:
            self.view.show_message('Справочник успешно сохранен.')

    # --------- Универсальные методы ввода с валидацией и поддержкой /menu ---------

    def _input_contact_name(
        self,
        edit_value: str | None = None,
        allow_empty: bool = False
    ) -> str | None:
        """
        Возвращает:
        - str: валидное имя
        - '' : если allow_empty=True и пользователь оставил пустым (для "не менять")
        - None: если пользователь ввёл /menu
        """
        while True:
            name = self.view.get_contact_name(edit_value=edit_value)
            if name == self.MENU_COMMAND:
                return None

            if not name and allow_empty:
                return ''

            try:
                Contact.validate_name(name)
            except EmptyValueInInputError as e:
                self.view.show_message(str(e))
            else:
                return name

    def _input_contact_phone_number(
        self,
        edit_value: int | None = None,
        allow_empty: bool = False
    ) -> int | str | None:
        """
        Возвращает:
        - int: валидный номер телефона
        - '' : если allow_empty=True и пользователь оставил пустым (для "не менять")
        - None: если пользователь ввёл /menu
        """
        while True:
            raw = self.view.get_contact_phone_number(edit_value=edit_value)
            if raw == self.MENU_COMMAND:
                return None

            try:
                phone = Contact.parse_phone_number(raw)
            except EmptyValueInInputError as e:
                if allow_empty:
                    return ''
                self.view.show_message(str(e))
            except (NotADigitValueError, InvalidPhoneNumberError) as e:
                self.view.show_message(str(e))
            else:
                return phone

    def _input_contact_comment(
        self,
        edit_value: str | None = None,
        allow_empty: bool = True
    ) -> str | None:
        """
        Возвращает:
        - str: комментарий (в т.ч. пустой, если allow_empty=True и нужно "не менять")
        - None: если пользователь ввёл /menu
        """
        comment = self.view.get_contact_comment(edit_value=edit_value)
        if comment == self.MENU_COMMAND:
            return None
        if not comment and allow_empty:
            return ''
        return comment

    def _input_existing_contact_id(
        self,
        id_getter: Callable[[], str]
    ) -> int | None:
        """
        Унифицированный ввод ID контакта (редактирование/удаление) с /menu.
        """
        while True:
            raw = id_getter()
            if raw == self.MENU_COMMAND:
                return None
            try:
                contact_id = self.parse_contact_id_input(raw)
            except (EmptyValueInInputError, NotADigitValueError, WrongContactIdError) as e:
                self.view.show_message(str(e))
            else:
                return contact_id

    def _input_search_mode(self) -> int | None:
        """
        Ввод пункта меню поиска с поддержкой /menu.
        """
        command_options = [str(k) for k in self.SEARCH_MENU_DICT]
        while True:
            value = self.view.get_menu_command()
            if value == self.MENU_COMMAND:
                return None
            try:
                command = self.parse_command_input(value, command_options)
            except (NotADigitValueError, UnsupportedCommandError) as e:
                self.view.show_message(str(e))
            else:
                return command

    def _input_search_term(self) -> str | None:
        """
        Ввод значения для поиска с поддержкой /menu.
        """
        while True:
            value = self.view.get_search_term()
            if value == self.MENU_COMMAND:
                return None
            try:
                self.parse_search_term_input(value)
            except EmptyValueInInputError as e:
                self.view.show_message(str(e))
            else:
                return value

    # --------- Парсеры / валидаторы команд ---------

    @staticmethod
    def parse_command_input(value: str, options: Iterable[str]) -> int:
        if not value.isdigit():
            raise NotADigitValueError('Ввод должен быть положительным числом.')
        if value not in options:
            raise UnsupportedCommandError('Введенная команда не поддерживается.')
        return int(value)

    def parse_contact_id_input(self, value: str) -> int:
        int_value = Contact.parse_contact_id(value)

        if int_value not in self.model.get_contact_ids():
            raise WrongContactIdError('Данный ID не найден.')

        return int_value

    @staticmethod
    def parse_search_term_input(value: str) -> str:
        if not value:
            raise EmptyValueInInputError('Поиск по пустому значению невозможен.')
