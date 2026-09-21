import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Mobile size set karne ke liye window (Desktop par mobile look)
Window.size = (360, 640)

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                amount REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def add_expense(self, item, amount):
        self.cursor.execute("INSERT INTO expenses (item, amount) VALUES (?, ?)", (item, amount))
        self.conn.commit()

    def get_expenses(self):
        self.cursor.execute("SELECT item, amount FROM expenses ORDER BY id DESC")
        return self.cursor.fetchall()

    def get_total(self):
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        res = self.cursor.fetchone()[0]
        return res if res else 0.0


class ExpenseTrackerApp(App):
    def build(self):
        self.db = Database()

        # Main Vertical Layout
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header Title
        title = Label(
            text="Kharcha Tracker", 
            font_size=24, 
            bold=True, 
            size_hint_y=None, 
            height=40
        )
        main_layout.add_widget(title)

        # Total Expense Display Label
        self.total_label = Label(
            text="Total Kharcha: ₹ 0.0", 
            font_size=20, 
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=None, 
            height=30
        )
        main_layout.add_widget(self.total_label)

        # Inputs Form
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=90)
        
        input_layout.add_widget(Label(text="Kahan Kharcha Hua?:", font_size=14))
        self.item_input = TextInput(hint_text="e.g., Chai, Grocery", multiline=False)
        input_layout.add_widget(self.item_input)

        input_layout.add_widget(Label(text="Kitna Rupe (₹):", font_size=14))
        self.amount_input = TextInput(hint_text="e.g., 50", input_filter='float', multiline=False)
        input_layout.add_widget(self.amount_input)

        main_layout.add_widget(input_layout)

        # Add Button
        add_btn = Button(
            text="Kharcha Add Karein", 
            size_hint_y=None, 
            height=45,
            background_color=(0.1, 0.6, 0.9, 1),
            bold=True
        )
        add_btn.bind(on_press=self.add_entry)
        main_layout.add_widget(add_btn)

        # Scrollable Expense History List
        history_title = Label(
            text="Purana Kharcha History:", 
            font_size=16, 
            bold=True,
            size_hint_y=None, 
            height=30
        )
        main_layout.add_widget(history_title)

        self.history_layout = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        scroll_view = ScrollView()
        scroll_view.add_widget(self.history_layout)
        main_layout.add_widget(scroll_view)

        # Load Saved Data
        self.update_ui()

        return main_layout

    def add_entry(self, instance):
        item = self.item_input.text.strip()
        amount_text = self.amount_input.text.strip()

        if item and amount_text:
            try:
                amount = float(amount_text)
                self.db.add_expense(item, amount)
                
                # Clear Inputs
                self.item_input.text = ""
                self.amount_input.text = ""
                
                # Refresh List & Total
                self.update_ui()
            except ValueError:
                pass

    def update_ui(self):
        # Update Total
        total = self.db.get_total()
        self.total_label.text = f"Total Kharcha: ₹ {total:.2f}"

        # Clear and Reload History List
        self.history_layout.clear_widgets()
        records = self.db.get_expenses()

        for item, amount in records:
            lbl_item = Label(text=item, size_hint_y=None, height=30, font_size=14)
            lbl_amount = Label(text=f"₹ {amount:.2f}", size_hint_y=None, height=30, font_size=14)
            self.history_layout.add_widget(lbl_item)
            self.history_layout.add_widget(lbl_amount)

if __name__ == "__main__":
    ExpenseTrackerApp().run()