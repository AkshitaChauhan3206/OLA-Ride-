# Ola Ride Insights

Analysis of one month of Ola ride bookings (July 2024, 103,024 rows). The project cleans the data,
answers the project questions with SQL, explores the data in a notebook and shows the results in an
interactive Streamlit dashboard.

- **Live demo:** https://YOUR_APP_NAME.streamlit.app
- **GitHub:** https://github.com/YOUR_USERNAME/ola-ride-insights

## Project description

Ola generates a lot of booking data. This project looks at that data to find out how many bookings are
completed, why the rest fail, how customers pay, which vehicle types earn more and how drivers and
customers rate each other. The dashboard has nine tabs: Overview, Vehicles, Revenue, Cancellations,
Ratings, Data Health, Insights, SQL Lab and Power BI. The sidebar filters the data by date, vehicle type,
booking status, payment method and pickup location.

### Main findings

- Only 62.1% of bookings are completed. Failed bookings carry about Rs 2.15 Cr of booking value, against Rs 3.51 Cr earned.
- Drivers cancel 1.8 times more than customers (17.9% against 10.2%).
- About 70% of customer cancellations are caused by the service, for example the driver not moving to the pickup point.
- Price does not depend on distance (correlation 0.002).
- There is no clear peak hour, and failures are similar in every hour, area and vehicle type.
- Cash is 54.9% of revenue and UPI is 40.4%.
- 6.1% of completed rides are marked incomplete.
- 91.6% of customers booked only once.

The detailed report is in `report/Ola_Ride_Insights_Report.pdf`.

## Tools used

Python, Pandas, NumPy, SciPy, Matplotlib, Seaborn, Plotly, Streamlit, SQL (MySQL and SQLite), Power BI.

## Project structure

```
ola_ride_insights/
├── app.py                  Streamlit dashboard
├── requirements.txt        Packages needed
├── .streamlit/config.toml  Dashboard theme
├── data/ola_cleaned.csv    Cleaned data
├── sql/ola_queries.sql     15 SQL queries
├── notebooks/              EDA notebook
├── report/                 Insights report (PDF)
└── src/                    Code used by the dashboard
    ├── config.py           Paths, colours and project links
    ├── cleaning.py         Raw Excel file to cleaned CSV
    ├── features.py         Extra columns
    ├── data_loader.py      Loads the data
    ├── metrics.py          Business numbers
    ├── charts.py           Plotly charts
    ├── styles.py           Dashboard design
    ├── insights.py         Findings and recommendations
    └── sql_lab.py          Runs SQL queries inside the app
```

## Run locally in VS Code

1. Install Python 3.10 or higher and install VS Code with the Python extension.
2. Open VS Code, choose **File > Open Folder** and select the `ola_ride_insights` folder.
3. Open the terminal in VS Code (**Terminal > New Terminal**).
4. Create a virtual environment:
   ```
   python -m venv venv
   ```
5. Activate it.
   - Windows: `venv\Scripts\activate`
   - Mac or Linux: `source venv/bin/activate`
6. Install the packages:
   ```
   pip install -r requirements.txt
   ```
7. Start the dashboard:
   ```
   streamlit run app.py
   ```
8. The browser opens at `http://localhost:8501`. If it does not open, copy this address into the browser.

To open the EDA notebook, install the Jupyter extension in VS Code and open
`notebooks/Ola_Ride_Insights_EDA.ipynb`.

To rebuild the cleaned file from the original Excel file:
```
python -m src.cleaning path/to/OLA_DataSet.xlsx
```

## SQL queries

The queries are in `sql/ola_queries.sql` and work in MySQL and SQLite. Load `data/ola_cleaned.csv` into a
table named `ola_bookings`. Questions 1 to 10 are from the project brief and questions 11 to 15 are extra.
The SQL Lab tab in the dashboard runs them directly.

## Deploy on Streamlit Community Cloud

1. Upload this folder to a public GitHub repository.
2. Go to share.streamlit.io and click **New app**.
3. Select the repository, the branch `main` and the main file `app.py`, then click **Deploy**.
4. Copy the live link into this README and into `src/config.py`.

To show a Power BI report in the Power BI tab, publish the report, copy its embed link and paste it into
`POWERBI_EMBED_URL` in `src/config.py`.

## Notes about the data

- Blank cells are not errors. A cancelled ride has no payment, rating, distance or turnaround time, so the blanks were not filled.
- Average distance and ratings are calculated for completed rides only.
- Revenue means the booking value of bookings with status Success. Incomplete rides are inside it and are shown separately.
- The units of V_TAT and C_TAT are not given in the data. They look like seconds.
- Most patterns in the data are very even, so it may be sample data. The findings should be confirmed on live data.
