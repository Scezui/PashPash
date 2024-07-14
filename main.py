from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp, sp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.uix.togglebutton import ToggleButton
from kivymd.uix.button import MDIconButton
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import IRightBodyTouch
from kivy.utils import get_color_from_hex
from kivymd.uix.menu import MDDropdownMenu
import random
import string
import sqlite3
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
import csv
from kivy.app import App
import os
import traceback
from kivy.utils import platform
from kivymd.uix.button import MDRaisedButton
from kivy.utils import platform
from kivy.clock import Clock
from kivy.clock import mainthread
from secure_storage import get_cipher_suite
from kivy.core.clipboard import Clipboard


cipher_suite = get_cipher_suite()

# For Android 10, export files
def get_downloads_dir_android():
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
    downloads_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
    return downloads_dir

def get_database_path():
    if platform == 'android':
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'passwords.db')
    else:
        return 'passwords.db'

def setup_database_connection():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_add TEXT,
                    username TEXT,
                    website TEXT,
                    year TEXT,
                    password TEXT)''')
    conn.commit()
    
    return conn, cursor

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(3)
        self.size_hint = (0.8, None)
        self.height = dp(400)
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.2)  # Semi-transparent black for shadow
            self.shadow = RoundedRectangle(size=(self.width + dp(10), self.height + dp(10)),
                                        pos=(self.x - dp(5), self.y - dp(5)),
                                        radius=[dp(10)])
            # Card
            Color(1, 1, 1, 1)  # Original card color
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        # Update shadow position and size
        self.shadow.pos = (self.x - dp(5), self.y - dp(5))
        self.shadow.size = (self.width + dp(10), self.height + dp(10))
        # Update card position and size
        self.rect.pos = self.pos
        self.rect.size = self.size


class IntegerInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if substring.isdigit():
            return super().insert_text(substring, from_undo=from_undo)


class PasswordGeneratorWidget(Screen):
    def __init__(self, **kwargs):
        super(PasswordGeneratorWidget, self).__init__(**kwargs)

        self.card = Card()
        self.card.pos_hint = {'center_x': 0.5, 'top': 0.88}

        # Label and Input for password length
        length_label = Label(text='Password Length:', halign='left', color=(0, 0, 0, 1), bold=True, font_size=sp(16))
        length_label.bind(size=length_label.setter('text_size'))
        self.card.add_widget(length_label)
        self.password_length_input = TextInput(text='15', multiline=False, hint_text='Enter password length',
                                                font_size=sp(14), height=dp(40))
        self.card.add_widget(self.password_length_input)

        # Label and Input for password length
        email = Label(text='Email Adress:', halign='left', color=(0, 0, 0, 1), bold=True, font_size=sp(16))
        email.bind(size=email.setter('text_size'))
        self.card.add_widget(email)
        self.email = TextInput(multiline=False, hint_text='Enter email address',
                                                font_size=sp(14), height=dp(50))
        self.card.add_widget(self.email)

        # Label and Input for username
        user_label = Label(text='Username:', halign='left', color=(0, 0, 0, 1), bold=True, font_size=sp(16))
        user_label.bind(size=user_label.setter('text_size'))
        self.card.add_widget(user_label)
        self.username = TextInput(multiline=False, hint_text='Enter Username:', font_size=sp(14), height=dp(40))
        self.card.add_widget(self.username)

        # Label and Input for website
        website_label = Label(text='Website:', halign='left', color=(0, 0, 0, 1), bold=True, font_size=sp(16))
        website_label.bind(size=website_label.setter('text_size'))
        self.card.add_widget(website_label)
        self.password_website = TextInput(multiline=False, hint_text='Enter website:', font_size=sp(14), height=dp(40))
        self.card.add_widget(self.password_website)

        # Label and Input for Year Created
        year_label = Label(text='Year:', halign='left', color=(0, 0, 0, 1), bold=True, font_size=sp(16))
        year_label.bind(size=year_label.setter('text_size'))
        self.card.add_widget(year_label)
        self.year = IntegerInput(multiline=False, hint_text='Enter Year:', font_size=sp(14), height=dp(40))
        self.card.add_widget(self.year)

        # Button to generate password
        self.generate_button = Button(text='Generate Password', font_size=sp(16), height=dp(50))
        self.generate_button.bind(on_press=self.generate_password)
        self.card.add_widget(self.generate_button)

        # Button to save password
        self.save_button = Button(text='Save Password', font_size=sp(16), height=dp(50))
        self.save_button.bind(on_press=self.save_password)
        self.card.add_widget(self.save_button)

        self.generated_password_label = TextInput(
            text='Your password will appear here',
            halign='center',
            size_hint=(0.8, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            readonly=True,
            multiline=False,
            font_size=sp(16)
        )
        self.card.add_widget(self.generated_password_label)

        self.add_widget(self.card)

    def get_user_input(self):
        """Fetch user input values and return them."""
        email_add = str(self.email.text)
        username = str(self.username.text)
        website = str(self.password_website.text)
        year = str(self.year.text)
        return email_add, username, website, year


    def generate_password(self, instance):
        email_add, username, website, year = self.get_user_input()
        punctuation = random.choice('.!_')  # Choose one punctuation randomly
        password_parts = [website, username, punctuation, year]

        # Handle default value for password length
        password_length_text = self.password_length_input.text.strip()
        if not password_length_text:
            self.generated_password_label.text = "Please enter a password length"
            return

        try:
            length = int(password_length_text)
            if length <= 8:
                self.generated_password_label.text = "Password length must be greater than 8"
                return
        except ValueError:
            self.generated_password_label.text = "Invalid input for password length"
            return

        leet_dict = {
            'a': '4', 'b': '8', 'c': '<', 'd': '|)', 'e': '3', 'g': '6', 'h': '#', 'i': '1',
            'l': '1', 'o': '0', 'q': '0,','s': '5', 't': '7','z': '2',
            '0': 'O', '1': 'L', '2': 'Z', '3': 'E', '4': 'A', '5': 'S', '6': 'G', '7': 'T', '8': 'B', '9': 'g'
        }

        random.shuffle(password_parts)
        password = ''.join(password_parts).replace(' ', '')
        if len(password) < length:
            password += ''.join(random.choice(string.ascii_letters + string.digits + punctuation) for _ in
                                range(length - len(password)))

        password_leet = ''
        for char in password:
            if char.isalpha() and random.random() < 0.2:  # 50% probability to convert to Leet speak
                password_leet += leet_dict.get(char.lower(), char)
            else:
                password_leet += char

        self.generated_password_label.text = password_leet

    
    def encrypt_password(self, plain_pass):
        cipher_text = cipher_suite.encrypt(plain_pass.encode())
        return cipher_text

    def save_password(self, instance):
        email_add, username, website, year = self.get_user_input()

        password = self.generated_password_label.text
        encrypted_password = self.encrypt_password(password)

        # Save to SQLite database
        conn, cursor = setup_database_connection()

        # Insert data into table
        cursor.execute('INSERT INTO passwords (email_add, username, website, year, password) VALUES (?, ?, ?, ?, ?)',
                    (email_add, username, website, year, encrypted_password))
        conn.commit()

        # Close cursor and connection
        cursor.close()
        conn.close()

class PasswordListItem(TwoLineAvatarIconListItem):
    def __init__(self, password_manager, **kwargs):
        super().__init__(**kwargs)
        self.password_manager = password_manager
        self.option_button = OptionButton(self, self.password_manager)
        self.add_widget(BoxLayout(size_hint_x=None, width=dp(48)))  # Add a spacer widget
        self.add_widget(self.option_button)  # Add the option button

from kivymd.uix.list import OneLineListItem

class OptionButton(IRightBodyTouch, MDIconButton):
    def __init__(self, list_item, password_manager, **kwargs):
        super().__init__(**kwargs)
        self.list_item = list_item
        self.password_manager = password_manager
        self.icon = "dots-vertical"
        self.pos_hint = {"center_y": .5}
        self.on_release = self.show_options
        self.menu = None
        self.confirm_popup = None  # Initialize confirm_popup attribute


    def show_options(self):
        self.menu = MDDropdownMenu(
            caller=self,
            items=[
                {
                    "text": "Delete",
                    "viewclass": "OneLineListItem",
                    "on_release": self.show_delete_confirmation
                },
                {
                    "text": "Copy to Clipboard",
                    "viewclass": "OneLineListItem",
                    "on_release": self.copy_to_clipboard
                }
            ],
            width_mult=2,
            pos_hint={'right': 1}  # Attempt to align the menu's right edge with the right edge of the screen

        )
        self.menu.open()

    def show_delete_confirmation(self, *args):
        if self.menu:
            self.menu.dismiss()

        content = BoxLayout(orientation='vertical')
        message = Label(text="Are you sure you want to delete this item?", size_hint_y=None, height=dp(50))
        content.add_widget(message)

        buttons = BoxLayout(size_hint_y=None, height=dp(50))
        yes_button = Button(text='Yes')
        no_button = Button(text='No')
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)

        content.add_widget(buttons)

        self.confirm_popup = Popup(
            title='Confirm Deletion',
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(160))
        )
        yes_button.bind(on_release=self.delete_item)
        no_button.bind(on_release=self.confirm_popup.dismiss)
        self.confirm_popup.open()

    def delete_item(self, *args):
        self.password_manager.delete_selected(self.list_item)
        if self.confirm_popup:
            self.confirm_popup.dismiss()
    
    def copy_to_clipboard(self):
        id = self.password_manager.id_map.get(self.list_item)
        if id is not None:
            conn, cursor = setup_database_connection()
            cursor.execute('SELECT password from passwords WHERE id=?', (id,))
            row = cursor.fetchone()
            conn.close

            if row:
                encrypted_password = row[0]
                decrypted_password = self.password_manager.decrypt_password(encrypted_password)
                Clipboard.copy(decrypted_password)
        
        if self.menu:
            self.menu.dismiss()
            self.show_popup("Password copied to clipboard!")

    def show_popup(self, message):
        popup = Popup(
            title='Notification',
            content=Label(text=message, size_hint_y=None, height=dp(50)),
            size_hint=(None, None),
            size=(dp(250), dp(150))
        )
        popup.open()


class PasswordManagerWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_items = []
        self.selected_color = get_color_from_hex('#00FF00')  # Green color
        self.long_press_event = None

        
        # Create a ScrollView
        self.scroll = ScrollView(size_hint=(1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.55})
        
        # Create MDList
        self.list = MDList()
        self.scroll.add_widget(self.list)
        self.add_widget(self.scroll)

        # Create a BoxLayout for buttons
        self.button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(56),
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )

        # Create Export to CSV button
        self.export_csv = MDRaisedButton(
            text="Export to CSV",
            size_hint=(1, None),
            height=dp(56)
        )
        self.export_csv.bind(on_release=self.export_to_csv)
        self.button_layout.add_widget(self.export_csv)

        # Add the Eye button to toggle password visibility
        self.eye_button = MDIconButton(
            icon="eye-off",
            size_hint=(None, None),
            height=dp(56),
            width=dp(56),
            on_release=self.toggle_password_visibility
        )
        self.button_layout.add_widget(self.eye_button)

        # # Create Delete Selected button
        # self.delete_button = MDRaisedButton(
        #     text="Delete Selected",
        #     size_hint=(1, None),
        #     height=dp(56)
        # )
        # self.delete_button.bind(on_release=self.delete_selected)
        # self.button_layout.add_widget(self.delete_button)

        # Add button layout to the screen
        self.add_widget(self.button_layout)

        # Adjust the position of the button layout
        self.button_layout.pos_hint = {'center_x': 0.5, 'y': 0.02}
        self.hidden_passwords = True
        self.full_row_data = []
        self.selected_items = []

    def on_enter(self):
        self.fetch_passwords()

    def fetch_passwords(self):
        conn, cursor = setup_database_connection()
        cursor.execute('SELECT id, email_add, username, website, year, password FROM passwords')
        rows = cursor.fetchall()
        conn.close()

        self.list.clear_widgets()
        self.id_map = {}
        self.full_row_data = rows

        for row in rows:
            self.add_list_item(row)

    def add_list_item(self, row):
        id, email_add, username, website, year, encrypted_password = row
        decrypted_password = self.decrypt_password(encrypted_password)
        password_display = '*' * 8 if self.hidden_passwords else decrypted_password

        item = PasswordListItem(
            self,  # Pass self (PasswordManagerWidget instance) here
            text=f"{email_add} - {username}",
            secondary_text=f"{website} ({year}) - {password_display}"
        )
        item.bind(on_long_press=self.select_item)
        self.list.add_widget(item)

        self.id_map[item] = id

    def select_item_delayed(self, instance, touch):
        if self.long_press_event is not None:
            self.long_press_event.cancel()

        self.long_press_event = Clock.schedule_once(lambda dt: self.select_item(instance, touch), 0.5)
        touch.grab(self)  # Grab the touch event

    def select_item(self, instance, touch):
        if instance not in self.selected_items:
            instance.bg_color = self.selected_color
            self.selected_items.append(instance)
        else:
            instance.bg_color = (1, 1, 1, 1)  # Reset to default background color
            self.selected_items.remove(instance)

        touch.ungrab(self)  # Release the touch event
    def toggle_password_visibility(self, instance):
        self.hidden_passwords = not self.hidden_passwords
        self.eye_button.icon = "eye-off" if self.hidden_passwords else "eye"
        self.update_list_data()

    def update_list_data(self):
        self.list.clear_widgets()
        for row in self.full_row_data:
            self.add_list_item(row)

    def delete_selected(self, item):
        conn, cursor = setup_database_connection()
        
        id = self.id_map.get(item)
        if id is not None:
            cursor.execute('DELETE FROM passwords WHERE id=?', (id,))
            self.list.remove_widget(item)
            self.full_row_data = [row for row in self.full_row_data if row[0] != id]
            del self.id_map[item]  # Remove the item from id_map

        conn.commit()
        conn.close()
        
        # Update the list view
        self.update_list_data()

    def export_to_csv(self, *args):
        try:
            data = [row[1:] for row in self.full_row_data]  # Exclude ID
            column_headers = ['Email Address', 'Username', 'Website', 'Year', 'Password']

            # Export Path
            if platform == 'android':
                from androidstorage4kivy import SharedStorage
                shared_storage = SharedStorage()
                
                cache_dir = shared_storage.get_cache_dir()
                if not cache_dir:
                    raise Exception("Could not get cache directory")
                
                temp_file_path = os.path.join(cache_dir, 'passwords_export.csv')
                
                with open(temp_file_path, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(column_headers)
                    csv_writer.writerows(data)
                
                uri = shared_storage.copy_to_shared(temp_file_path, collection='DIRECTORY_DOCUMENTS')
                
                if uri:
                    export_path = uri.toString()
                else:
                    raise Exception("Failed to copy file to shared storage")
            else:
                export_path = 'passwords_export.csv'
                with open(export_path, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(column_headers)
                    csv_writer.writerows(data)

            popup = Popup(title='Success',
                        content=Label(text=f'Data exported successfully!\nFile location: {export_path}',
                                        text_size=(dp(250), None),
                                        size_hint_y=None, height=dp(100)),
                        size_hint=(None, None), size=(dp(300), dp(200)))
            popup.open()

        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            popup = Popup(title='Error',
                        content=Label(text=error_msg,
                                        text_size=(dp(250), None),
                                        size_hint_y=None, height=dp(100)),
                        size_hint=(None, None), size=(dp(300), dp(200)))
            popup.open()

    def decrypt_password(self, cipher_text):
        plain_password = cipher_suite.decrypt(cipher_text).decode()
        return plain_password

class PashPashApp(MDApp):
    def build(self):
        self.icon = 'assets/icon.jpg'
        self.screen_manager = ScreenManager()
        self.initialize_app()

        if platform == 'android':
            from android.permissions import check_permission, Permission
            # Check if permission is granted
            if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                self.check_permissions()
            else:
                # self.initialize_app()
                return self.root_layout
        # else:
        #     self.initialize_app()
        return self.root_layout


    def initialize_app(self):
        setup_database_connection()

        # Password Generator Screen
        self.password_generator_screen = PasswordGeneratorWidget(name='password_generator')
        self.screen_manager.add_widget(self.password_generator_screen)

        # Password Manager Screen
        self.password_manager_screen = PasswordManagerWidget(name='password_manager')
        self.screen_manager.add_widget(self.password_manager_screen)

        # Menu Layout
        self.menu_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            pos_hint={'top': 1}
        )

        # Password Generator Toggle Button
        self.password_generator_toggle = ToggleButton(
            text='Password Generator', 
            group='menu', 
            state='down',
            font_size=sp(16)
        )
        self.password_generator_toggle.bind(on_press=self.toggle_menu)
        self.menu_layout.add_widget(self.password_generator_toggle)

        # Password Manager Toggle Button
        self.password_manager_toggle = ToggleButton(
            text='Password Manager', 
            group='menu', 
            font_size=sp(16)
        )
        self.password_manager_toggle.bind(on_press=self.toggle_menu)
        self.menu_layout.add_widget(self.password_manager_toggle)

        # Root layout
        self.root_layout = FloatLayout()
        self.root_layout.add_widget(self.screen_manager)
        self.root_layout.add_widget(self.menu_layout)

    @mainthread
    def permission_callback(self, permissions, results):
        if all(results):
            pass
        else:
            popup = Popup(
                title='Permission Denied',
                content=Label(text='Storage permission is required for this app to function properly. Please grant the permission and restart the app. The app will close in 5 seconds.'),
                size_hint=(0.8, 0.4)
            )
            popup.bind(on_dismiss=self.stop)
            popup.open()
            # Schedule the app to close after 5 seconds
            Clock.schedule_once(self.stop, 5)
            self.check_permissions()

    def check_permissions(self):
        # Request permission
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE], self.permission_callback)
        return Label(text='Requesting permissions...')

    def toggle_menu(self, instance):
        if instance.state == 'down':
            if instance.text == 'Password Generator':
                self.screen_manager.current = 'password_generator'
            elif instance.text == 'Password Manager':
                self.screen_manager.current = 'password_manager'
                # Refresh the Password Manager screen
                self.password_manager_screen.fetch_passwords()

if __name__ == '__main__':
    try:
        PashPashApp().run()
    except Exception as e:
        with open('/storage/emulated/0/pashpash_error.log', 'w') as f:
            f.write(str(e))
            f.write(traceback.format_exc())