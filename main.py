from datetime import datetime, timedelta
from collections import UserDict
import pickle

# Клас Field для представлення загальних полів
class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

# Клас Name для представлення імен
class Name(Field):
    pass

# Клас Phone для представлення номерів телефонів
class Phone(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    def is_valid(self, number):
        return len(number) == 10 and number.isdigit()

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError("Invalid phone number")
        self._value = new_value

# Клас Birthday для представлення днів народження
class Birthday(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Invalid birthday")
        super().__init__(value)

    def is_valid(self, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            raise ValueError("Invalid birthday")
        self._value = new_value

# Клас Note для представлення текстових нотаток
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

# Розширення класу Record (для додавання нотаток)
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
        self.notes = []

    # методи для роботи з нотатками
    def add_note(self, note_value, tags=None):
        note = Note(note_value, tags)
        self.notes.append(note)

    def edit_note(self, old_note, new_note):
        for note in self.notes:
            if isinstance(note, Note) and note.value == old_note:
                note.value = new_note
                return
        raise ValueError(f"Note {old_note} not found.")

    def remove_note(self, note):
        for n in self.notes:
            if isinstance(n, Note) and n.value == note:
                self.notes.remove(n)
                return
        raise ValueError(f"Note {note} not found.")

    def add_tag_to_note(self, note_value, tag):
        note = next((note for note in self.notes if note.value == note_value), None)
        if note:
            note.add_tag(tag)
        else:
            raise ValueError(f"Note {note_value} not found.")

    def remove_tag_from_note(self, note_value, tag):
        note = next((note for note in self.notes if note.value == note_value), None)
        if note:
            note.remove_tag(tag)
        else:
            raise ValueError(f"Note {note_value} not found.")

    def search_notes_by_tag(self, tag):
        return [note for note in self.notes if note.has_tag(tag)]

# Клас AddressBook для представлення книги адрес
class AddressBook(UserDict):
    def __init__(self, file_path="address_book.pkl"):
        super().__init__()
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass

    def save_data(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_data()

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            self.save_data()

    def find(self, query):
        found_records = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                found_records.append(record)
            for phone in record.phones:
                if query in phone.value:
                    found_records.append(record)
        return found_records

    def iterator(self, chunk_size=5):
        records = list(self.data.values())
        for i in range(0, len(records), chunk_size):
            yield records[i:i + chunk_size]

# Клас Assistant для управління контактами та взаємодією з користувачем
class Assistant:
    def __init__(self):
        self.contacts = AddressBook()

    # метод для додавання нотаток (до контакту)
    def add_note_to_contact(self, name, note):
        record = self.contacts.find(name)
        if record:
            record.add_note(note)
            self.contacts.save_data()
            return f"Note added to {name}: {note}."
        else:
            raise KeyError

    # метод для редагування нотаток        
    def edit_note(self, name, old_note, new_note):
        record = self.contacts.find(name)
        if record:
            try:
                record.edit_note(old_note, new_note)
                self.contacts.save_data()
                return f"Note edited for {name}: '{old_note}' changed to '{new_note}'."
            except ValueError as e:
                return str(e)  # обробка помилки, якщо нотатка не знайдена
        else:
            raise KeyError

    # метод для перегляду нотаток
    def view_notes(self, name):
        record = self.contacts.find(name)
        if record:
            if record.notes:
                notes_str = ", ".join(note.value for note in record.notes)
                return f"Notes for {name}: {notes_str}."
            else:
                return f"No notes found for {name}."
        else:
            raise KeyError
        
    def add_tag_to_note(self, name, note_value, tag):
        record = self.contacts.find(name)
        if record:
            record.add_tag_to_note(note_value, tag)
            self.contacts.save_data()
            return f"Tag '{tag}' added to note {note_value} for {name}."
        else:
            raise KeyError

    def remove_tag_from_note(self, name, note_value, tag):
        record = self.contacts.find(name)
        if record:
            record.remove_tag_from_note(note_value, tag)
            self.contacts.save_data()
            return f"Tag '{tag}' removed from note {note_value} for {name}."
        else:
            raise KeyError

    def search_notes_by_tag(self, tag):
        found_records = []
        for record in self.contacts.data.values():
            for note in record.notes:
                if note.has_tag(tag):
                    found_records.append((record, note))
        if found_records:
            result = "Found notes with tag '{}':\n".format(tag)
            for record, note in found_records:
                result += f"{record.name.value} - {note.value}\n"
            return result.strip()
        else:
            return "No notes found with tag '{}'.".format(tag)

if __name__ == "__main__":
    assistant = Assistant()
    assistant.main()