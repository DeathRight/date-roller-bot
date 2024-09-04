from typing import Callable
import pyautogui
import keyboard
import pyperclip
from classes import OrderRow, DateValues, Config
import pygetwindow as gw
import time

# Wait times
short_wait = 0.01
medium_wait = 1
long_wait = 5

# Windows
window_size = (1520, 350)
window_position = (0, 0)

# Relative to window
update_button_position = (830,68)
order_number_list_position = (35, 152)
status_button_position = (170, 308)


def sleep(seconds: int):
    # Check if trying to exit
    if keyboard.is_pressed("esc"):
        exit()
    # If longer than 0.25 seconds, divide into steps
    if seconds > 0.25:
        for _ in range(int(seconds / 0.25)):
            time.sleep(0.25)
            if keyboard.is_pressed("esc"):
                exit()
        time.sleep(seconds % 0.25)
    else:
        time.sleep(seconds)
        if keyboard.is_pressed("esc"):
            exit()

############################################
# Pre and post update functions
############################################

def switch_to_queue_window():
    queue_window = gw.getWindowsWithTitle("Transfer Register Queue")[0]
    queue_window.activate()
    # Resize window
    queue_window.resizeTo(*window_size)
    # Move window to top left corner
    queue_window.moveTo(*window_position)
    sleep(short_wait)

def switch_to_order_window():
    order_window = gw.getWindowsWithTitle("Transfer Order Entry")[0]
    order_window.activate()
    # Resize window
    order_window.resizeTo(*window_size)
    # Move window to top left corner
    order_window.moveTo(*window_position)
    sleep(short_wait)

def pre_update(config: Config):
    switch_to_queue_window()
    if config["press_update"]:
        # Click update button
        pyautogui.click(*update_button_position)
        sleep(config["update_time"])

def find_first_column():
    # Repeat left arrow key and copy value to clipboard until two values are the same
    previous_value = None
    current_value = None
    while previous_value != current_value or previous_value is None:
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        previous_value = pyperclip.paste()
        pyautogui.press("left")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    print(f"First column found: {current_value}")

def index_queue_rows(config: Config, checker: Callable[[str], bool]) -> int:
    # Repeat up arrow key and copy value to clipboard until two values are the same
    previous_value = None
    current_value = None

    # Find the first row
    while previous_value != current_value or previous_value is None:
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        previous_value = pyperclip.paste()
        pyautogui.press("up")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()
        # Call checker on current_value, if it's false, press down
        # set current_value to previous_value, and break.
        # This is because checker should return false if we have gone too far.
        if not checker(current_value):
            pyautogui.press("down")
            current_value = previous_value
            break

    print(f"First row found: {current_value}")

    previous_value = None
    current_value = None
    # Find the last row
    while previous_value != current_value or previous_value is None:
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        previous_value = pyperclip.paste()
        config["rows"].append(OrderRow(order_number=previous_value, ship_date=None))
        pyautogui.press("down")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    print(f"Last row found: {current_value}")

    # Go back up to the first row
    while current_value != config["rows"][0]["order_number"]:
        pyautogui.press("up")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    print(f"Returned to first row: {current_value}")

    return len(config["rows"])

def post_update(config: Config):
    pyautogui.click(*order_number_list_position)
    sleep(short_wait)
    find_first_column()
    # Find first row, checking to make sure each copied string is a valid order number
    # (begins with T or S)
    index_queue_rows(config, lambda x: x[0] in ["T", "S"])
    # Go right 3 times to get to the "Ship Date" column
    for _ in range(3):
        pyautogui.press("right")
        sleep(short_wait)

############################################
# Order Open state functions
############################################

def index_order_rows(config: Config):
    # Repeat up arrow key and copy value to clipboard until two values are the same
    previous_value = None
    current_value = None

    rows: list[str] = []

    # Find the first row
    while previous_value != current_value or previous_value is None:
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        previous_value = pyperclip.paste()
        pyautogui.press("up")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    pyautogui.press("down")
    print(f"First row found: {current_value}")

    previous_value = None
    current_value = None

    # Find the last row
    while previous_value != current_value or previous_value is None:
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        previous_value = pyperclip.paste()
        rows.append(previous_value)
        pyautogui.press("down")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    print(f"Last row found: {current_value}")

    # Go back up to the first row
    while current_value != rows[0]:
        pyautogui.press("up")
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()

    print(f"Returned to first row: {current_value}")

    return rows

def check_shiprec_date(type: str, date: str, config: Config):
    date_timestamp = time.mktime(time.strptime(date, "%m/%d/%y"))
    if config["date_values"][type]["choice"] == "ALL":
        return True
    elif config["date_values"][type]["choice"] == "NEVER":
        return False
    elif config["date_values"][type]["choice"] == "LAST":
        return date_timestamp >= time.time() - int(config["date_values"][type]["value"]) * 86400
    elif config["date_values"][type]["choice"] == "SINCE":
        return date_timestamp >= config["date_values"][type]["value"]

def correct_status_column():
    # Check if the current column is the Ship/Received Dt column
    pyautogui.hotkey("ctrl", "c")
    sleep(short_wait)
    previous_value = pyperclip.paste()
    
    # Check if in date format
    try:
        time.strptime(previous_value, "%m/%d/%y")
    except ValueError:
        # We aren't in the correct column, move right until two values are the same
        previous_value = None
        current_value = None
        while previous_value != current_value or previous_value is None:
            pyautogui.hotkey("ctrl", "c")
            sleep(short_wait)
            previous_value = pyperclip.paste()
            pyautogui.press("right")
            pyautogui.hotkey("ctrl", "c")
            sleep(short_wait)
            current_value = pyperclip.paste()
        
        # Ship/Rec Dt column is 2nd from last column, so move left once
        pyautogui.press("left")
        sleep(short_wait)

def order_status(config: Config, rows: list[str]):
    changed = False
    # Set clipboard to first day of next month
    first_day_timestamp = time.time() + 2592000
    first_day = time.strftime("%m/01/%Y", time.localtime(first_day_timestamp))

    for row in rows:
        date_type = None
        if "Ship" in row:
            date_type = "ship"
        elif "Rece" in row:
            date_type = "receive"
        
        correct_status_column()
        # Check if row has "Ship" or "Rece" in it
        if date_type is not None and check_shiprec_date(date_type, config["rows"][config["current_row"]]["ship_date"], config):
            # Check if the date is already correct
            pyautogui.hotkey("ctrl", "c")
            sleep(short_wait)
            clipboard_data = pyperclip.paste()
            if clipboard_data != first_day:
                pyperclip.copy(first_day)
                # Paste clipboard into the cell
                pyautogui.hotkey("ctrl", "v")
                print(f"Updated row {config['current_row']} '{row}' to {pyperclip.paste()}")
                config["rows"][config["current_row"]]["changed_to"] = pyperclip.paste()

                changed = True

                pyautogui.press("enter")
                sleep(medium_wait)
        
        # Move to the next row
        pyautogui.press("down")
        sleep(medium_wait)
    
    print("Order status state finished, exiting back to queue.")
    keyboard.press_and_release(88)
    sleep(medium_wait)

    if changed:
        # Press enter twice to skip any possible popups
        pyautogui.press("enter")
        sleep(short_wait)
        pyautogui.press("enter")
        sleep(short_wait)
        pyautogui.press("tab")
        sleep(short_wait)
        pyautogui.press("enter")
        sleep(medium_wait)
    print("Exited back to queue.")

def open_order(config: Config):
    # Open the order in edit mode by pressing ctrl+e
    pyautogui.hotkey("ctrl", "e")
    sleep(long_wait)

    switch_to_order_window()

    # Press enter twice to skip any possible popups
    pyautogui.press("enter")
    sleep(short_wait)
    pyautogui.press("enter")
    sleep(short_wait)

    # Move to Status tab
    pyautogui.click(*status_button_position)
    sleep(medium_wait)

    # Press enter twice again to skip any possible popups
    pyautogui.press("enter")
    sleep(medium_wait)
    pyautogui.press("enter")
    sleep(medium_wait)

    # Find the first column
    find_first_column()

    # Move right twice to get to Order Status
    pyautogui.press("right")
    pyautogui.press("right")

    rows = index_order_rows(config)

    # Move right twice to get to Ship/Received Dt column
    pyautogui.press("right")
    sleep(short_wait)
    pyautogui.press("right")
    sleep(short_wait)

    order_status(config, rows)

############################################
# Queue state functions
############################################

def check_date(date: str, config: Config):
    # Check both ship and receive dates against parameters
    # If none of the parameters are met, return False
    # If any of the parameters are met, return True

    # Convert date to timestamp
    date_timestamp = time.mktime(time.strptime(date, "%m/%d/%y"))

    def check_date_value(date_value: DateValues):
        # Check if date is within range
        if date_value["choice"] == "ALL":
            return True
        elif date_value["choice"] == "NEVER":
            return False
        elif date_value["choice"] == "LAST":
            return date_timestamp >= time.time() - int(date_value["value"]) * 86400
        elif date_value["choice"] == "SINCE":
            return date_timestamp >= date_value["value"]
        
        return False
    
    return check_date_value(config["date_values"]["ship"]) or check_date_value(config["date_values"]["receive"])

def correct_queue_place(config: Config):
    # Check if the current column is the Ship Date column
    pyautogui.hotkey("ctrl", "c")
    sleep(short_wait)
    previous_value = pyperclip.paste()
    
    # Check if in date format
    try:
        time.strptime(previous_value, "%m/%d/%y")
    except ValueError:
        # We aren't in the correct column. First, move left until the value begins with T or S and has a number on the second character
        while previous_value[0] not in ["T", "S"] or not previous_value[1].isdigit():
            pyautogui.press("left")
            pyautogui.hotkey("ctrl", "c")
            sleep(short_wait)
            previous_value = pyperclip.paste()
        
        # Move up to try and find the order number we are supposed to be on
        while previous_value != config["rows"][config["current_row"]]["order_number"]:
            pyautogui.press("up")
            pyautogui.hotkey("ctrl", "c")
            sleep(short_wait)
            previous_value = pyperclip.paste()
            if previous_value[0] not in ["T", "S"] or not previous_value[1].isdigit():
                # Too far, go down one, and we will be at index 0
                pyautogui.press("down")
                sleep(short_wait)

                # Go down until we get to the right index
                for _ in range(config["current_row"]):
                    pyautogui.press("down")
                    sleep(short_wait)
                break
        
        # Move right 3 times to get to the "Ship Date" column
        for _ in range(3):
            pyautogui.press("right")
            sleep(short_wait)

def queue_state(config: Config):
    # Call check_date on each row in the queue
    # If true, open order then continue to next row
    # If false, continue to next row

    for index, row in enumerate(config["rows"]):
        # Update current_row
        config["current_row"] = index
        correct_queue_place(config)
    
        # Copy the current value to the clipboard
        pyautogui.hotkey("ctrl", "c")
        sleep(short_wait)
        current_value = pyperclip.paste()
    
        # Update the ship_date of the current row
        row["ship_date"] = current_value
        print(f"Checking row {index} '{row['order_number']}': {current_value}")
    
        # Check the date and open the order if necessary
        if check_date(current_value, config):
            print("Order opened.")
            open_order(config)
            switch_to_queue_window()
    
        # Move to the next row
        pyautogui.press("down")
        sleep(short_wait)
    
    print("Queue state finished.")


############################################
# Start bot
############################################

def start_bot(config: Config):
    print("Starting bot...")

    # Set initial values
    ship = config["date_values"]["ship"]
    rec = config["date_values"]["receive"]
    pre_update(config)
    post_update(config)
    queue_state(config)
    print("Bot finished.")

# TODO: Order Open State, Order Status State -> Check each line for "Ship" or "Rece" and change ship and receive date based on parameters
