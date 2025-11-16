import json
from pathlib import Path
from custom_types import Contact
from custom_errors import FileCorruptedError, InvalidFileFormatError, ContactLoadError


class FileReader:
    """Класс для чтения данных контактов из JSON файла"""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> list[Contact]:
        """
        Читает и парсит данные контактов из JSON файла.

        Returns:
            list[Contact]: Список валидных контактов из файла

        Raises:
            FileNotFoundError: Если файл не существует
            FileCorruptedError: Если файл поврежден или пуст
            InvalidFileFormatError: Если формат файла некорректен
            ContactLoadError: Если не удалось загрузить контакты
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f'Файл {self.file_path} не найден')

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                raw = json.load(file)
        except json.JSONDecodeError as e:
            raise FileCorruptedError(f'Файл поврежден или пуст: {e}')

        if not isinstance(raw, list):
            raise InvalidFileFormatError('Некорректный формат файла данных (ожидался список).')

        contacts: list[Contact] = []
        errors: list[str] = []

        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                contacts.append(Contact.from_dict(item))
            except Exception as e:
                errors.append(f'Контакт {item}: {e}')

        if errors:
            raise ContactLoadError('\n'.join(errors))

        return contacts
