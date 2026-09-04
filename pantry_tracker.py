"""
Community Food Pantry Flow Tracker
CSC484 - Module 3 Critical Thinking

A small Tkinter application that records daily food donations and
community distribution by broad food category, saves daily activity to CSV,
and estimates a seven-day flow based on the current day's measurements.

The program intentionally demonstrates try, except, and finally in three
major application functions:
1. Daily input validation and calculation
2. Saving a daily record to a CSV file
3. Seven-day projection calculation
"""

import csv
import os
from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


APP_TITLE = "Community Food Pantry Flow Tracker"
DATA_FILE = "pantry_records.csv"

FOOD_CATEGORIES = {
    "Canned Goods": "Vegetables, soups, beans, fruits, and canned meals",
    "Meat": "Beef, chicken, pork, fish, and packaged meats",
    "Frozen Goods": "Frozen meals, vegetables, fruits, and breads",
    "Refrigerated Goods": "Milk, eggs, cheese, yogurt, and chilled foods",
    "Dry Goods": "Rice, pasta, cereal, flour, beans, and boxed foods",
}


class PantryTrackerApp:
    """Main graphical application for daily pantry flow tracking."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x1060")
        self.root.minsize(1000, 900)

        self.entries = {}
        self.daily_results = None
        self.weekly_results = None

        self.status_var = tk.StringVar(value="Enter today's pantry activity to begin.")
        self.daily_donated_var = tk.StringVar(value="0")
        self.daily_given_var = tk.StringVar(value="0")
        self.daily_net_var = tk.StringVar(value="0")
        self.highest_demand_var = tk.StringVar(value="Not calculated")
        self.coverage_var = tk.StringVar(value="Not calculated")

        self.weekly_donated_var = tk.StringVar(value="0")
        self.weekly_given_var = tk.StringVar(value="0")
        self.weekly_net_var = tk.StringVar(value="0")

        self.donation_chart_figure = None
        self.distribution_chart_figure = None
        self.donation_chart_axis = None
        self.distribution_chart_axis = None
        self.donation_chart_canvas = None
        self.distribution_chart_canvas = None

        self._configure_styles()
        self._build_interface()

    # ------------------------------------------------------------------
    # USER INTERFACE
    # ------------------------------------------------------------------
    def _configure_styles(self):
        """Create a small, readable ttk style set for the application."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Category.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Description.TLabel", font=("Segoe UI", 9))
        style.configure("Metric.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("MetricValue.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))

    def _build_interface(self):
        """Build all visible widgets."""
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text=(
                "Track food received and distributed today, then estimate "
                "a seven-day flow from the current day's activity."
            ),
            style="Subtitle.TLabel",
            wraplength=760,
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        ttk.Label(
            header,
            text=f"Activity Date: {date.today().strftime('%B %d, %Y')}",
            style="Metric.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(16, 0))

        input_frame = ttk.LabelFrame(
            outer,
            text="Daily Food Movement",
            padding=12,
            style="Section.TLabelframe",
        )
        input_frame.grid(row=1, column=0, sticky="nsew")
        input_frame.columnconfigure(0, weight=3)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        ttk.Label(input_frame, text="Food Category", style="Metric.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 8)
        )
        ttk.Label(input_frame, text="Donated", style="Metric.TLabel").grid(
            row=0, column=1, pady=(0, 8)
        )
        ttk.Label(input_frame, text="Given Out", style="Metric.TLabel").grid(
            row=0, column=2, pady=(0, 8)
        )

        for row_index, (category, description) in enumerate(
            FOOD_CATEGORIES.items(), start=1
        ):
            info = ttk.Frame(input_frame)
            info.grid(
                row=row_index,
                column=0,
                sticky="ew",
                padx=(0, 14),
                pady=6,
            )
            ttk.Label(info, text=category, style="Category.TLabel").pack(
                anchor="w"
            )
            ttk.Label(
                info,
                text=description,
                style="Description.TLabel",
                wraplength=460,
            ).pack(anchor="w")

            donated_entry = ttk.Entry(input_frame, width=12, justify="center")
            donated_entry.grid(row=row_index, column=1, padx=8, pady=6)
            donated_entry.insert(0, "0")

            given_entry = ttk.Entry(input_frame, width=12, justify="center")
            given_entry.grid(row=row_index, column=2, padx=8, pady=6)
            given_entry.insert(0, "0")

            self.entries[category] = {
                "donated": donated_entry,
                "given": given_entry,
            }

        button_frame = ttk.Frame(outer)
        button_frame.grid(row=2, column=0, sticky="ew", pady=12)
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.calculate_button = ttk.Button(
            button_frame,
            text="Calculate Daily Totals",
            command=self.calculate_daily_totals,
        )
        self.calculate_button.grid(row=0, column=0, padx=4, sticky="ew")

        self.save_button = ttk.Button(
            button_frame,
            text="Save Daily Record",
            command=self.save_daily_record,
        )
        self.save_button.grid(row=0, column=1, padx=4, sticky="ew")

        self.estimate_button = ttk.Button(
            button_frame,
            text="Calculate 7-Day Projection",
            command=self.calculate_weekly_estimate,
        )
        self.estimate_button.grid(row=0, column=2, padx=4, sticky="ew")

        ttk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form,
        ).grid(row=0, column=3, padx=4, sticky="ew")

        results_frame = ttk.Frame(outer)
        results_frame.grid(row=3, column=0, sticky="nsew")
        results_frame.columnconfigure((0, 1), weight=1)

        daily_frame = ttk.LabelFrame(
            results_frame,
            text="Today's Measurements",
            padding=12,
            style="Section.TLabelframe",
        )
        daily_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._metric_row(daily_frame, 0, "Items Donated", self.daily_donated_var)
        self._metric_row(daily_frame, 1, "Items Given to Public", self.daily_given_var)
        self._metric_row(daily_frame, 2, "Net Movement", self.daily_net_var)
        self._metric_row(daily_frame, 3, "Highest Demand", self.highest_demand_var)
        self._metric_row(daily_frame, 4, "Donation Coverage", self.coverage_var)

        weekly_frame = ttk.LabelFrame(
            results_frame,
            text="Projected 7-Day Activity",
            padding=12,
            style="Section.TLabelframe",
        )
        weekly_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self._metric_row(
            weekly_frame, 0, "Projected Donations", self.weekly_donated_var
        )
        self._metric_row(
            weekly_frame, 1, "Projected Distribution", self.weekly_given_var
        )
        self._metric_row(weekly_frame, 2, "Projected Net", self.weekly_net_var)

        ttk.Label(
            weekly_frame,
            text=(
                "Projection assumes today's donation and distribution levels "
                "continue at the same rate for seven days."
            ),
            style="Description.TLabel",
            wraplength=330,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))

        statistics_frame = ttk.LabelFrame(
            outer,
            text="Food Type Statistics",
            padding=10,
            style="Section.TLabelframe",
        )
        statistics_frame.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        statistics_frame.columnconfigure((0, 1), weight=1)

        donation_chart_frame = ttk.Frame(statistics_frame)
        donation_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        distribution_chart_frame = ttk.Frame(statistics_frame)
        distribution_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.donation_chart_figure = Figure(figsize=(4.7, 2.15), dpi=100)
        self.donation_chart_axis = self.donation_chart_figure.add_subplot(111)
        self.donation_chart_canvas = FigureCanvasTkAgg(
            self.donation_chart_figure, master=donation_chart_frame
        )
        self.donation_chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.distribution_chart_figure = Figure(figsize=(4.7, 2.15), dpi=100)
        self.distribution_chart_axis = self.distribution_chart_figure.add_subplot(111)
        self.distribution_chart_canvas = FigureCanvasTkAgg(
            self.distribution_chart_figure, master=distribution_chart_frame
        )
        self.distribution_chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        self._draw_empty_chart(
            self.donation_chart_axis,
            self.donation_chart_canvas,
            "Donations by Food Type",
            "Calculate daily totals to display donation percentages.",
        )
        self._draw_empty_chart(
            self.distribution_chart_axis,
            self.distribution_chart_canvas,
            "Items Given Out by Food Type",
            "Calculate daily totals to display distribution percentages.",
        )

        status_frame = ttk.Frame(outer)
        status_frame.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        status_frame.columnconfigure(0, weight=1)
        ttk.Separator(status_frame).grid(row=0, column=0, sticky="ew", pady=(0, 7))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=1040,
        ).grid(row=1, column=0, sticky="w")

    @staticmethod
    def _metric_row(parent, row, label_text, value_variable):
        """Create one label/value pair inside a results panel."""
        ttk.Label(parent, text=label_text, style="Metric.TLabel").grid(
            row=row, column=0, sticky="w", pady=5
        )
        ttk.Label(parent, textvariable=value_variable, style="MetricValue.TLabel").grid(
            row=row, column=1, sticky="e", padx=(18, 0), pady=5
        )
        parent.columnconfigure(0, weight=1)

    @staticmethod
    def _draw_empty_chart(axis, canvas, title, message):
        """Display a readable placeholder when a pie chart has no data yet."""
        axis.clear()
        axis.set_title(title, fontsize=11, fontweight="bold")
        axis.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            wrap=True,
            fontsize=9,
            transform=axis.transAxes,
        )
        axis.axis("off")
        axis.figure.tight_layout()
        canvas.draw_idle()

    @staticmethod
    def _draw_percentage_pie(axis, canvas, title, values, empty_message):
        """Draw one percentage pie chart for the five pantry food categories."""
        axis.clear()
        total = sum(values)

        if total == 0:
            PantryTrackerApp._draw_empty_chart(axis, canvas, title, empty_message)
            return

        labels = list(FOOD_CATEGORIES.keys())
        wedges, _, _ = axis.pie(
            values,
            startangle=90,
            autopct=lambda percent: f"{percent:.1f}%" if percent > 0 else "",
            pctdistance=0.72,
            textprops={"fontsize": 8},
        )
        axis.set_title(title, fontsize=11, fontweight="bold")
        axis.legend(
            wedges,
            labels,
            loc="center left",
            bbox_to_anchor=(0.93, 0.5),
            fontsize=7.5,
            frameon=False,
        )
        axis.axis("equal")
        axis.figure.tight_layout()
        canvas.draw_idle()

    def _update_statistics_charts(self, category_results):
        """Refresh donation and distribution percentage charts from daily data."""
        donated_values = [
            category_results[category]["donated"] for category in FOOD_CATEGORIES
        ]
        given_values = [
            category_results[category]["given"] for category in FOOD_CATEGORIES
        ]

        self._draw_percentage_pie(
            self.donation_chart_axis,
            self.donation_chart_canvas,
            "Donations by Food Type",
            donated_values,
            "No donated items were recorded today.",
        )
        self._draw_percentage_pie(
            self.distribution_chart_axis,
            self.distribution_chart_canvas,
            "Items Given Out by Food Type",
            given_values,
            "No distributed items were recorded today.",
        )

    def _reset_statistics_charts(self):
        """Return both statistics charts to their pre-calculation state."""
        self._draw_empty_chart(
            self.donation_chart_axis,
            self.donation_chart_canvas,
            "Donations by Food Type",
            "Calculate daily totals to display donation percentages.",
        )
        self._draw_empty_chart(
            self.distribution_chart_axis,
            self.distribution_chart_canvas,
            "Items Given Out by Food Type",
            "Calculate daily totals to display distribution percentages.",
        )

    # ------------------------------------------------------------------
    # MAJOR FUNCTION 1: DAILY CALCULATION
    # ------------------------------------------------------------------
    def calculate_daily_totals(self):
        """
        Read and validate all food movement entries, then calculate daily stats.

        This function demonstrates try/except/finally for user-input handling.
        The finally block restores the Calculate button regardless of success.
        """
        self.calculate_button.config(state="disabled")
        self.status_var.set("Calculating today's pantry activity...")

        try:
            category_results = {}

            for category, widgets in self.entries.items():
                donated_text = widgets["donated"].get().strip()
                given_text = widgets["given"].get().strip()

                if donated_text == "" or given_text == "":
                    raise ValueError(
                        f"Both Donated and Given Out are required for {category}."
                    )

                donated = int(donated_text)
                given = int(given_text)

                if donated < 0 or given < 0:
                    raise ValueError(
                        f"{category} values cannot be negative. Use zero when no items moved."
                    )

                category_results[category] = {
                    "donated": donated,
                    "given": given,
                    "net": donated - given,
                }

            total_donated = sum(
                result["donated"] for result in category_results.values()
            )
            total_given = sum(
                result["given"] for result in category_results.values()
            )
            net_movement = total_donated - total_given

            highest_demand_category = max(
                category_results,
                key=lambda name: category_results[name]["given"],
            )
            highest_demand_value = category_results[highest_demand_category]["given"]

            if total_given == 0:
                if total_donated == 0:
                    coverage_text = "No movement today"
                else:
                    coverage_text = "No distribution today"
            else:
                coverage_percent = (total_donated / total_given) * 100
                coverage_text = f"{coverage_percent:.1f}%"

            self.daily_results = {
                "date": date.today().isoformat(),
                "categories": category_results,
                "total_donated": total_donated,
                "total_given": total_given,
                "net_movement": net_movement,
                "highest_demand_category": highest_demand_category,
                "highest_demand_value": highest_demand_value,
                "coverage_text": coverage_text,
            }

            # A new daily calculation invalidates any older weekly projection.
            self.weekly_results = None
            self.weekly_donated_var.set("0")
            self.weekly_given_var.set("0")
            self.weekly_net_var.set("0")

            self.daily_donated_var.set(str(total_donated))
            self.daily_given_var.set(str(total_given))
            self.daily_net_var.set(self._format_signed(net_movement))
            self.highest_demand_var.set(
                f"{highest_demand_category} ({highest_demand_value})"
            )
            self.coverage_var.set(coverage_text)
            self._update_statistics_charts(category_results)

            self.status_var.set(
                "Daily totals calculated successfully. You can now save the record "
                "or calculate the seven-day projection."
            )

        except ValueError as error:
            self.daily_results = None
            self.weekly_results = None
            self._reset_statistics_charts()
            self.status_var.set(f"Daily calculation stopped: {error}")
            messagebox.showerror("Invalid Pantry Entry", str(error))

        except Exception as error:
            self.daily_results = None
            self.weekly_results = None
            self._reset_statistics_charts()
            self.status_var.set("An unexpected error stopped the daily calculation.")
            messagebox.showerror(
                "Unexpected Error",
                f"The daily calculation could not be completed.\n\nDetails: {error}",
            )

        finally:
            # This always runs, even when one of the exceptions above occurs.
            self.calculate_button.config(state="normal")

    # ------------------------------------------------------------------
    # MAJOR FUNCTION 2: SAVE DAILY RECORD
    # ------------------------------------------------------------------
    def save_daily_record(self):
        """
        Save the most recently calculated daily result to a CSV file.

        This function demonstrates try/except/finally for file-resource handling.
        The file is explicitly closed in finally whether the write succeeds or fails.
        """
        self.save_button.config(state="disabled")
        file_handle = None

        try:
            if self.daily_results is None:
                raise ValueError(
                    "Calculate today's totals before attempting to save the record."
                )

            file_exists = os.path.exists(DATA_FILE)
            file_handle = open(DATA_FILE, "a", newline="", encoding="utf-8")
            writer = csv.writer(file_handle)

            if not file_exists or os.path.getsize(DATA_FILE) == 0:
                writer.writerow(self._csv_header())

            writer.writerow(self._csv_row())

            self.status_var.set(
                f"Daily record saved successfully to {DATA_FILE}."
            )
            messagebox.showinfo(
                "Record Saved",
                f"Today's pantry activity was saved to {DATA_FILE}.",
            )

        except ValueError as error:
            self.status_var.set(f"Save stopped: {error}")
            messagebox.showwarning("Nothing to Save", str(error))

        except OSError as error:
            self.status_var.set("The daily record could not be written to disk.")
            messagebox.showerror(
                "File Error",
                f"The pantry record could not be saved.\n\nDetails: {error}",
            )

        except Exception as error:
            self.status_var.set("An unexpected error occurred while saving the record.")
            messagebox.showerror(
                "Unexpected Save Error",
                f"The record could not be saved.\n\nDetails: {error}",
            )

        finally:
            # This is the resource-cleanup behavior emphasized in this module.
            if file_handle is not None and not file_handle.closed:
                file_handle.close()
            self.save_button.config(state="normal")

    # ------------------------------------------------------------------
    # MAJOR FUNCTION 3: SEVEN-DAY ESTIMATE
    # ------------------------------------------------------------------
    def calculate_weekly_estimate(self):
        """
        Project seven days of activity from the most recent daily totals.

        This function demonstrates try/except/finally for application-state handling.
        A projection cannot be created until a valid daily calculation exists.
        """
        self.estimate_button.config(state="disabled")
        self.status_var.set("Calculating seven-day projection...")

        try:
            if self.daily_results is None:
                raise ValueError(
                    "A valid daily calculation is required before creating a projection."
                )

            daily_donated = self.daily_results["total_donated"]
            daily_given = self.daily_results["total_given"]

            if not isinstance(daily_donated, int) or not isinstance(daily_given, int):
                raise TypeError("Daily totals are not in the expected numeric format.")

            if daily_donated < 0 or daily_given < 0:
                raise ValueError("Daily totals cannot contain negative quantities.")

            weekly_donated = daily_donated * 7
            weekly_given = daily_given * 7
            weekly_net = weekly_donated - weekly_given

            self.weekly_results = {
                "weekly_donated": weekly_donated,
                "weekly_given": weekly_given,
                "weekly_net": weekly_net,
            }

            self.weekly_donated_var.set(str(weekly_donated))
            self.weekly_given_var.set(str(weekly_given))
            self.weekly_net_var.set(self._format_signed(weekly_net))

            self.status_var.set(
                "Seven-day projection calculated successfully using today's activity."
            )

        except (ValueError, TypeError) as error:
            self.weekly_results = None
            self.status_var.set(f"Projection stopped: {error}")
            messagebox.showwarning("Projection Unavailable", str(error))

        except Exception as error:
            self.weekly_results = None
            self.status_var.set("An unexpected error stopped the weekly projection.")
            messagebox.showerror(
                "Unexpected Projection Error",
                f"The projection could not be completed.\n\nDetails: {error}",
            )

        finally:
            # The UI returns to an usable state regardless of calculation outcome.
            self.estimate_button.config(state="normal")

    # ------------------------------------------------------------------
    # SUPPORTING FUNCTIONS
    # ------------------------------------------------------------------
    def clear_form(self):
        """Reset all user input and calculated output."""
        for widgets in self.entries.values():
            for key in ("donated", "given"):
                entry = widgets[key]
                entry.delete(0, tk.END)
                entry.insert(0, "0")

        self.daily_results = None
        self.weekly_results = None

        self.daily_donated_var.set("0")
        self.daily_given_var.set("0")
        self.daily_net_var.set("0")
        self.highest_demand_var.set("Not calculated")
        self.coverage_var.set("Not calculated")

        self.weekly_donated_var.set("0")
        self.weekly_given_var.set("0")
        self.weekly_net_var.set("0")

        self._reset_statistics_charts()

        self.status_var.set("Form cleared. Enter today's pantry activity to begin.")

    def _csv_header(self):
        """Return CSV column headings."""
        header = ["date"]
        for category in FOOD_CATEGORIES:
            safe_name = category.lower().replace(" ", "_")
            header.extend(
                [
                    f"{safe_name}_donated",
                    f"{safe_name}_given",
                    f"{safe_name}_net",
                ]
            )

        header.extend(
            [
                "total_donated",
                "total_given",
                "net_movement",
                "highest_demand_category",
                "highest_demand_quantity",
                "donation_coverage",
            ]
        )
        return header

    def _csv_row(self):
        """Return the current daily result as one CSV row."""
        row = [self.daily_results["date"]]

        for category in FOOD_CATEGORIES:
            category_result = self.daily_results["categories"][category]
            row.extend(
                [
                    category_result["donated"],
                    category_result["given"],
                    category_result["net"],
                ]
            )

        row.extend(
            [
                self.daily_results["total_donated"],
                self.daily_results["total_given"],
                self.daily_results["net_movement"],
                self.daily_results["highest_demand_category"],
                self.daily_results["highest_demand_value"],
                self.daily_results["coverage_text"],
            ]
        )
        return row

    @staticmethod
    def _format_signed(number):
        """Display positive values with a leading plus sign."""
        if number > 0:
            return f"+{number}"
        return str(number)


def main():
    """Create and start the Tkinter application."""
    root = tk.Tk()
    PantryTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
