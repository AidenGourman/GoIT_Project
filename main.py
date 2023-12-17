import json
import os


class PersonalAssistant:
    def __init__(self, storage_path='contacts.json'):
        self.storage_path = storage_path
        self.contacts = self.load_contacts()

    def load_contacts(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as file:
                contacts = json.load(file)
            return contacts
        else:
            return {}

    def save_contacts(self):
        with open(self.storage_path, 'w') as file:
            json.dump(self.contacts, file, indent=2)

    def add_contact(self, name, address, phone, email, birthday, note):
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
        print(f"Контакт {name} додано успішно.")

    def display_contacts(self):
        if not self.contacts:
            print("Книга контактів порожня.")
        else:
            print("\nКонтакти:")
            for name, details in self.contacts.items():
                print(f"\nІм'я: {details['Name']}")
                print(f"Адреса: {details['Address']}")
                print(f"Телефон: {details['Phone']}")
                print(f"Email: {details['Email']}")
                print(f"День народження: {details['Birthday']}")
                print(f"Нотатка: {details['Note']}")
                print("-" * 30)


if __name__ == "__main__":
    assistant = PersonalAssistant()

    while True:
        print("\nМеню:")
        print("1. Додати контакт")
        print("2. Показати всі контакти")
        print("3. Вийти")

        choice = input("\nВиберіть опцію: ")

        if choice == '1':
            name = input("\nВведіть ім'я: ")
            address = input("Введіть адресу: ")
            phone = input("Введіть номер телефону: ")
            email = input("Введіть email: ")
            birthday = input("Введіть день народження: ")
            note = input("Введіть нотатку: ")
            assistant.add_contact(name, address, phone, email, birthday, note)

        elif choice == '2':
            assistant.display_contacts()

        elif choice == '3':
            break

        else:
            print("Невірний вибір. Спробуйте ще раз.")
