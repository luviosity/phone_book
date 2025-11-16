from typing import TypedDict, NotRequired
from dataclasses import dataclass, asdict
from custom_errors import EmptyValueInInputError, NotADigitValueError, InvalidPhoneNumberError


@dataclass
class Contact:
    id: int
    name: str
    phone_number: int
    comment: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        return cls(
            id=int(data['id']),
            name=str(data['name']),
            phone_number=int(data['phone_number']),
            comment=str(data.get('comment', '')),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def validate_name(value: str) -> None:
        if not value:
            raise EmptyValueInInputError('Имя не может быть пустым.')

    @staticmethod
    def parse_phone_number(value: str) -> int:
        if not value:
            raise EmptyValueInInputError('Номер телефона не может быть пустым.')

        if not value.isdigit():
            raise NotADigitValueError('Номер должен быть положительным числом.')

        if not (7 <= len(value) <= 15):
            raise InvalidPhoneNumberError('Номер должен содержать от 7 до 15 цифр.')

        return int(value)

    @staticmethod
    def parse_contact_id(value: str) -> int:
        if not value:
            raise EmptyValueInInputError('ID контакта не может быть пустым.')

        try:
            int_value = int(value)
        except ValueError:
            raise NotADigitValueError('ID контакта должен быть числом.')

        if int_value <= 0:
            raise NotADigitValueError('ID контакта должен быть положительным числом.')

        return int_value


class ContactUpdate(TypedDict):
    name: NotRequired[str]
    phone_number: NotRequired[int]
    comment: NotRequired[str]


class ContactAdd(TypedDict):
    name: str
    phone_number: int
    comment: str
