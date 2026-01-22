from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from .base import INVALID_NAMES


def apply_regex(value, regex, message=None):
    RegexValidator(
        regex=regex,
        message=message or f"{value} is invalid",   
    )(value)


@deconstructible
class UsernameValidator:
    def __init__(self, invalid_names=None):
        self.invalid_names = invalid_names or INVALID_NAMES
    
    def __call__(self, value):
        apply_regex(
            value,
            r'^[a-z0-9_.]+$',
            'Username must contain only lowercase letters, numbers and _/.'
        )

        for name in self.invalid_names:
            if name in value:
                raise ValidationError(f"'{value}' is not allowed as a username")
        if value.isdigit():
            raise ValidationError('Username cannot be only numbers.')
        if all(char in '._' for char in value):
            raise ValidationError('Username cannot consist only of dots and underlines.')


@deconstructible
class NameValidator:
    def __init__(self, field_name='Name'):
        self.field_name = field_name
    
    def __call__(self, value):
        apply_regex(
            value,
            r'^[a-zA-Z]+$',
            f"{self.field_name} must contain only letters."
        )


@deconstructible
class URLValidator:
    def __call__(self, value):
        if not value.startswith('https://'):
            raise ValidationError('URL must starts with https://')