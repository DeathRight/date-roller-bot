# Eclipse TRQ Date Roller Bot

## Purpose

The Eclipse Transfer Register Queue Date Roller Bot is a specialized automation tool designed to streamline the process of updating ship and receive dates for transfer orders in the Eclipse ERP system. This bot is tailored for a specific company's workflow, addressing the need for efficient batch processing of order dates based on predefined criteria.

## How It Works

The bot interacts with the Eclipse ERP system through GUI automation, simulating user actions to navigate through the Transfer Register Queue and Transfer Order Entry windows. Here's a high-level overview of its operation:

1. **Configuration**: The user sets parameters for date rolling through a graphical interface, including update preferences and date criteria.
2. **Queue Processing**: The bot scans the Transfer Register Queue, identifying orders that meet the specified date criteria.
3. **Order Updates**: For qualifying orders, the bot opens the Transfer Order Entry window and updates the ship or receive dates as needed.
4. **Batch Processing**: The bot continues this process for all orders in the queue, ensuring efficient bulk updates.

## Features

- **Graphical User Interface**: Easy-to-use interface for setting update parameters and initiating the bot.
- **Flexible Date Criteria**: Supports various date selection options including "ALL", "NEVER", "SINCE", and "LAST X DAYS" for both ship and receive dates.
- **Queue Update Option**: Ability to trigger a queue update before processing, with a customizable wait time.
- **Automated Navigation**: Intelligently navigates through different windows and tabs in the Eclipse system.
- **Progress Tracking**: Keeps track of processed orders and displays progress information.
- **Error Handling**: Implements checks and corrections to ensure accurate navigation and data entry.

## Edge Cases Covered

The bot is designed to handle various edge cases that may occur during the automation process:

- **Window Management**: Automatically resizes and positions relevant windows to ensure consistent interaction points.
- **Column Navigation**: Implements checks to ensure it's always in the correct column when reading or updating dates.
- **Data Validation**: Verifies copied data to ensure it's in the expected format before processing.
- **Popup Handling**: Anticipates and dismisses potential popup windows that may interrupt the workflow.
- **Interruption Recovery**: Able to re-orient itself within the queue if the process is interrupted or loses its place.
- **User Interrupt**: Allows for graceful termination of the process if the user presses the escape key.

## Technical Details

- **Language**: Python
- **Key Libraries**:
  - `pyautogui`: For simulating mouse and keyboard inputs
  - `keyboard`: For detecting key presses (e.g., escape key for interruption)
  - `pyperclip`: For clipboard operations
  - `pygetwindow`: For window management
  - `tkinter`: For the graphical user interface
  - `tkcalendar`: For date picker functionality in the GUI

## Limitations and Considerations

- This bot is highly specialized for a specific Eclipse ERP setup and may require adjustments for different environments or Eclipse versions.
- It relies on consistent window layouts and element positions, so any changes to the Eclipse UI may require updates to the bot's navigation logic.
- The bot should be used with caution and ideally in a test environment before applying changes to live data.
