from typing import Optional, TypedDict

class DateInfo(TypedDict):
    choice: str
    value: int

class DateValues(TypedDict):
    ship: DateInfo
    receive: DateInfo

class OrderRow(TypedDict):
    order_number: str
    ship_date: str
    changed_to: Optional[str]

class Config(TypedDict):
    press_update: bool
    update_time: int
    date_values: DateValues
    rows: list[OrderRow]
    current_row: int