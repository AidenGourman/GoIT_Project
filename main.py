import re
from datetime import datetime
from collections import UserDict

class Field:                                        #parrent 
    def __init__(self, value=None):
        self.__value = None
        self.value = value
    
    @property                                       #getter
    def value(self):
        return self.__value
    
    @value.setter                                   #setter
    def value(self, value):
        self.__value = value
    
    def __repr__(self):                             #get readable form
        return f"{self.__class__.__name__}({self.value})"

class Name(Field):
    @Field.value.setter
    def value(self, value:str):
        if not(re.findall(r'[^a-zA-Z\s]', value)): # check if name is valid: [value.isalpha\s]
            self._Field__value = value
        else:
            raise ValueError('Name should include only letter character')

class Birthday(Field):
    @Field.value.setter
    def value(self, value=None):
        if value:
            try:                                       
                self._Field__value = datetime.strptime(value, '%Y-%m-%d').date() 
            except Exception:
                raise ValueError("Date should be in the format YYYY-MM-DD") # add info about format of the date

class Phone(Field): 
    @Field.value.setter
    def value(self, value):
        phone_pattern_ua = re.compile(r"^0[3456789]\d{8}$") # format UA mobile_operators,10 numbers and only digits,first 0
        if phone_pattern_ua.match(value):
            self._Field__value = value
        else:
            raise ValueError('Phone is not valid')

class Email(Field):   
    @Field.value.setter
    def value(self, value):
        email_pattern = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$") # check if correct input for email
        #(one char@letters_digit_dot_hyphen_from_1_char.domain_only_letters_from_2_chars)
        if email_pattern.match(value):
            self._Field__value = value
        else:
            raise ValueError("Email is not valid")

class Note:
    pass
class Address:
    pass

class Record: 
    def __init__(self, name, phone, birthday, email, address=None, note=None) -> None:
        self.name = Name(name)
        self.birthday = Birthday(birthday)
        self.phone = Phone(phone) if phone else None
        self.phones = [self.phone] if phone else [] 
        self.email = Email(email)
        self.address = Address(address)
        self.note = Note(note)         
        self.notes = [self.note] if note else []  

    def add_phone(self, phone_number:str): # adding phone
        phone = Phone(phone_number)  
        if phone not in self.phones: 
            self.phones.append(phone) 

    def remove_phone(self, phone_number:str):  #delete phone
        phone = Phone(phone_number)
        for i in self.phones:
         if phone.value == i.value:
            self.phones.remove(i)
            return "phone is removed"  

    def edit_phone(self, old_phone, new_phone):  # edditing  reccords 
        if not self.find_phone(old_phone): 
            raise ValueError
        for i, phone in enumerate(self.phones): # get position for replasement with phone
            if phone.value == old_phone:
                new_phone_obj = Phone(new_phone) 
                self.phones[i] = new_phone_obj   

    def find_phone(self, phone_number:str): # find phone if it exist 
        phone = Phone(phone_number)
        for i in self.phones:
            if i.value == phone.value: 
                return i.value
        return None
    
    def edit_email(self, new_email):
        new_email = Email(new_email)
        self.email = new_email
        return f"email:{self.email.value}"
    
    def add_note(self, note:str):
        if  self.name.value:
            new_note_obj = Note(note)
            self.notes.append(new_note_obj)
            return f'note added'
        else:
            raise ValueError(f"The record not exist")

    def show_note(self, name):
        if name == self.name.value:
            return f'notes of {name} : {"; ".join(note.value for note in self.notes) if self.notes else "N/A"}'
        else:
            raise ValueError(f"Name not found: {name}")

    def edit_note(self, name, new_note:str):
        if name == self.name.value:
            pass
    
    def __str__(self) -> str: # readable view
        return f"contact name:{self.name.value}, phones:{'; '.join(i.value for i in self.phones)}, birthday:{self.birthday.value}, email:{self.email.value}, address:{self.address.value if self.address.value is not None else 'N/A'}, note:{'; '.join(i.value for i in self.notes) if self.note.value is not None else 'N/A'}"
    