class PhoneBookBaseException(Exception):
    pass


class PhoneBookValueError(PhoneBookBaseException):
    pass


class NotADigitValueError(PhoneBookValueError):
    pass


class UnsupportedCommandError(PhoneBookValueError):
    pass


class EmptyValueInInputError(PhoneBookValueError):
    pass


class InvalidPhoneNumberError(PhoneBookValueError):
    pass


class WrongContactIdError(PhoneBookValueError):
    pass


class FileCorruptedError(PhoneBookBaseException):
    """Файл поврежден или имеет неверный формат"""
    pass


class InvalidFileFormatError(PhoneBookBaseException):
    """Некорректный формат данных в файле"""
    pass


class ContactLoadError(PhoneBookBaseException):
    """Ошибка при загрузке контакта"""
    pass


class SaveFileError(PhoneBookBaseException):
    """Ошибка при сохранении файла"""
    pass


class CreateEmptyBookError(PhoneBookBaseException):
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
