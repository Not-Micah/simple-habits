from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.card import MDCard
#####
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDIconButton
#####
from data import check_date, read_habits, write_habits, write_color, get_current_day, icon_list
#####
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineListItem
from kivy.uix.button import Button
######
from threading import Thread
from kivy.clock import mainthread, Clock
######
from datetime import datetime
from kivy.animation import Animation
######
from kivy.properties import BooleanProperty
from android.runnable import run_on_ui_thread
from jnius import autoclass


Color = autoclass("android.graphics.Color")
WindowManager = autoclass('android.view.WindowManager$LayoutParams')
activity = autoclass('org.kivy.android.PythonActivity').mActivity

class HexChanger(MDBoxLayout):
    pass

class IconSlider(MDBoxLayout):
    pass

class EditHabit(MDBoxLayout):
    pass

class CreateHabit(MDBoxLayout):
    pass

class HabitItem(OneLineAvatarIconListItem):
    pass

class CreateItem(OneLineAvatarIconListItem):
    pass

class HabitCard(MDFloatLayout):
    pass

class DayButton(Button):
    pass

class MainApp(MDApp):
    isready = BooleanProperty(False)

    @run_on_ui_thread
    def statusbar(self):
        window = activity.getWindow()
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor("#FFFFFF")) 
        window.setNavigationBarColor(Color.parseColor("#FFFFFF"))

    def on_start(self):
        Animation(opacity=1, duration=0).start(self.root.ids.navigation)
        self.isready = True

    def on_isready(self, *largs):
        def load_all(*l):
            # intializing variables
            self.habits = read_habits()
            self.current_habit = ""
            self.daily_habits = []

            # initializing contstants
            self.colors = {0:[0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0], 1:[0.12941176470588237, 0.5882352941176471, 0.9529411764705882, 1.0]}

            check_date(self.habits) 
            self.load_daily_habits()

            ######
            self.root.ids.home_date.text = datetime.today().strftime('%d %b, %a')
            self.load_counter()  

            ######
            self.hex_dialog = MDDialog(title="Color Changer", type="custom", content_cls=HexChanger())

            ######
            self.load_icon_changer()

            ######
            self.load_habit_cards()

            ######
            self.edit_dialog = MDDialog(title="Edit Habit", type="custom", content_cls=EditHabit())
            self.create_dialog = MDDialog(title="Edit Habit", type="custom", content_cls=CreateHabit())

            ######
            self.load_habit_items()

            ######
            self.statusbar()

        Clock.schedule_once(load_all, .1)

    @mainthread
    def load_daily_habits(self):
        day_index = get_current_day()

        self.daily_habits = [
            habit for habit in self.habits if habit["days"][day_index] == 1
            ]

    @mainthread
    def load_habit_cards(self):
        self.root.ids.card_holder.clear_widgets()

        for i in range(len(self.daily_habits)):
            # registering the habit data
            habit_card = HabitCard()
            habit_card.ids.card_icon.icon = self.daily_habits[i]["icon"]
            habit_card.ids.card_label.text = self.daily_habits[i]["habit"]

            habit_card.ids.card_completion.md_bg_color = self.root.ids.home_date.color

            self.root.ids.card_holder.add_widget(habit_card)
            
            # registering the progress already made 
            habit_card.ids.card_completion.md_bg_color = self.habits[i]["color"]
            habit_card.ids.card_completion.size_hint_x = self.habits[i]["current"]/self.habits[i]["freq"] * 1
            self.update_progress(habit_card, self.habits[i]["freq"])

    @mainthread
    def load_counter(self):
        self.remaining_daily = len([habit for habit in self.daily_habits if habit["current"] != habit["freq"]])
        if self.remaining_daily == 1:
            self.root.ids.home_count.text = f"{self.remaining_daily} Habit Left"
        else:
            self.root.ids.home_count.text = f"{self.remaining_daily} Habits Left"

    @mainthread
    def load_habit_items(self):
        self.root.ids.habit_menu.clear_widgets()

        for i in range(len(self.habits)):
            habit = HabitItem(text=self.habits[i]["habit"])

            # ensuring the top habit cannot be moved up
            if i == 0: 
                habit.ids.item_icon.disabled = True
            
            # adding the habit
            self.root.ids.habit_menu.add_widget(habit)
        
        # adding the create item
        self.root.ids.habit_menu.add_widget(CreateItem())

    def load_icon_changer(self):
        self.icon_dialog = MDDialog(title="Icons", type="custom", content_cls=IconSlider())

        page_mapping = {
            0: self.icon_dialog.content_cls.ids.page_one,
            1: self.icon_dialog.content_cls.ids.page_two,
            2: self.icon_dialog.content_cls.ids.page_three,
            3: self.icon_dialog.content_cls.ids.page_four,
            4: self.icon_dialog.content_cls.ids.page_five
        }

        for i, icon in enumerate(icon_list):
            page_number, index_on_page = divmod(i, 12)                              # each icon slider page has 12 slots...
            page = page_mapping.get(page_number)
            page.add_widget(MDIconButton(icon=icon, on_press=self.click_icon))

    ''' HABIT ITEM FUNCTIONS '''
    @mainthread
    def move_up(self, name):
        habit = name.text

        # define the update_habits function within move_up
        def update_habits(dt):
            for i in range(len(self.habits)):
                if self.habits[i]["habit"] == habit:
                    self.habits[i], self.habits[i-1] = self.habits[i-1], self.habits[i]

            # load the UI elements after a short delay
            Clock.schedule_once(lambda dt: self.load_daily_habits(), 0)
            Clock.schedule_once(lambda dt: self.load_habit_items(), 0.1)
            Clock.schedule_once(lambda dt: self.load_habit_cards(), 0.2)
            write_habits(self.habits)

        Clock.schedule_once(update_habits, 0)

    def click_day(self, item):
        if item.color == [0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0]:
            item.color = "#2196F3"
        else:
            item.color = "#808080"

    def click_icon(self, btn):
        for i in range(len(self.habits)):
            if self.habits[i]["habit"] == self.current_habit.ids.card_label.text:
                self.habits[i]["icon"] = btn.icon
                break

        self.current_habit.ids.card_icon.icon = btn.icon
        write_habits(self.habits)
        self.icon_dialog.dismiss()

    @mainthread
    def edit_habit_dg(self, item):
        habit = item.text

        for i in range(len(self.habits)):
            if self.habits[i]["habit"] == habit:
                current = self.habits[i]
                break

        week = current["days"]
        dialog = self.edit_dialog.content_cls.ids

        # displaying current settings
        dialog.habit.text = current["habit"]
        dialog.monday.color = self.colors[week[0]]
        dialog.tuesday.color = self.colors[week[1]]
        dialog.wednesday.color = self.colors[week[2]]
        dialog.thursday.color = self.colors[week[3]]
        dialog.friday.color = self.colors[week[4]]
        dialog.saturday.color = self.colors[week[5]]
        dialog.sunday.color = self.colors[week[6]]
        dialog.frequency.text = str(current["freq"])
        dialog.color.text = str(current["color"])

        # opening the dialog
        self.edit_dialog.open()

    def edit_habit(self):
        hex_code = set('0123456789abcdef')

        # Define the update_habit function within edit_habit
        def update_habit():
            for i in range(len(self.habits)):
                if self.habits[i]["habit"] == self.current_habit.text:
                    current = self.habits[i]
                    break

            dialog = self.edit_dialog.content_cls.ids
            week = current["days"]

            # updating the database
            current["habit"] = dialog.habit.text
            current["freq"] = int(dialog.frequency.text)
            week[0] = 0 if self.colors[0] == dialog.monday.color else 1
            week[1] = 0 if self.colors[0] == dialog.tuesday.color else 1
            week[2] = 0 if self.colors[0] == dialog.wednesday.color else 1
            week[3] = 0 if self.colors[0] == dialog.thursday.color else 1
            week[4] = 0 if self.colors[0] == dialog.friday.color else 1
            week[5] = 0 if self.colors[0] == dialog.saturday.color else 1
            week[6] = 0 if self.colors[0] == dialog.sunday.color else 1
            current["color"] = dialog.color.text.zfill(6)

            # load the UI elements
            self.load_habit_items()
            self.load_daily_habits()
            self.load_habit_cards()
            self.load_counter()
            write_habits(self.habits)

        # create a new thread and start it to run update_habit asynchronously
        dialog = self.edit_dialog.content_cls.ids
        if dialog.frequency.text and dialog.habit.text and len(dialog.color.text) <= 6 and len(dialog.color.text) >=1 and all(c in hex_code for c in dialog.color.text.lower()):
            Thread(target=update_habit).start()
            self.edit_dialog.dismiss()

    @mainthread
    def create_habit_dg(self):
        self.create_dialog.open()

    def create_habit(self):
        hex_code = set('0123456789abcdef')
        dialog = self.create_dialog.content_cls.ids

        ### validation
        if self.create_dialog.content_cls.ids.habit.text == "":
            self.create_dialog.content_cls.ids.habit.required = True

        if self.create_dialog.content_cls.ids.frequency.text == "":
            self.create_dialog.content_cls.ids.frequency.required = True

        if dialog.frequency.text and dialog.habit.text and len(dialog.color.text) <= 6 and len(dialog.color.text) >=1 and all(c in hex_code for c in dialog.color.text.lower()):
            new = {'habit': '', 'icon':'alpha-a-box', 'days': [], 'freq': 0, 'current':0, 'color':''}
            current = self.create_dialog.content_cls.ids

            new["habit"] = current.habit.text
            new["color"] = current.color.text.zfill(6)
            new["days"].append(0 if self.colors[0] == current.monday.color else 1)
            new["days"].append(0 if self.colors[0] == current.tuesday.color else 1)
            new["days"].append(0 if self.colors[0] == current.wednesday.color else 1)
            new["days"].append(0 if self.colors[0] == current.thursday.color else 1)
            new["days"].append(0 if self.colors[0] == current.friday.color else 1)
            new["days"].append(0 if self.colors[0] == current.saturday.color else 1)
            new["days"].append(0 if self.colors[0] == current.sunday.color else 1)
            new["freq"] = int(current.frequency.text)

            self.create_dialog.dismiss()
            self.create_dialog.content_cls.ids.habit.required = False
            self.create_dialog.content_cls.ids.frequency.required = False

            # define the update_habit_data function within create_habit and run it in a separate thread
            def update_habit_data():
                # add new habit data to the list and update the UI elements
                self.habits.append(new)
                self.load_habit_items()
                self.load_daily_habits()
                self.load_habit_cards()
                self.load_counter()
                write_habits(self.habits)

            # create a new thread and start it to run update_habit_data asynchronously
            Thread(target=update_habit_data).start()

    def delete_habit(self):
        # define the update_habits function within delete_habit
        def update_habits():
            for i in range(len(self.habits)):
                if self.habits[i]["habit"] == self.current_habit.text:
                    self.habits.pop(i)
                    break

            # load the UI elements
            self.load_habit_items()
            self.load_daily_habits()
            self.load_habit_cards()
            self.load_counter()
            write_habits(self.habits)

        # create a new thread and start it to run update_habits asynchronously
        Thread(target=update_habits).start()
        self.edit_dialog.dismiss()

    ''' HABIT CARD FUNCTIONS '''
    @mainthread
    def click_habit(self, card):
        for i in range(len(self.habits)):
            if self.habits[i]['habit'] == card.ids.card_label.text:
                index = i
                break

        fraction = 1 / self.habits[index]['freq']
        value = card.ids.card_completion.size_hint_x

        if round(value, 1) + 0.1 <= 1:
            card.ids.card_completion.size_hint_x += fraction
            self.habits[index]['current'] += 1
        elif round(value, 1) + 0.1 > 1:
            card.ids.card_completion.size_hint_x = 0.0000000001
            self.habits[index]['current'] = 0
        
        self.update_progress(card, self.habits[index]['freq'])
        self.load_counter()
        write_habits(self.habits)

    @mainthread
    def update_progress(self, card, freq):
        completion = card.ids.card_completion.size_hint_x/1 * freq
        card.ids.card_fraction.text = f"{round(completion)}/{freq}"

if __name__=="__main__":
    MainApp().run()