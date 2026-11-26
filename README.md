# CHRIST Smart Assignment & Deadline Management Dashboard

An interactive, local academic planner for CHRIST University students. This is an independent student project, not an official university service.

## Run the application

1. Install Python 3.10 or newer.
2. Extract the ZIP, open its `christ_dashboard` folder in VS Code, and open the terminal in that folder.
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start: `python -m streamlit run app.py`
5. Streamlit normally opens the app at http://localhost:8501.

## Features

- Overview: total, open, completed and overdue counts; live Indian date/time; completion rate; alerts; upcoming workload and urgent tasks.
- Manage assignments: add, edit, mark complete, delete with confirmation, search and filter by subject/status/priority.
- Analytics: status distribution, deadline workload, subject-wise stacked bar chart and completion percentages.
- Local persistence: changes are saved to `assignments.csv` in the current folder. The CSV is created after the first successful change. Keep a backup if needed.
- Examples: the first run has eight example assignments with deadlines relative to the current date. Use **Remove example assignments** to start with a blank list. An edited example becomes your own record and is no longer removed by this button.
- CSV export in the sidebar includes calculated deadline labels and days remaining.

## Deadline rules

- Completed: not counted in deadline warnings, regardless of deadline.
- Overdue: deadline is before today's date in India.
- Due today: deadline is today's date.
- Due soon: deadline is 1–7 days after today, inclusive.
- Upcoming: deadline is more than seven days away.

The dashboard updates immediately after changes. The sidebar clock refreshes every minute and refreshes the dashboard at a date change. Alerts are shown inside the app, not via email or notifications. The workload chart covers today and the next six days.

## Libraries used

- Streamlit: UI, forms, session state, controls
- Pandas: CSV storage, table operations, grouping and date calculations
- NumPy: deadline categories and numerical chart arrays
- Matplotlib: charts

No other libraries are imported in app.py. CSS is embedded in the UI for visual styling, and `.streamlit/config.toml` applies the navy/gold theme. The local CSV is designed for one student; a publicly hosted shared instance would need separate user accounts and per-user storage for privacy.
