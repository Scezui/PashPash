from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp, sp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivy.uix.togglebutton import ToggleButton
from kivymd.uix.button import MDIconButton
import random
import string
import sqlite3
from kivy.graphics import Color, RoundedRectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.popup import Popup
import csv
from kivy.app import App
import os
import traceback
from kivy.utils import platform
from kivymd.uix.button import MDRaisedButton

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

    def save_password(self, instance):
        email_add, username, website, year = self.get_user_input()

        password = self.generated_password_label.text

        # Save to SQLite database
        conn, cursor = setup_database_connection()

        # Insert data into table
        cursor.execute('INSERT INTO passwords (email_add, username, website, year, password) VALUES (?, ?, ?, ?, ?)',
                    (email_add, username, website, year, password))
        conn.commit()

        # Close cursor and connection
        cursor.close()
        conn.close()

class PasswordManagerWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.column_data = [
            ("Email Address", dp(40)),
            ("Username", dp(30)),
            ("Year", dp(20)),
            ("Website", dp(30)),
            ("Password", dp(30)),
        ]
        self.table = MDDataTable(
            size_hint=(0.95, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            use_pagination=True,
            check=True,
            column_data=self.column_data,
        )
        self.add_widget(self.table)

        # Create a BoxLayout for buttons
        self.button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(56),  # Standard height for buttons
            spacing=dp(10),  # Space between buttons
            padding=[dp(10), dp(10), dp(10), dp(10)]  # Padding around buttons
        )

        # Create Export to CSV button
        self.export_csv = MDRaisedButton(
            text="Export to CSV",
            size_hint=(1, None),
            height=dp(56)
        )
        self.export_csv.bind(on_release=self.export_to_csv)
        self.button_layout.add_widget(self.export_csv)

        # Create Delete Selected button
        self.delete_button = MDRaisedButton(
            text="Delete Selected",
            size_hint=(1, None),
            height=dp(56)
        )
        self.delete_button.bind(on_release=self.delete_selected)
        self.button_layout.add_widget(self.delete_button)

        # Add button layout to the screen
        self.add_widget(self.button_layout)

        # Adjust the position of the button layout
        self.button_layout.pos_hint = {'center_x': 0.5, 'y': 0.02}

    def export_to_csv(self, *args):
        try:
            conn, cursor = setup_database_connection()
            
            # Fetch data from the database
            cursor.execute("SELECT * FROM passwords")
            all_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            data = [row[1:] for row in all_data]  # This slices each tuple to exclude the first element (ID)
            column_headers = ['Email Address', 'Username', 'Website', 'Year', 'Password']
            
            # Determine the export file path
            if platform == 'android':
                from android.storage import primary_external_storage_path
                export_path = os.path.join(primary_external_storage_path(), 'Download', 'passwords_export.csv')
            else:
                export_path = 'passwords_export.csv'
            
            # Write data to CSV file
            with open(export_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Write column headers
                csv_writer.writerow(column_headers)
                
                # Write data
                csv_writer.writerows(data)
            
                popup = Popup(title='Success',
                            content=Label(text=f'Data exported to {export_path} successfully!',
                                            text_size=(dp(250), None),  # Wrap text if it's too long
                                            size_hint_y=None,
                                            height=dp(100)),  # Adjust height as needed
                            size_hint=(None, None),
                            size=(dp(300), dp(200)))  # Fixed size in density-independent pixels
                popup.open()
        
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)  # This will appear in your Android logcat
            popup = Popup(title='Error',
                        content=Label(text=error_msg),
                        size_hint=(None, None), size=(400, 300))
            popup.open()

    def on_enter(self):
        # This method is called every time the screen is entered
        self.fetch_passwords()

    def fetch_passwords(self):
        conn, cursor = setup_database_connection()
        cursor.execute('SELECT * FROM passwords')
        rows = cursor.fetchall()
        conn.close()

        self.row_data = []
        for row in rows:
            _, email_add, username, website, year, password = row
            self.row_data.append((email_add, username, year, website, password))

        self.table.row_data = self.row_data
        # Force table update
        self.table.update_row_data(self.table, self.row_data)

    def delete_selected(self, instance):
        checked_rows = self.table.get_row_checks()
        if not checked_rows:
            return
        conn, cursor = setup_database_connection()

        for row in checked_rows:
            email_add, username, year, website, password = row
            cursor.execute('DELETE FROM passwords WHERE email_add=? AND username=? AND year=? AND website=? AND password=?',
                        (email_add, username, year, website, password))

        conn.commit()
        conn.close()

        # Refresh table
        self.fetch_passwords()


class PashPashApp(MDApp):
    def build(self):
        setup_database_connection()
        self.icon = 'assets/icon.jpg'
        self.screen_manager = ScreenManager()

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
        self.password_generator_toggle = ToggleButton(text='Password Generator', group='menu', state='down',
                                                    font_size=sp(16))
        self.password_generator_toggle.bind(on_press=self.toggle_menu)
        self.menu_layout.add_widget(self.password_generator_toggle)

        # Password Manager Toggle Button
        self.password_manager_toggle = ToggleButton(text='Password Manager', group='menu', font_size=sp(16))
        self.password_manager_toggle.bind(on_press=self.toggle_menu)
        self.menu_layout.add_widget(self.password_manager_toggle)

        # Root layout
        self.root_layout = FloatLayout()
        self.root_layout.add_widget(self.screen_manager)
        self.root_layout.add_widget(self.menu_layout)

        return self.root_layout

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