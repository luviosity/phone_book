import pytest
import json
from pathlib import Path
from unittest.mock import patch

from tools import FileWriter
from custom_types import Contact
from custom_errors import SaveFileError


def read_json_file(file_path: Path) -> list:
    """Вспомогательная функция для чтения JSON файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestFileWriter:
    """Тесты для класса FileWriter"""

    def test_write_creates_file_when_not_exists(self, tmp_path, sample_contacts):
        """Должен создать файл если он не существует"""
        file_path = tmp_path / 'contacts.json'
        writer = FileWriter(file_path)
        assert not file_path.exists()

        writer.write(sample_contacts)

        assert file_path.exists()
        assert file_path.is_file()

    def test_write_creates_valid_json(self, tmp_path, sample_contacts):
        """Должен создать валидный JSON файл"""
        file_path = tmp_path / 'contacts.json'
        writer = FileWriter(file_path)

        writer.write(sample_contacts)

        data = read_json_file(file_path)
        assert isinstance(data, list)
        assert len(data) == len(sample_contacts)

        assert data[0]['id'] == sample_contacts[0].id
        assert data[0]['name'] == sample_contacts[0].name
        assert data[0]['phone_number'] == sample_contacts[0].phone_number
        assert data[0]['comment'] == sample_contacts[0].comment

        assert data[1]['id'] == sample_contacts[1].id
        assert data[1]['name'] == sample_contacts[1].name
        assert data[1]['phone_number'] == sample_contacts[1].phone_number
        assert data[1]['comment'] == sample_contacts[1].comment

    def test_write_overwrites_existing_file(self, tmp_path, sample_contacts):
        """Должен перезаписать существующий файл"""
        file_path = tmp_path / 'contacts.json'
        writer = FileWriter(file_path)

        writer.write(sample_contacts)
        initial_data = read_json_file(file_path)
        assert len(initial_data) == 2

        new_contacts = [
            Contact(id=3, name='Charlie', phone_number=555555555, comment='new')
        ]

        writer.write(new_contacts)

        new_data = read_json_file(file_path)
        assert len(new_data) == 1
        assert new_data[0]['id'] == 3
        assert new_data[0]['name'] == 'Charlie'
        assert new_data[0]['comment'] == 'new'

    def test_write_handles_empty_list(self, tmp_path):
        """Должен успешно записать пустой список контактов"""
        file_path = tmp_path / 'empty.json'
        writer = FileWriter(file_path)
        empty_contacts = []

        writer.write(empty_contacts)

        data = read_json_file(file_path)
        assert data == []

    def test_write_raises_save_error_when_json_dump_fails(self, tmp_path):
        """Должен вызвать SaveFileError при ошибке сериализации JSON"""
        file_path = tmp_path / 'test.json'
        writer = FileWriter(file_path)
        contacts = [Contact(id=1, name='Test', phone_number=123, comment='test')]

        with patch('json.dump', side_effect=Exception("JSON error")):
            with pytest.raises(SaveFileError):
                writer.write(contacts)

    def test_write_raises_save_error_when_file_write_fails(self, tmp_path):
        """Должен вызвать SaveFileError при ошибке записи файла"""
        file_path = tmp_path / 'test.json'
        writer = FileWriter(file_path)
        contacts = [Contact(id=1, name='Test', phone_number=123, comment='test')]

        with patch('builtins.open', side_effect=IOError("Write failed")):
            with pytest.raises(SaveFileError):
                writer.write(contacts)

    def test_write_preserves_data_types(self, tmp_path):
        """Должен сохранять корректные типы данных в JSON"""
        file_path = tmp_path / 'types.json'
        writer = FileWriter(file_path)
        contacts = [Contact(id=1, name='Test', phone_number=999999999, comment='')]

        writer.write(contacts)

        data = read_json_file(file_path)
        assert isinstance(data[0]['id'], int)
        assert isinstance(data[0]['name'], str)
        assert isinstance(data[0]['phone_number'], int)
        assert isinstance(data[0]['comment'], str)