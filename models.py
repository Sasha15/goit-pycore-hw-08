from collections import UserDict
from datetime import datetime, timedelta
import re
from colorama import Fore, Style

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        self._validate_phone(value)
        super().__init__(value)

    def _validate_phone(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must be exactly 10 digits.")


class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_obj)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: str, new_phone: str):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return True
        raise ValueError("Phone number not found.")

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phones_str = '; '.join(Fore.GREEN + p.value + Style.RESET_ALL for p in self.phones)
        birthday_str = f", birthday: {Fore.MAGENTA}{self.birthday}{Style.RESET_ALL}" if self.birthday else ""
        return f"{Fore.CYAN}Contact name: {self.name.value}{Style.RESET_ALL}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    # adapted version of get_upcoming_birthdays from homework 3
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if not record.birthday:
                continue

            name = record.name.value
            birthday = record.birthday.value.date()

            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            delta_days = (birthday_this_year - today).days
            if 0 <= delta_days <= 7:
                congratulation_date = birthday_this_year
                if birthday_this_year.weekday() in [5, 6]:
                    # переносимо на понеділок
                    days_to_monday = 7 - birthday_this_year.weekday()
                    congratulation_date = birthday_this_year + timedelta(days=days_to_monday)

                upcoming_birthdays.append({
                    "name": name,
                    "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                })

            # особливий випадок: понеділок і ДН у вихідні перед ним
            if today.weekday() == 0 and birthday_this_year.weekday() in [5, 6]:
                upcoming_birthdays.append({
                    "name": name,
                    "congratulation_date": today.strftime("%Y.%m.%d")
                })

        return upcoming_birthdays
