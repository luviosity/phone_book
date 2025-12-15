import pytest
from unittest.mock import patch
from model import ContactBookModel
from custom_types import ContactAdd, ContactUpdate


class TestContactBookModel:
    """Тесты для класса ContactBookModel"""

    # ==================== Тесты добавления контакта ====================

    def test_add_contact_to_book(self, contact_book):
        """Должен добавить контакт"""
        contact_data: ContactAdd = {
            'name': 'John',
            'phone_number': 1234567,
            'comment': ''
        }

        contact_book.add_contact(contact_data)

        assert len(contact_book.data) == 3
        assert contact_book.data[2].id == 3
        assert contact_book.data[2].name == 'John'
        assert contact_book.data[2].phone_number == 1234567
        assert contact_book.data[2].comment == ''
        assert contact_book.is_changed() is True

    # ==================== Тесты поиска контакта ====================

    def test_find_contact_by_name(self, contact_book):
        """Должен найти контакты по имени"""
        results = contact_book.find_contact('Alex', mode_id='1')

        assert len(results) == 1
        assert results[0].name == 'Alex'

    def test_find_contact_by_phone_number(self, contact_book):
        """Должен найти контакты по номеру телефона"""
        results = contact_book.find_contact('12345678', mode_id='2')

        assert len(results) == 1
        assert results[0].phone_number == 12345678

    def test_find_contact_by_comment(self, contact_book):
        """Должен найти контакты по комментарию"""
        results = contact_book.find_contact('abc', mode_id='3')

        assert len(results) == 2
        assert results[0].comment == 'abc'
        assert results[1].comment == 'abc'

    def test_find_contact_in_all_fields(self, contact_book):
        """Должен искать по всем полям в режиме 'all'"""
        results = contact_book.find_contact('7', mode_id='4')

        assert len(results) == 2
        assert results[0].name == 'Alex'
        assert results[1].name == 'Bob'

    @pytest.mark.parametrize("mode_id,search_term,expected_count", [
        ('1', 'Alex', 1),  # Поиск по имени
        ('2', '987654321', 1),  # Поиск по телефону
        ('3', 'abc', 2),  # Поиск по комментарию
        ('4', 'Bob', 1),  # Поиск по всем полям
        ('1', 'Tyson', 0),
        ('1', '', 0),
        ('1', 'alex', 1),
        ('1', 'al.*', 1),
        ('1', '[invalid', 0) # Поиск по подстроке
    ])
    def test_find_contact_different_modes(self, contact_book, mode_id, search_term, expected_count):
        """Должен правильно находить контакты в разных режимах поиска"""
        results = contact_book.find_contact(search_term, mode_id=mode_id)

        assert len(results) == expected_count

    # ==================== Тесты изменения контакта ====================

    def test_edit_contact_name(self, contact_book):
        """Должен обновить имя контакта"""
        update_data: ContactUpdate = {'name': 'Александр'}

        contact_book.edit_contact(1, update_data)

        contact = contact_book.get_contact(1)
        assert contact is not None
        assert contact.name == 'Александр'
        assert contact_book.is_changed() is True

    def test_edit_contact_phone_number(self, contact_book):
        """Должен обновить номер телефона контакта"""
        update_data: ContactUpdate = {'phone_number': 99999999}

        contact_book.edit_contact(1, update_data)

        contact = contact_book.get_contact(1)
        assert contact is not None
        assert contact.phone_number == 99999999
        assert contact_book.is_changed() is True

    def test_edit_contact_comment(self, contact_book):
        """Должен обновить комментарий контакта"""
        update_data: ContactUpdate = {'comment': 'Updated comment'}

        contact_book.edit_contact(1, update_data)

        contact = contact_book.get_contact(1)
        assert contact is not None
        assert contact.comment == 'Updated comment'
        assert contact_book.is_changed() is True

    def test_edit_multiple_fields(self, contact_book):
        """Должен обновить несколько полей одновременно"""
        update_data: ContactUpdate = {
            'name': 'NewName',
            'phone_number': 11111111,
            'comment': 'New comment'
        }

        contact_book.edit_contact(1, update_data)

        contact = contact_book.get_contact(1)
        assert contact is not None
        assert contact.name == 'NewName'
        assert contact.phone_number == 11111111
        assert contact.comment == 'New comment'

    def test_edit_nonexistent_contact(self, contact_book):
        """Не должен делать ничего при попытке изменить несуществующий контакт"""
        update_data: ContactUpdate = {'name': 'Test'}
        original_data = contact_book.data.copy()

        contact_book.edit_contact(999, update_data)

        assert contact_book.data == original_data

    # ==================== Тесты удаления контакта ====================

    def test_delete_existing_contact(self, contact_book):
        """Должен удалить контакт из книги"""
        initial_count = len(contact_book.data)

        contact_book.delete_contact(1)

        assert len(contact_book.data) == initial_count - 1
        assert contact_book.get_contact(1) is None
        assert contact_book.is_changed() is True

    def test_delete_nonexistent_contact(self, contact_book):
        """Не должен давать ошибку при удалении несуществующего контакта"""
        initial_count = len(contact_book.data)

        contact_book.delete_contact(999)

        assert len(contact_book.data) == initial_count
        assert contact_book.is_changed() is True

    # ==================== Тесты вспомогательных методов ====================

    def test_get_contact_existing(self, contact_book):
        """Должен вернуть контакт по ID"""
        contact = contact_book.get_contact(1)

        assert contact is not None
        assert contact.id == 1
        assert contact.name == 'Alex'

    def test_get_contact_nonexistent(self, contact_book):
        """Должен вернуть None для несуществующего ID"""
        contact = contact_book.get_contact(999)

        assert contact is None

    def test_get_all_contacts(self, contact_book):
        """Должен вернуть все контакты"""
        contacts = contact_book.get_all_contacts()

        assert len(contacts) == 2
        assert contacts[0].id == 1
        assert contacts[1].id == 2

    def test_get_contact_ids(self, contact_book):
        """Должен вернуть список всех ID контактов"""
        ids = contact_book.get_contact_ids()

        assert ids == [1, 2]

    # ==================== Тесты загрузки/сохранения ====================

    def test_load_data_from_nonexistent_file(self, tmp_path):
        """Не должен давать ошибку при загрузке из несуществующего файла"""
        file_path = tmp_path / 'nonexist.json'
        book = ContactBookModel(str(file_path))
        book.load_data()

        assert book.data == []

    def test_save_file(self, contact_book):
        """Должен сохранить контакты в файл"""
        import json
        contact_data: ContactAdd = {
            'name': 'Test',
            'phone_number': 1234567,
            'comment': 'test'
        }
        contact_book.add_contact(contact_data)

        contact_book.save_file()

        assert contact_book.is_changed() is False

        with open(contact_book.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[2]['name'] == 'Test'
