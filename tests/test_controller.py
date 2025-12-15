import pytest
from unittest.mock import Mock
from controller import ContactBookController
from custom_errors import (
    NotADigitValueError,
    UnsupportedCommandError,
    WrongContactIdError,
    EmptyValueInInputError,
    SaveFileError
)


class TestContactBookController:
    """Тесты для класса ContactBookController"""

    @pytest.fixture
    def mock_model(self, sample_contacts):
        """Фикстура для мокирования модели"""
        model = Mock()
        model.get_all_contacts.return_value = sample_contacts
        model.get_contact_ids.return_value = [1, 2]
        model.is_changed.return_value = False
        return model

    @pytest.fixture
    def mock_view(self):
        """Фикстура для мокирования представления"""
        view = Mock()
        return view

    @pytest.fixture
    def controller(self, mock_model, mock_view):
        """Фикстура для создания контроллера"""
        return ContactBookController(mock_model, mock_view)

    # ==================== Тесты для парсеров ====================

    def test_parse_command_input_not_digit(self, controller):
        """Должен вызвать ошибку если команда не является числом"""
        with pytest.raises(NotADigitValueError):
            controller.parse_command_input('abc', ['1', '2', '3'])

    def test_parse_command_input_unsupported(self, controller):
        """Должен вызвать ошибку если команда не поддерживается"""
        with pytest.raises(UnsupportedCommandError):
            controller.parse_command_input('5', ['1', '2', '3'])

    @pytest.mark.parametrize("value,options,expected", [
        ('1', ['1', '2', '3'], 1),
        ('2', ['1', '2', '3'], 2),
        ('8', ['1', '2', '3', '4', '5', '6', '7', '8'], 8),
    ])
    def test_parse_command_input_various_valid_commands(self, controller, value, options, expected):
        """Должен правильно парсить различные валидные команды"""
        result = controller.parse_command_input(value, options)

        assert result == expected

    def test_parse_contact_id_input_valid(self, controller):
        """Должен правильно распарсить валидный ID контакта"""
        result = controller.parse_contact_id_input('2')

        assert result == 2

    def test_parse_contact_id_input_not_found(self, controller):
        """Должен вызвать ошибку если ID не найден"""
        with pytest.raises(WrongContactIdError):
            controller.parse_contact_id_input('99')

    def test_parse_contact_id_input_empty(self, controller):
        """Должен вызвать ошибку если ID пустой"""
        with pytest.raises(EmptyValueInInputError):
            controller.parse_contact_id_input('')

    def test_parse_contact_id_input_not_digit(self, controller):
        """Должен вызвать ошибку если ID не является числом"""
        with pytest.raises(NotADigitValueError):
            controller.parse_contact_id_input('abc')

    def test_parse_search_term_input_valid(self, controller):
        """Должен правильно распарсить валидный поисковый запрос"""
        # Метод не возвращает значение, только валидирует
        # Если не бросает исключение - значит валидация прошла успешно
        controller.parse_search_term_input('Alex')  # Не должно быть исключения

    def test_parse_search_term_input_empty(self, controller):
        """Должен вызвать ошибку если поисковый запрос пустой"""
        with pytest.raises(EmptyValueInInputError):
            controller.parse_search_term_input('')

    # ==================== Тесты для обработчиков команд ====================

    def test_handle_show_all_contacts(self, controller, mock_model, mock_view, sample_contacts):
        """Должен показать все контакты"""
        controller._handle_show_all_contacts()

        mock_model.get_all_contacts.assert_called_once()
        mock_view.show_contacts.assert_called_once_with(sample_contacts)

    def test_handle_save_success(self, controller, mock_model, mock_view):
        """Должен успешно сохранить файл"""
        controller._handle_save()

        mock_model.save_file.assert_called_once()
        mock_view.show_message.assert_called_once_with('Справочник успешно сохранен.')

    def test_handle_save_error(self, controller, mock_model, mock_view):
        """Должен показать ошибку при неудачном сохранении"""
        mock_model.save_file.side_effect = SaveFileError('Test error')

        controller._handle_save()

        mock_model.save_file.assert_called_once()
        mock_view.show_message.assert_called_once_with('Упс, что-то пошло не так\nTest error')

    def test_handle_add_contact_success(self, controller, mock_model, mock_view):
        """Должен добавить новый контакт"""
        mock_view.get_contact_name.return_value = 'John'
        mock_view.get_contact_phone_number.return_value = '1234567'
        mock_view.get_contact_comment.return_value = 'Test comment'

        controller._handle_add_contact()

        mock_model.add_contact.assert_called_once_with({
            'name': 'John',
            'phone_number': 1234567,
            'comment': 'Test comment'
        })
        mock_view.show_message.assert_called_once_with('Добавлен новый контакт John')

    def test_handle_delete_contact_success(self, controller, mock_model, mock_view):
        """Должен удалить контакт"""
        mock_view.get_contact_id_to_delete.return_value = '1'
        mock_model.get_contact.return_value = mock_model.get_all_contacts()[0]

        controller._handle_delete_contact()

        mock_model.delete_contact.assert_called_once_with(1)
        mock_view.show_message.assert_called_once_with('Контакт с ID 1 успешно удален.')

    def test_handle_delete_contact_not_found(self, controller, mock_model, mock_view):
        """Должен показать сообщение если контакт не найден"""
        mock_view.get_contact_id_to_delete.return_value = '1'
        mock_model.get_contact.return_value = None

        controller._handle_delete_contact()

        mock_model.delete_contact.assert_not_called()
        mock_view.show_message.assert_called_once_with('Контакт не найден, потому что был удален.')

    def test_handle_search_contacts_success(self, controller, mock_model, mock_view, sample_contacts):
        """Должен найти и показать контакты"""
        mock_view.get_menu_command.return_value = '1'
        mock_view.get_search_term.return_value = 'Alex'
        mock_model.find_contact.return_value = [sample_contacts[0]]

        controller._handle_search_contacts()

        mock_model.find_contact.assert_called_once_with('Alex', 1)
        mock_view.show_contacts.assert_called_once_with([sample_contacts[0]])

    def test_handle_search_contacts_no_matches(self, controller, mock_model, mock_view):
        """Должен показать сообщение если совпадений не найдено"""
        mock_view.get_menu_command.return_value = '1'
        mock_view.get_search_term.return_value = 'NonExistent'
        mock_model.find_contact.return_value = []

        controller._handle_search_contacts()

        mock_view.show_message.assert_called_once_with('Совпадений не найдено.')
        mock_view.show_contacts.assert_not_called()

    def test_handle_edit_contact_success(self, controller, mock_model, mock_view):
        """Должен обновить контакт"""
        contact = mock_model.get_all_contacts()[0]
        new_name = 'Aleksandr'
        new_phone_number = '99999999'
        new_comment = 'Updated'
        mock_view.get_contact_id_to_edit.return_value = '1'
        mock_model.get_contact.return_value = contact
        mock_view.get_contact_name.return_value = new_name
        mock_view.get_contact_phone_number.return_value = new_phone_number
        mock_view.get_contact_comment.return_value = new_comment

        controller._handle_edit_contact()

        mock_model.edit_contact.assert_called_once_with(1, {
            'name': new_name,
            'phone_number': int(new_phone_number),
            'comment': new_comment
        })
        mock_view.show_message.assert_called_once_with('Контакт c ID 1 обновлен.')

    def test_handle_edit_contact_partial_update(self, controller, mock_model, mock_view):
        """Должен обновить только заполненные поля"""
        contact = mock_model.get_all_contacts()[0]
        mock_view.get_contact_id_to_edit.return_value = '1'
        mock_model.get_contact_ids.return_value = [1, 2]
        mock_model.get_contact.return_value = contact
        new_name = 'Aleksandr'
        mock_view.get_contact_name.return_value = new_name
        mock_view.get_contact_phone_number.return_value = ''
        mock_view.get_contact_comment.return_value = ''

        controller._handle_edit_contact()

        mock_model.edit_contact.assert_called_once()
        mock_model.edit_contact.assert_called_once_with(1, {
            'name': new_name,
        })

    def test_handle_edit_contact_no_changes(self, controller, mock_model, mock_view):
        """Не должен вызывать edit_contact если нет изменений"""
        contact = mock_model.get_all_contacts()[0]
        mock_view.get_contact_id_to_edit.return_value = '1'
        mock_model.get_contact_ids.return_value = [1, 2]
        mock_model.get_contact.return_value = contact
        mock_view.get_contact_name.return_value = ''
        mock_view.get_contact_phone_number.return_value = ''
        mock_view.get_contact_comment.return_value = ''

        controller._handle_edit_contact()

        mock_model.edit_contact.assert_not_called()

    def test_handle_edit_contact_not_found(self, controller, mock_model, mock_view):
        """Должен показать сообщение если контакт не найден"""
        mock_view.get_contact_id_to_edit.return_value = '1'
        mock_model.get_contact_ids.return_value = [1, 2]
        mock_model.get_contact.return_value = None

        controller._handle_edit_contact()

        mock_model.edit_contact.assert_not_called()
        mock_view.show_message.assert_called_once_with('Контакт не найден, потому что был удален.')

    # ==================== Тесты для методов валидации ввода ====================

    def test_input_contact_name_valid(self, controller, mock_view):
        """Должен вернуть валидное имя"""
        mock_view.get_contact_name.return_value = 'John'

        result = controller._input_contact_name()

        assert result == 'John'

    def test_input_contact_name_empty_not_allowed(self, controller, mock_view):
        """Должен повторять запрос при пустом имени если not allow_empty"""
        mock_view.get_contact_name.side_effect = ['', 'John']

        result = controller._input_contact_name(allow_empty=False)

        assert result == 'John'
        assert mock_view.get_contact_name.call_count == 2

    def test_input_contact_name_empty_allowed(self, controller, mock_view):
        """Должен вернуть пустую строку если allow_empty=True"""
        mock_view.get_contact_name.return_value = ''

        result = controller._input_contact_name(allow_empty=True)

        assert result == ''

    def test_input_contact_phone_number_valid(self, controller, mock_view):
        """Должен вернуть валидный номер телефона"""
        mock_view.get_contact_phone_number.return_value = '1234567'

        result = controller._input_contact_phone_number()

        assert result == 1234567

    def test_input_contact_phone_number_invalid_then_valid(self, controller, mock_view):
        """Должен повторять запрос при невалидном номере"""
        mock_view.get_contact_phone_number.side_effect = ['abc', '1234567']

        result = controller._input_contact_phone_number()

        assert result == 1234567
        assert mock_view.get_contact_phone_number.call_count == 2

    def test_input_contact_comment_valid(self, controller, mock_view):
        """Должен вернуть валидный комментарий"""
        mock_view.get_contact_comment.return_value = 'Test comment'

        result = controller._input_contact_comment()

        assert result == 'Test comment'
