class NotADigitValueError(ValueError):
    pass


class UnsupportedCommandError(ValueError):
    pass


class EmptyValueInInputError(ValueError):
    pass


class InvalidPhoneNumberError(ValueError):
    pass


class WrongContactIdError(ValueError):
    pass


class FileCorruptedError(Exception):
    """Файл поврежден или имеет неверный формат"""
    pass


class InvalidFileFormatError(Exception):
    """Некорректный формат данных в файле"""
    pass


class ContactLoadError(Exception):
    """Ошибка при загрузке контакта"""
    pass


class SaveFileError(Exception):
    """Ошибка при сохранении файла"""
    pass


class CreateEmptyBookError(Exception):
    """Ошибка при создании пустого справочника"""
    pass


__all__ = [
    'NotADigitValueError',
    'UnsupportedCommandError',
    'EmptyValueInInputError',
    'InvalidPhoneNumberError',
    'WrongContactIdError',
    'FileCorruptedError',
    'InvalidFileFormatError',
    'ContactLoadError',
    'SaveFileError',
    'CreateEmptyBookError'
]
