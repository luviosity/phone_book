import pytest
from custom_types import Contact
from unittest.mock import patch
from model import ContactBookModel


@pytest.fixture
def sample_contacts():
    """Фикстура с образцами контактов для тестов"""
    return [
        Contact(id=1, name='Alex', phone_number=12345678, comment='abc'),
        Contact(id=2, name='Bob', phone_number=987654321, comment='abc')
    ]

@pytest.fixture
def contact_book(tmp_path, sample_contacts):
    """Фикстура для ContactBookModel с тестовыми данными"""
    file_path = tmp_path / 'test_contacts.json'
    book = ContactBookModel(str(file_path))
    with patch.object(book.reader, 'read', return_value=sample_contacts):
        book.load_data()
    return book
