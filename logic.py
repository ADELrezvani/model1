import re
import sqlite3
from calendar import monthrange
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).with_name("bmi.db")

NAME_RE = re.compile(r"^[A-Z][a-z]*$")
HEIGHT_RE = re.compile(r"^\d+$")
WEIGHT_RE = re.compile(r"^\d+(\.\d+)?$")


def validate(name, height, weight):
    errors = []
    if not NAME_RE.match(name):
        errors.append("Name must contain only letters, and only the first letter must be uppercase (e.g. Ali).")
    if not HEIGHT_RE.match(height) or int(height) == 0:
        errors.append("Height must be a positive integer in cm (e.g. 175).")
    if not WEIGHT_RE.match(weight) or float(weight) == 0:
        errors.append("Weight must be a positive decimal number in kg (e.g. 70.5).")
    return errors


def calc_bmi(height_cm, weight_kg):
    h = height_cm / 100
    return weight_kg / (h * h)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_age(birth, today=None):
    today = today or date.today()
    if birth > today:
        raise ValueError("Birth date cannot be in the future")

    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day

    y, m = today.year, today.month
    while days < 0:
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        days += monthrange(y, m)[1]
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months, days


def init_db(path=DB_PATH):
    with sqlite3.connect(path) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS records (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   height INTEGER NOT NULL,
                   weight REAL NOT NULL,
                   bmi REAL NOT NULL,
                   created_at TEXT DEFAULT CURRENT_TIMESTAMP
               )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS ages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   birth_date TEXT NOT NULL,
                   years INTEGER NOT NULL,
                   months INTEGER NOT NULL,
                   days INTEGER NOT NULL,
                   created_at TEXT DEFAULT CURRENT_TIMESTAMP
               )"""
        )


def save_record(name, height, weight, bmi, path=DB_PATH):
    init_db(path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO records (name, height, weight, bmi) VALUES (?, ?, ?, ?)",
            (name, height, weight, bmi),
        )


def save_age(birth, years, months, days, path=DB_PATH):
    init_db(path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO ages (birth_date, years, months, days) VALUES (?, ?, ?, ?)",
            (birth.isoformat(), years, months, days),
        )
