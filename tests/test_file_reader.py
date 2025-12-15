import pytest
import json
from custom_errors import FileCorruptedError, InvalidFileFormatError, ContactLoadError
from tools import FileReader


class TestFileReader:
    """Тесты для класса FileReader"""

    def test_read_raises_not_found_when_file_missing(self, tmp_path):
        """Должен вызвать FileNotFoundError если файл не существует"""
        file_path = tmp_path / 'nonexistent.json'
        reader = FileReader(file_path)

        with pytest.raises(FileNotFoundError):
            reader.read()

    def test_read_raises_invalid_format_when_not_list(self, tmp_path):
        """Должен вызвать InvalidFileFormatError если JSON не является списком"""
        file_path = tmp_path / 'not_list.json'
        file_path.write_text('{"id": 1, "name": "Alex"}', encoding='utf-8')
        reader = FileReader(file_path)

        with pytest.raises(InvalidFileFormatError):
            reader.read()

    def test_read_raises_contact_load_error_when_invalid_contact_data(self, tmp_path):
        """Должен вызвать ContactLoadError если данные контакта невалидны"""
        file_path = tmp_path / 'invalid_contact.json'
        invalid_data = [
            {"id": 1, "name": "Alex"}  # Отсутствуют обязательные поля
        ]
        file_path.write_text(json.dumps(invalid_data), encoding='utf-8')
        reader = FileReader(file_path)

        with pytest.raises(ContactLoadError):
            reader.read()

    def test_read_returns_contacts_from_valid_file(self, tmp_path, sample_contacts):
        """Должен успешно прочитать и распарсить валидные данные контактов"""
        file_path = tmp_path / 'contacts.json'
        data = [contact.to_dict() for contact in sample_contacts]
        file_path.write_text(json.dumps(data), encoding='utf-8')
        reader = FileReader(file_path)

        contacts = reader.read()

        assert len(contacts) == 2
        assert contacts[0].id == 1
        assert contacts[0].name == 'Alex'
        assert contacts[0].phone_number == 12345678
        assert contacts[0].comment == 'abc'
        assert contacts[1].id == 2
        assert contacts[1].name == 'Bob'
        assert contacts[1].phone_number == 987654321
        assert contacts[1].comment == 'abc'

    def test_read_returns_empty_list_when_file_contains_empty_list(self, tmp_path):
        """Должен вернуть пустой список если файл содержит валидный пустой JSON-массив"""
        file_path = tmp_path / 'empty_list.json'
        file_path.write_text('[]', encoding='utf-8')
        reader = FileReader(file_path)

        contacts = reader.read()

        assert contacts == []

    def test_read_skips_non_dict_items_in_list(self, tmp_path):
        """Должен пропускать элементы которые не являются словарями"""
        file_path = tmp_path / 'mixed_types.json'
        data = [
            {"id": 1, "name": "Alex", "phone_number": 12345678, "comment": "abc"},
            "invalid string",
            123,
            None,
            {"id": 2, "name": "Bob", "phone_number": 987654321, "comment": "abc"}
        ]
        file_path.write_text(json.dumps(data), encoding='utf-8')
        reader = FileReader(file_path)

        contacts = reader.read()

        assert len(contacts) == 2
        assert contacts[0].name == "Alex"
        assert contacts[1].name == "Bob"

    @pytest.mark.parametrize("invalid_json", [
        "{ invalid json }",
        "not json at all",
        "{unterminated",
        "[1, 2, 3,]",
        '{"key": undefined}',
        ""
    ])
    def test_read_raises_corrupted_error_for_various_invalid_json(self, tmp_path, invalid_json):
        """Должен вызвать FileCorruptedError для различных типов невалидного JSON"""
        file_path = tmp_path / 'invalid.json'
        file_path.write_text(invalid_json, encoding='utf-8')
        reader = FileReader(file_path)

        with pytest.raises(FileCorruptedError):
            reader.read()