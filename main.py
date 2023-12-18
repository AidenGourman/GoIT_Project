from datetime import datetime
import pickle
import os
import re


class Field:
    def __init__(self, value=None):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class Name(Field):
    @Field.value.setter
    def value(self, value: str):
        if not re.findall(r'[^a-zA-Z\s]', value):
            self._Field__value = value
        else:
            raise ValueError('Name should include only letter characters')


class Birthday(Field):
    @Field.value.setter
    def value(self, value=None):
        if value:
            try:
                self._Field__value = datetime.strptime(
                    value, '%Y-%m-%d').date()
            except Exception:
                raise ValueError("Date should be in the format YYYY-MM-DD")


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        phone_pattern_ua = re.compile(r"^0[3456789]\d{8}$")
        if phone_pattern_ua.match(value):
            self._Field__value = value
        else:
            raise ValueError('Phone is not valid')


class Email(Field):
    @Field.value.setter
    def value(self, value):
        email_pattern = re.compile(
            "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if email_pattern.match(value):
            self._Field__value = value
        else:
            raise ValueError("Email is not valid")


class Note(Field):
    def __init__(self, value, tags=None):
        super().__init__(value)
        self.tags = tags or []

    def add_tag(self, tag):
        self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
        else:
            raise ValueError(f"Tag {tag} not found.")

    def has_tag(self, tag):
        return tag in self.tags

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value}, {self.tags})"


class AddressBook:
    def __init__(self, file_path="address_book.pkl"):
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            self.data = {}

    def save_data(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def add_record(self, record):
        self.data[record.name.value] = record.__dict__
        self.save_data()

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self.save_data()

    def find(self, query):
        found_records = []
        for name, record_data in self.data.items():
            if query.lower() in name.lower():
                found_records.append(self.create_record(record_data))
        return found_records

    def create_record(self, data):
        record = Record('', '', '', '', '')
        record.__dict__.update(data)
        return record


class Record:
    def __init__(self, name, phone, birthday, email, note) -> None:
        self.name = Name(name)
        self.birthday = Birthday(birthday)
        self.phone = Phone(phone) if phone else None
        self.phones = [self.phone] if phone else []
        self.email = Email(email)
        self.note = Note(note)

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        if phone not in self.phones:
            self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = Phone(phone_number)
        for i in self.phones:
            if phone.value == i.value:
                self.phones.remove(i)
                return "phone is removed"

    def edit_phone(self, old_phone, new_phone):
        if not self.find_phone(old_phone):
            raise ValueError
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                new_phone_obj = Phone(new_phone)
                self.phones[i] = new_phone_obj

    def find_phone(self, phone_number):
        phone = Phone(phone_number)
        for i in self.phones:
            if i.value == phone.value:
                return i.value
        return None

    def edit_email(self, new_email):
        new_email = Email(new_email)
        self.email = new_email
        return f"email:{self.email.value}"

    def add_note(self, note):
        if self.name.value:
            new_note_obj = Note(note)
            self.note = new_note_obj
            return f'note added'
        else:
            raise ValueError(f"The record does not exist")

    def show_note(self):
        return f'notes: {self.note.value}'

    def edit_note(self, new_note):
        self.note.value = new_note

    def __str__(self):
        return f"contact name:{self.name.value}, phones:{'; '.join(i.value for i in self.phones)}, " \
               f"birthday:{self.birthday.value}, email:{self.email.value}, " \
               f"note:{self.note.value if self.note.value is not None else 'N/A'}"


class PersonalAssistant:
    def __init__(self, storage_path='contacts.pkl'):
        self.storage_path = storage_path
        self.contacts = self.load_contacts()

    def load_contacts(self):
        try:
            with open(self.storage_path, 'rb') as file:
                contacts = pickle.load(file)
            return contacts
        except FileNotFoundError:
            return {}

    def save_contacts(self):
        with open(self.storage_path, 'wb') as file:
            pickle.dump(self.contacts, file)

    def validate_input(self, prompt, validation_func):
        while True:
            user_input = input(prompt)
            try:
                validation_func(user_input)
                return user_input
            except ValueError as e:
                print(f"Error: {e}")

    def add_contact(self):
        name = self.validate_input("\nEnter name: ", lambda x: Name(x))
        address = input("Enter address: ")
        phone = self.validate_input("Enter phone: ", lambda x: Phone(x))
        email = self.validate_input("Enter email: ", lambda x: Email(x))
        birthday = self.validate_input(
            "Enter birthday (YYYY-MM-DD): ", lambda x: Birthday(x))
        note = input("Enter note: ")

        contact = {
            'Name': name,
            'Address': address,
            'Phone': phone,
            'Email': email,
            'Birthday': birthday,
            'Note': note
        }
        self.contacts[name] = contact
        self.save_contacts()
        print(f"Contact {name} added successfully.")

    def display_contacts(self):
        if not self.contacts:
            print("Address book is empty.")
        else:
            print("\nContacts:")
            for name, details in self.contacts.items():
                print(f"\nName: {details['Name']}")
                print(f"Address: {details['Address']}")
                print(f"Phone: {details['Phone']}")
                print(f"Email: {details['Email']}")
                print(f"Birthday: {details['Birthday']}")
                print(f"Note: {details['Note']}")
                print("-" * 30)

    def run_menu(self):
        while True:
            print("\nMenu:")
            print("1. Add contact")
            print("2. Display all contacts")
            print("3. Exit")

            choice = input("\nChoose an option: ")

            if choice == '1':
                self.add_contact()

            elif choice == '2':
                self.display_contacts()

            elif choice == '3':
                break

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    assistant = PersonalAssistant()
    assistant.run_menu()
