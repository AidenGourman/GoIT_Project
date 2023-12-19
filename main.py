from _collections_abc import Iterator
from datetime import datetime
from collections import UserDict
from faker import Faker
import random
import pickle
import os
import re
import time

from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.progress import track


custom_theme = Theme(
    {"success": "bold green", "error": "bold red", "warning": "bold yellow"})
console = Console(theme=custom_theme)


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


class Address(Field):
    @Field.value.setter
    def value(self, value):
        self._Field__value = value


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


class Record:
    def __init__(self, name, phone, birthday, email, notes=None, address=None) -> None:
        self.name = Name(name)
        self.birthday = Birthday(birthday)
        self.phone = Phone(phone) if phone else None
        self.phones = [self.phone] if phone else []
        self.email = Email(email)
        self.address = Address(address)
        self.notes = [Note(notes)] if notes else []

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

    def show_notes(self):
        return f'Notes: {"; ".join(str(note) for note in self.notes) if self.notes else "No notes"}'

    def find_note(self, keyword):
        matching_notes = [
            str(note) for note in self.notes if keyword.lower() in str(note).lower()]
        return matching_notes

    def add_note(self, note_value, tags=None):
        new_note = Note(note_value, tags)
        self.notes.append(new_note)
        return f'notes: {"; ".join(str(note) for note in self.notes) if self.notes else "N/A"}'

    def edit_note(self, keyword, new_note_value, new_tags=None):
        for note in self.notes:
            if keyword.lower() in str(note).lower():
                note.edit_value(new_note_value)
                if new_tags is not None:
                    note.tags = new_tags
                return f"Note edited: {keyword} -> {note}, tags: {note.tags}"
        else:
            raise ValueError("Note not found.")

    def delete_note(self, keyword):
        for note in self.notes:
            if keyword.lower() in str(note).lower():
                self.notes.remove(note)
                return f"Note deleted, notes: {self.show_notes()}"
        else:
            raise ValueError("Note not found.")

    def days_to_birthday(self):
        if self.birthday:
            date_now = datetime.now().date()
            user_next_birthday = datetime(
                date_now.year, self.birthday.value.month, self.birthday.value.day).date()
            user_next_year = user_next_birthday.replace(year=date_now.year + 1)
            delta = user_next_birthday - \
                date_now if user_next_birthday >= date_now else user_next_year - date_now
            return delta.days

    def __str__(self) -> str:
        return (
            f"Contact_name: {self.name.value if self.name else 'N/A'} || "
            f"Phone: {'; '.join(i.value for i in self.phones) if self.phones else 'N/A'} || "
            f"Birthday: {self.birthday.value if self.birthday else 'N/A'} || "
            f"Email: {self.email.value if self.email else 'N/A'} || "
            f"Address: {self.address.value if self.address and self.address.value else 'N/A'} || "
            f"Notes: {'; '.join(str(note) for note in self.notes) if self.notes else 'N/A'} || "
            f"To_birthday: {self.days_to_birthday()}")


class AddressBook(UserDict):
    def add_record(self, record: Record):  # add record in dictionary
        key = record.name.value
        self.data[key] = record

    def find(self, name):   # get record in dictionary
        return self.data.get(name)

    def delete(self, name):  # delete contact in dictionary
        if name in self.data:
            del self.data[name]
            return f'Record {name} deleted'
        else:
            raise KeyError(f"Contact '{name}' not found.")

    def save_to_file(self, filename):     # serialization data to file
        with open(filename, 'wb') as file_write:
            pickle.dump(self.data, file_write)
            return f'exit'

    def restore_from_file(self, filename):  # deserialization data from file
        with open(filename, 'rb') as file_read:
            self.data = pickle.load(file_read)

    def search(self, row):  # searching records via partial name or phone
        row = row.lower()
        result = []
        for record in self.data.values():
            if row in record.name.value.lower() or any(row in phone.value for phone in record.phones):
                result.append(record)
        return result

    def add_note_to_contact(self, contact_name, note_value, tags=None):
        contact = self.find(contact_name)
        if contact:
            return contact.add_note(note_value, tags)
        else:
            raise ValueError("Contact not found.")

    # generate records for address_book
    def generate_random_contacts(self, n=10):
        fake = Faker()
        for i in range(n+1):
            name = fake.name()
            # random phone numbers according pattern (r"^0[3456789]\d{8}$")
            phone = f'{0}{random.choice("3456789")}{random.randint(10**7,10**8-1)}'
            birthday = fake.date_of_birth(
                minimum_age=18, maximum_age=60).strftime('%Y-%m-%d')
            email = fake.email()
            notes = fake.text()
            address = fake.address()
            record = Record(name, phone, birthday, email, notes, address)
            self.add_record(record)
        self.save_to_file(filename)
        print('AddressBook records are generated and saved')

    def validate_input(self, prompt, validation_func):
        while True:
            user_input = input(prompt)
            try:
                validation_func(user_input)
                return user_input
            except ValueError as e:
                print(f"Error: {e}")

    def get_contact(self):
        name = self.validate_input("\nEnter name: ", lambda x: Name(x))
        address = self.validate_input(
            "\nEnter Address: ", lambda x: Address(x))
        phone = self.validate_input("Enter phone: ", lambda x: Phone(x))
        email = self.validate_input("Enter email: ", lambda x: Email(x))
        birthday = self.validate_input(
            "Enter birthday (YYYY-MM-DD): ", lambda x: Birthday(x))
        note = self.validate_input("\nEnter note: ", lambda x: Note(x))
        return Record(name, phone, birthday, email, note, address)

# //////////////////// NOTe LOGIC ///////////////////

# //////////////////// NOTe LOGIC ///////////////////

    def __iter__(self) -> Iterator:
        # Iterable class
        return AddressBookIterator(self.data.values(), page_size=2)

    def __repr__(self):
        return f"AddressBook({self.data})"


class AddressBookIterator:
    def __init__(self, records_list, page_size):
        self.records = list(records_list)
        self.page_size = page_size
        self.counter = 0  # quantity on page
        # use for showing part of the reccords that size < page_size
        self.page = len(self.records) // self.page_size

    def __next__(self):
        if self.counter >= len(self.records):
            raise StopIteration
        else:
            if self.page > 0:
                # slice reccords on the page
                result = list(
                    self.records[self.counter:self.counter + self.page_size])
                self.page -= 1
                self.counter += self.page_size
            else:
                # the rest of the records on the page
                result = list(self.records[self.counter:])
                self.counter = len(self.records)
        return result


if __name__ == '__main__':
    filename = 'contacts.pkl'
    address_book = AddressBook()  # create object
    try:
        if os.path.getsize(filename) > 0:  # check if file of data not empty
            address_book.restore_from_file(filename)
    except Exception:
        f'First run, will be create file'
#       address_book.generate_random_contacts()
    for i in track(range(5), description="Loading data..."):
        print(f"loading {i}")
        time.sleep(0.5)
    while True:
        print("\nMenu:")
        print("-" * 45)
        print("1. Add contact  | 2. Display all contacts")
        print("3. Edit contact | 4. Delete contact")
        print("5. Find contact | 6. Find the nearest birthday")
        print("-" * 45)
        print("7. Note menu")
        print("-" * 12)
        print("8. Save & Exit")

        choice = input("\nChoose an option: ")

        if choice == '1':
            address_book.add_record(address_book.get_contact())
            console.print('Contact added successfully', style="success")

        elif choice == '2':
            for page in address_book:
                for record in page:
                    print(record)
                    print(record.days_to_birthday())
            print('*' * 20)
# /////////////////////////////////EDIT MENU ///////////////////////////////////////
        elif choice == '3':
            while True:
                print("\nEdit menu:")
                print("-" * 45)
                print("1. Edit whole contact")
                print("2. Edit contact phone number")
                print("3. Edit contact mail")
                print("4. Return to contact menu")
                print("-" * 45)

                choice = input("\nChoose an option: ")

                if choice == '1':  # Edit whole contact
                    pass

                elif choice == '2':  # Edit contact phone number
                    pass

                elif choice == '3':  # Edit contact mail
                    pass

                elif choice == '4':  # Exit from edit menu and back to contact menu
                    break
                else:
                    console.print(
                        "Invalid choice. Please try again.", style="error")

# /////////////////////////////////EDIT MENU ///////////////////////////////////////
        elif choice == '4':  # Delete contact
            contact_name = input("Enter contact name to delete: ")
            try:
                address_book.delete(contact_name)
                console.print(
                    f"Contact '{contact_name}' deleted successfully", style="success")
            except KeyError:
                console.print(
                    f"Contact '{contact_name}' not found", style="error")

        elif choice == '5':  # Find contact
            search_query = input(
                "Enter a name or phone number to search: ").lower()

            # Search for contacts
            search_result = address_book.search(search_query)

            if search_result:
                console.print("Search result:")
                for result in search_result:
                    console.print(result)
            else:
                console.print("No matching contacts found", style="warning")

        elif choice == '6':  # display_contacts_n_day_to birthday
            n = int(input("Input quantity days to birthday: "))
            for page in address_book:
                for record in page:
                    if record.days_to_birthday() <= n:
                        print(record)
                print('*' * 20)

# ///////////////////////  LOGIC FOR NOTES MENU /////////////////////////
        elif choice == '7':
            while True:
                print("\nNote menu:")
                print("-" * 45)
                print("1. Add note  | 2. Show all notes")
                print("3. Edit note | 4. Delete note")
                print("5. Find note | 6. Return to contact menu")

                choice = input("\nChoose an option: ")

                if choice == '1':  # Add note
                    contact_name = input("Enter contact name: ")
                    note_value = input("Enter note: ")
                    tags = input("Enter tags (comma-separated): ").split(',')
                    try:
                        result = address_book.add_note_to_contact(
                            contact_name, note_value, tags)
                        console.print(result, style="success")
                    except ValueError as e:
                        console.print(f"Error: {e}", style="error")

                elif choice == '2':  # Show all notes
                    contact_name = input("Enter contact name: ")
                    contact = address_book.find(contact_name)
                    if contact:
                        notes_result = contact.show_notes()
                        console.print(
                            notes_result if notes_result != "No notes" else "warning")
                    else:
                        print("Contact not found", style="error")

                elif choice == '3':  # Edit notes
                    pass

                elif choice == '4':  # Delete note
                    contact_name = input("Enter contact name: ")
                    contact = address_book.find(contact_name)
                    if contact:
                        keyword = input("Enter keyword to delete note: ")
                        try:
                            result = contact.delete_note(keyword)
                            console.print(result, style="success")
                        except ValueError as e:
                            console.print(f"Error: {e}", style="error")
                    else:
                        console.print("Contact not found", style="error")

                elif choice == '5':  # Find notes
                    contact_name = input("Enter contact name: ")
                    contact = address_book.find(contact_name)
                    if contact:
                        keyword = input(
                            "Enter a keyword to search in notes: ")
                        matching_notes = contact.find_note(keyword)
                        if matching_notes:
                            console.print("Notes found:")
                            for note in matching_notes:
                                console.print(note)
                        else:
                            console.print("Notes not found", style="warning")
                    else:
                        console.print("Contact not found", style="error")

                elif choice == '6':  # Exit from note menu and back to contact menu
                    break
                else:
                    console.print(
                        "Invalid choice. Please try again.", style="error")


# ^^^^^///////////////////////  LOGIC FOR NOTES MENU /////////////////////////^^^^^^
        elif choice == '8':
            address_book.save_to_file(filename)
            console.print(
                f'Contactbook saved, have a nice day! :D', style="success")
            break
        else:
            console.print("Invalid choice. Please try again.", style="error")
