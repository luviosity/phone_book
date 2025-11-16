import json
from pathlib import Path
from custom_types import Contact
from custom_errors import SaveFileError, CreateEmptyBookError


class FileWriter:
    """Класс для записи данных контактов в JSON файл"""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def _ensure_file_exists(self) -> None:
        """
        Создает пустой файл и необходимые директории, если они не существуют.

        Raises:
            CreateEmptyBookError: Если не удалось создать файл или директории
        """
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                self.file_path.touch()
        except OSError as e:
            raise CreateEmptyBookError(f'Ошибка в создании пустого справочника по пути {self.file_path}: {e}')

    def write(self, contacts: list[Contact]) -> None:
        """
        Записывает список контактов в JSON файл.

        Args:
            contacts: Список контактов для сохранения

        Raises:
            SaveFileError: Если не удалось сохранить файл
        """
        self._ensure_file_exists()
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([c.to_dict() for c in contacts], file, ensure_ascii=False)
        except Exception as e:
            raise SaveFileError(f'Невозможно сохранить файл: {e}')
