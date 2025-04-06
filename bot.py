import sys
import pickle
import functools
from pathlib import Path
from colorama import Fore, Style

from models import AddressBook, Record

BASE_DIR = Path(__file__).parent
# Define the path to the contacts file. 
# dat is used for binary files as we are saving UserDict
CONTACTS_FILE = BASE_DIR / "contacts.dat"
book = AddressBook()

# Decorator to handle input errors
def input_error(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "❌ Contact not found. Please enter a valid name."
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                return "⚠️ Not enough arguments. Please check the command format."
            return f"⚠️ Error: {str(e)}"
        except IndexError:
            return "⚠️ Missing arguments. Please check the command format."
        except TypeError:
            return "⚠️ Invalid number of arguments. Please check the command format."
    return inner

# Display message in color
# Types: success (green), error (red), info (blue), warning (yellow)
def print_colored(text: str, msg_type: str = "info"):
    colors = {
        "success": Fore.GREEN + Style.BRIGHT,
        "error": Fore.RED + Style.BRIGHT,
        "info": Fore.BLUE + Style.BRIGHT,
        "warning": Fore.YELLOW + Style.BRIGHT
    }
    print(colors.get(msg_type, Fore.WHITE) + text + Style.RESET_ALL)

# Load contacts from file during startup
def load_contacts():
    if Path(CONTACTS_FILE).exists():
        with open(CONTACTS_FILE, "rb") as f:
            global book
            book = pickle.load(f)

# Save contacts to file before exiting
# Save the AddressBook object as a binary file
# pickle allows for complex objects to be serialized
def save_contacts():
    with open(CONTACTS_FILE, "wb") as f:
        pickle.dump(book, f)

# Exit handler
def exit_handler():
    print_colored("\nSaving contacts... Good bye!", "warning")
    save_contacts()
    sys.exit(0)

# Prepare user input for command and arguments
def parse_input(user_input: str):
    user_input = user_input.strip()
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

# Add a contact or update an existing one
@input_error
def add_contact(args, book: AddressBook):
    name = args[0]
    phone = args[1] if len(args) > 1 else None
    record = book.find(name)
    message = "✅ Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "✅ Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"❌ Error: Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"🔄 Contact {name} updated."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return str(record)
    return f"❌ Error: Contact {name} not found."

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "📭 No contacts saved."
    output = "\n📇 Contacts List:\n"
    for record in book.data.values():
        output += f"📌 {record}\n"
    return output.strip()

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        return f"❌ Error: Contact {name} not found."
    record.add_birthday(birthday)
    return f"🎂 Birthday for {name} added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"🎂 {name}'s birthday is on {record.birthday}"
    elif record:
        return f"📭 No birthday found for {name}."
    return f"❌ Error: Contact {name} not found."

@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "📭 No upcoming birthdays this week."
    output = "🎉 Upcoming Birthdays:\n"
    for item in upcoming:
        output += f"📌 {item['name']} — {Fore.MAGENTA}{item['congratulation_date']}{Style.RESET_ALL}\n"
    return output.strip()

@input_error
def handle_command(user_input: str):
    command, args = parse_input(user_input)
    match command:
        case "hello":
            return "👋 How can I help you?"
        case "add":
            return add_contact(args, book)
        case "change":
            return change_contact(args, book)
        case "phone":
            return show_phone(args, book)
        case "add-birthday":
            return add_birthday(args, book)
        case "show-birthday":
            return show_birthday(args, book)
        case "birthdays":
            return birthdays(book)
        case "all":
            return show_all(book)
        case "help":
            return ("ℹ️ Available commands:\n"
                    "  hello\n  add <name> <phone>\n  change <name> <old_phone> <new_phone>\n"
                    "  phone <name>\n  add-birthday <name> <dd.mm.yyyy>\n  show-birthday <name>\n"
                    "  birthdays\n  all\n  help\n  exit | close")
        case "exit" | "close":
            exit_handler()
        case _:
            return "❌ Invalid command. Type 'help' to see available commands."

def main():
    load_contacts()
    print_colored("Welcome to the assistant bot!", "info")
    try:
        while True:
            command = input(Fore.YELLOW + "Enter a command: " + Style.RESET_ALL)
            response = handle_command(command)
            if response:
                print_colored(response, "success" if "✅" in response or "🔄" in response or "🎂" in response else "error" if "❌" in response else "info")
    except KeyboardInterrupt:
        exit_handler()

if __name__ == '__main__':
    main()
