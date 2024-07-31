import re


def validate_age(age):
    pattern = re.compile(r'^(18|19|[2-9][0-9])$')
    if pattern.match(age):
        return True
    else:
        return False


def validate_city(city):
    return True if city.isalpha() else False


def validate_name(name):
    pattern = r"^[а-яА-ЯёЁ\s]+$"
    if re.match(pattern, name):
        return True
    return False

