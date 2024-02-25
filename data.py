import ast
import json
import datetime

def read_date():
    with open("date.txt", 'r') as file:
        date_str = file.read().strip()
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def check_date(habits):
    current_date = datetime.datetime.now().date()
    stored_date = read_date()

    if stored_date != current_date:
        with open("date.txt", 'w') as file:
            file.write(current_date.strftime('%Y-%m-%d'))
        
        for habit in habits:
            habit["current"] = 0

def write_habits(habits):
    with open("habits.txt", "w") as file:
        for habit in habits:
            # Convert the habit dictionary to a string and write it as a line in the file
            file.write(str(habit) + "\n")

def read_habits():
    habits = []
    with open("habits.txt", "r") as file:
        for line in file:
            # Parse the line as a dictionary using ast.literal_eval
            habit_dict = ast.literal_eval(line.strip())

            # Append the habit dictionary to the habits list
            habits.append(habit_dict)

    return habits

def write_color(colors):
    with open('color.txt', 'w') as file:
        json.dump(colors, file)

def get_current_day():
    return datetime.datetime.now().weekday()

icon_list = [
    "arm-flex", "weight-lifter", "swim", "face-man", "face-woman",
    "heart", "medication", "food", "greenhouse",
    "briefcase", "book", "broom", "calculator", "cup-water",
    "alarm", "cellphone", "code-braces-box",
    "alert", "all-inclusive-box", "weather-sunny",
    "account",
    "pencil", "eraser",
    "alpha-a-box", "alpha-b-box", "alpha-c-box", "alpha-d-box", "alpha-e-box",
    "alpha-f-box", "alpha-g-box", "alpha-h-box", "alpha-i-box", "alpha-j-box",
    "alpha-k-box", "alpha-l-box", "alpha-m-box", "alpha-n-box", "alpha-o-box",
    "alpha-p-box", "alpha-q-box", "alpha-r-box", "alpha-s-box", "alpha-t-box",
    "alpha-u-box", "alpha-v-box", "alpha-w-box", "alpha-x-box", "alpha-y-box",
    "alpha-z-box"
]

day_indexes = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}

# habits = [{"habit": "Drink vitamins", "icon": "vitamins", "days": [1, 1, 1, 1, 1, 1, 1], "freq": 2},
#             {"habit": "Exercise", "icon": "fitness", "days": [1, 1, 0, 1, 1, 1, 0], "freq": 1}]

# write_color([2.323, 5.432, 1.3123, 1])
# print(read_color())

# print(get_current_day())