import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkcalendar import DateEntry
from bot import start_bot
from classes import DateInfo, DateValues, Config

def ask_date_with_picker(title):
    date_picker_window = tk.Toplevel(root)
    date_picker_window.title(title)
    date_picker_window.geometry("300x150")  # Set a fixed width and reduced height for the dialog window
    date_entry = DateEntry(date_picker_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.pack(padx=10, pady=10)
    date_entry.focus_force()

    selected_date = None

    def on_date_select():
        nonlocal selected_date
        selected_date = date_entry.get_date().strftime("%m/%d/%Y")
        date_picker_window.destroy()

    def on_cancel():
        date_picker_window.destroy()

    button_frame = tk.Frame(date_picker_window)
    button_frame.pack(pady=10)
    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)
    select_button = tk.Button(button_frame, text="Select", command=on_date_select)
    select_button.pack(side=tk.LEFT, padx=5)

    date_picker_window.protocol("WM_DELETE_WINDOW", on_cancel)
    date_picker_window.wait_window()

    return selected_date

def update_label(previous: DateValues, date_type: str, label: tk.Label, choice: str, value: int):
    # If ALL or NEVER, empty. Else, show value
    if choice == "ALL" or choice == "NEVER":
        label.config(text="")
    else:
        if choice == "SINCE":
            # Convert value to date in MM/DD/YYYY format
            label.config(text=f"Since {time.strftime("%m/%d/%Y", time.localtime(value))}")
        elif choice == "LAST":
            label.config(text=f"Last {value} Days")
    # Update previous values
    previous[date_type]["choice"] = choice
    previous[date_type]["value"] = value


def ask_date(previous: DateValues, date_type: str, choice: tk.StringVar, value: tk.StringVar, label: tk.Label):
    previous_choice = str(previous[date_type]["choice"])
    previous_value = int(previous[date_type]["value"])
    date = None

    if choice.get() == "SINCE":
        while True:
            date = ask_date_with_picker(f"Roll {date_type.capitalize()} Dates Since Date")
            if date is None:
                choice.set(previous_choice)
                value.set(previous_value)
                break
            try:
                # Convert date to integer and update value
                value.set(int(time.mktime(time.strptime(date, "%m/%d/%Y"))))
                break
            except ValueError:
                messagebox.showerror("Invalid Date", "Enter date in CORRECT format (MM/DD/YYYY)")
    elif choice.get() == "LAST":
        while True:
            date = simpledialog.askinteger(f"Roll {date_type.capitalize()} Dates From Last X Days", f"Enter number of days to roll {date_type.capitalize()} Dates")
            if date is None:
                choice.set(previous_choice)
                value.set(previous_value)
                break
            if isinstance(date, int):
                value.set(str(date))
                break
            else:
                messagebox.showerror("Invalid Number", "Enter a valid number of days")
    update_label(previous, date_type, label, choice.get(), int(value.get()))
    return value.get()

# GUI setup

def show_success_window():
    success_window = tk.Toplevel()
    success_window.title("Success")
    # Focus window
    success_window.focus_force()

    success_label = tk.Label(success_window, text="Bot finished successfully!", font=("Helvetica", 16))
    success_label.pack(pady=20)

    # Function to run when OK or close button is clicked
    def on_closing():
        success_window.destroy()
        root.quit()
    
    success_window.protocol("WM_DELETE_WINDOW", on_closing)

    tk.Button(success_window, text="OK", command=on_closing, width=20).pack(pady=10)

def show_countdown_window(config):
    countdown_window = tk.Toplevel()
    countdown_window.title("Countdown")

    countdown_label = tk.Label(countdown_window, text="", font=("Helvetica", 16))
    countdown_label.pack(pady=20)

    cancel_var = tk.BooleanVar(value=False)
    def cancel():
        cancel_var.set(True)
        countdown_window.destroy()

    tk.Button(countdown_window, text="Cancel", command=cancel, width=20).pack(pady=10)

    def countdown(seconds):
        if cancel_var.get():
            countdown_label.config(text="Cancelled")
            return
        
        if seconds > 0:
            countdown_label.config(text=f"Starting in {seconds}... Take your hands off the keyboard and mouse.")
            countdown_window.after(1000, countdown, seconds - 1)
        else:
            countdown_label.config(text="Starting now!")
            countdown_window.destroy()
            start_bot(config)
            show_success_window()

    countdown(3)


def start_gui():
    global root
    root = tk.Tk()
    root.withdraw()

    # Create window
    window = tk.Toplevel(root)
    window.title("Date Roller")

    # Object to store previous values
    previous: DateValues = {
        "ship": {
            "choice": "ALL",
            "value": 0
        },
        "receive": {
            "choice": "ALL",
            "value": 0
        }
    }

    def on_closing():
        root.quit()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    # Config parameters
    # -> Update Queue? Yes/No radio button
    update_queue = tk.IntVar()
    update_queue.set(0)

    tk.Label(window, text="Update Queue?").grid(row=0, column=0, sticky='w')
    tk.Radiobutton(window, text="Yes", variable=update_queue, value=1).grid(row=0, column=1, sticky='w')
    tk.Radiobutton(window, text="No", variable=update_queue, value=0).grid(row=0, column=2, sticky='w')

    # -> Update Time: Entry
    update_time = tk.IntVar()
    update_time.set(50)
    tk.Label(window, text="Update Time (s)").grid(row=0, column=3, sticky='w')
    update_time_entry = tk.Entry(window, textvariable=update_time, width=4, state='disabled')
    update_time_entry.grid(row=0, column=4, sticky='w')

    def toggle_update_time(*args):
        if update_queue.get() == 1:
            update_time_entry.config(state='normal')
        else:
            update_time_entry.config(state='disabled')
    
    update_queue.trace_add('write', toggle_update_time)
    
    # -> Ship Date: "ALL", "NEVER", "SINCE", "LAST"
    ship_date_choice = tk.StringVar()
    ship_date_choice.set("LAST")
    ship_date_value = tk.IntVar()
    ship_date_value.set(7)

    ship_date_label = tk.Label(window, text="Last 7 Days",)
    ship_date_label.grid(row=1, column=5, sticky='w')

    tk.Label(window, text="Ship Date").grid(row=1, column=0, sticky='w')
    tk.Radiobutton(window, text="ALL", variable=ship_date_choice, value="ALL", command=lambda: update_label(previous, "ship", ship_date_label, "ALL", 0)).grid(row=1, column=1, sticky='w')
    tk.Radiobutton(window, text="NEVER", variable=ship_date_choice, value="NEVER", command=lambda: update_label(previous, "ship", ship_date_label, "NEVER", 0)).grid(row=1, column=2, sticky='w')
    tk.Radiobutton(window, text="SINCE", variable=ship_date_choice, value="SINCE", command=lambda: ask_date(previous, "ship", ship_date_choice, ship_date_value, ship_date_label)).grid(row=1, column=3, sticky='w')
    tk.Radiobutton(window, text="LAST", variable=ship_date_choice, value="LAST", command=lambda: ask_date(previous, "ship", ship_date_choice, ship_date_value, ship_date_label)).grid(row=1, column=4, sticky='w')

    # -> Receive Date: "ALL", "NEVER", "SINCE", "LAST"
    receive_date_choice = tk.StringVar()
    receive_date_choice.set("ALL")
    receive_date_value = tk.IntVar()
    receive_date_value.set(0)

    receive_date_label = tk.Label(window, text="")
    receive_date_label.grid(row=2, column=5, sticky='w')

    tk.Label(window, text="Receive Date").grid(row=2, column=0, sticky='w')
    tk.Radiobutton(window, text="ALL", variable=receive_date_choice, value="ALL", command=lambda: update_label(previous, "receive", receive_date_label, "ALL", 0)).grid(row=2, column=1, sticky='w')
    tk.Radiobutton(window, text="NEVER", variable=receive_date_choice, value="NEVER", command=lambda: update_label(previous, "receive", receive_date_label, "NEVER", 0)).grid(row=2, column=2, sticky='w')
    tk.Radiobutton(window, text="SINCE", variable=receive_date_choice, value="SINCE", command=lambda: ask_date(previous, "receive", receive_date_choice, receive_date_value, receive_date_label)).grid(row=2, column=3, sticky='w')
    tk.Radiobutton(window, text="LAST", variable=receive_date_choice, value="LAST", command=lambda: ask_date(previous, "receive", receive_date_choice, receive_date_value, receive_date_label)).grid(row=2, column=4, sticky='w')

    # Run button
    def run():
        config: Config = {
            "press_update": update_queue.get() == 1,
            "update_time": update_time.get(),
            "date_values": {
                "ship": {
                    "choice": ship_date_choice.get(),
                    "value": ship_date_value.get()
                },
                "receive": {
                    "choice": receive_date_choice.get(),
                    "value": receive_date_value.get()
                },
            },
            "rows": [],
            "current_row": 0
        }
        print(config)
        # Show real-time countdown and tell the user to take their hands off their mouse and keyboard
        show_countdown_window(config)
    
    tk.Button(window, text="Run", command=run, width=20).grid(row=4, column=0, columnspan=5, sticky="ew", padx=10)

    # Auto-size window based on content
    window.update_idletasks()
    window.geometry(f"{window.winfo_reqwidth() + 100}x{window.winfo_reqheight()}")  # Add extra width for labels

    root.mainloop()
    return root
