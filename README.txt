# CSC484 Assignment 3 - Community Food Pantry Flow Tracker

## Program Description

The **Community Food Pantry Flow Tracker** is a Python desktop application designed to help a small food pantry record and review daily food movement.

The program tracks both food **donated to the pantry** and food **given out to the public** across five broad food categories:

- Canned Goods
- Meat
- Frozen Goods
- Refrigerated Goods
- Dry Goods

For each category, the user enters the number of items donated and the number of items distributed. The application then calculates daily totals, net movement, donation coverage, the highest-demand category, and a simple seven-day projection based on the current day's activity.

Two pie charts provide a visual statistical breakdown of:

- Percentage of total donations by food category
- Percentage of total items distributed by food category

The application also saves completed daily records to a CSV file for later review.

This project was created for **CSC484: Advanced Topics in Software Development with Python, Module 3** at Colorado State University Global.

---

## Purpose and Societal Impact

Food pantries need to understand both sides of inventory flow. Recording only incoming donations does not show how quickly food is being distributed to the community.

This application provides a simple way to compare incoming donations with outgoing food distribution. The information can help identify high-demand food categories and whether current donation levels are keeping pace with community needs.

The program is intended as an educational demonstration and not as a full production inventory-management system.

---

## Features

- Graphical user interface built with Tkinter
- Tracks donated and distributed quantities for five food categories
- Validates user input before calculations are performed
- Calculates:
  - Total items donated
  - Total items given to the public
  - Net daily movement
  - Highest-demand food category
  - Donation coverage percentage
- Produces a seven-day projection using the current day's activity
- Displays two pie charts showing:
  - Donation percentages by food category
  - Distribution percentages by food category
- Saves daily activity to `pantry_records.csv`
- Includes a Clear Form option for starting a new entry
- Demonstrates structured exception handling with `try`, `except`, and `finally`

---

## Exception Handling

A major purpose of this assignment is demonstrating Python exception-handling techniques.

The program uses `try`, `except`, and `finally` in three major functions.

### 1. Daily Calculation

The daily calculation validates all user entries.

The program handles situations such as:

- Blank fields
- Non-numeric entries
- Negative quantities
- Unexpected calculation errors

The `finally` block restores the Calculate button whether the calculation succeeds or fails.

### 2. Saving the Daily Record

The save routine writes the current daily results to a CSV file.

The program handles:

- Attempting to save before calculating daily totals
- File-system or permission errors
- Unexpected save errors

The `finally` block ensures the file handle is closed and the Save button is restored.

### 3. Seven-Day Projection

The projection routine requires a valid daily calculation before it can run.

The program handles:

- Attempting a projection before daily totals exist
- Invalid numeric program state
- Unexpected projection errors

The `finally` block restores the projection button regardless of the result.

---

## Food Categories

| Category | Examples |
| --- | --- |
| Canned Goods | Vegetables, soups, beans, fruits, canned meals |
| Meat | Beef, chicken, pork, fish, packaged meats |
| Frozen Goods | Frozen meals, vegetables, fruits, breads |
| Refrigerated Goods | Milk, eggs, cheese, yogurt, chilled foods |
| Dry Goods | Rice, pasta, cereal, flour, beans, boxed foods |

---

## Statistics

The program displays daily operational statistics and two pie charts.

### Daily Measurements

- Items Donated
- Items Given to Public
- Net Movement
- Highest Demand
- Donation Coverage

### Seven-Day Projection

The seven-day projection multiplies the current day's donation and distribution totals by seven.

This is a **projection**, not a prediction. It assumes the current day's activity continues at the same rate for seven days.

### Food-Type Pie Charts

The two pie charts show the percentage composition of the day's activity:

1. **Donations by Food Type**
2. **Items Given Out by Food Type**

If no items were donated or distributed, the application displays a message instead of attempting to graph an empty dataset.

---

## Requirements

- Python 3
- Tkinter
- Matplotlib

Tkinter is included with many standard Python installations, although some Linux distributions require it to be installed separately.

Matplotlib can be installed with:

```bash
pip install matplotlib
```

---

## Running the Program

1. Clone or download this repository.
2. Open a terminal or command prompt in the project folder.
3. Install Matplotlib if it is not already installed.
4. Run:

```bash
python pantry_tracker.py
```

Depending on the system, the command may instead be:

```bash
python3 pantry_tracker.py
```

---

## Using the Application

1. Enter the number of items **Donated** and **Given Out** for each food category.
2. Select **Calculate Daily Totals**.
3. Review the daily measurements and food-type pie charts.
4. Select **Calculate 7-Day Projection** to estimate one week of activity using the current day's values.
5. Select **Save Daily Record** to append the results to `pantry_records.csv`.
6. Select **Clear Form** to reset the interface.

Use `0` when no items were donated or distributed in a category.

---

## CSV Output

Saved records are written to:

```text
pantry_records.csv
```

The CSV contains:

- Date
- Donated quantity for each category
- Distributed quantity for each category
- Net movement for each category
- Total donated
- Total distributed
- Overall net movement
- Highest-demand category
- Highest-demand quantity
- Donation coverage

The file is created automatically when the first daily record is saved.

---

## Project Files

```text
CSC484-Assignment-3-Pantry-tracker/
├── pantry_tracker.py
├── README.md
└── pantry_records.csv   # Created when a daily record is saved
```

---

## Notes

- Quantities are entered as whole numbers.
- Negative quantities are rejected.
- Net movement represents the difference between food donated and food distributed during the current day. It is **not** the pantry's total on-hand inventory.
- The application does not track individual donors, recipients, or personally identifiable information.
- The program is intentionally scoped as a one-week academic Python project rather than a full inventory-management platform.

---

## Author

**Shawn T Storm**  
Colorado State University Global  
CSC484: Advanced Topics in Software Development with Python  
Module 3 Critical Thinking
