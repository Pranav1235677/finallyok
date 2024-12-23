import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Function to generate a simulated dataset
def generate_data(month):
    categories = [
        "Food", "Transportation", "Bills", "Groceries", "Entertainment", 
        "Healthcare", "Shopping", "Dining", "Travel", "Education",
        "Electricity", "Household Items", "Festive Expenses"
    ]
    
    payment_modes = ["Cash", "Online", "NetBanking", "Credit Card", "Debit Card", "Wallet"]
    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    data = []
    for _ in range(51):
        random_date = fake.date_between_dates(
            date_start=pd.Timestamp(year=2024, month=month_mapping[month], day=1),
            date_end=pd.Timestamp(year=2024, month=month_mapping[month], day=28)
        )
        data.append({
            "Date": random_date,
            "Category": random.choice(categories),
            "Payment_Mode": random.choice(payment_modes),
            "Description": random.choice([
                "Bought vegetables",
                "Paid electricity bill",
                "School fees payment",
                "Gas cylinder refill",
                "Groceries for home",
                "Milk and dairy items",
                "Medicine purchase",
                "Mobile recharge",
                "Monthly rent",
                "Dining at a restaurant",
                "Purchase of stationery",
                "House cleaning items",
                "Temple donation",
                "Shopping at local market",
                "Water bill payment",
                "Internet recharge",
                "Cable TV subscription",
                "New clothes purchase",
                "Repair work at home",
                "Train ticket booking",
                "Bus pass renewal",
                "Housemaid salary",
                "Fruit purchase",
                "Doctor consultation fee",
                "Car petrol refill",
                "Bike service expense",
                "Festival decorations",
                "Gift for a family member",
                "Newspaper subscription"
            ]),
            "Amount_Paid": round(random.uniform(10.0, 500.0), 2),
            "Cashback": round(random.uniform(0.0, 20.0), 2),
            "Month": month
        })
    return pd.DataFrame(data)

# Function to initialize the SQLite database with month-specific tables
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    for month in months:
        table_name = month.lower()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                Date TEXT,
                Category TEXT,
                Payment_Mode TEXT,
                Description TEXT,
                Amount_Paid REAL,
                Cashback REAL,
                Month TEXT
            )
        """)
    conn.commit()
    conn.close()

# Function to load data into the appropriate month table
def load_data_to_db(data, month):
    conn = sqlite3.connect('expenses.db')
    table_name = month.lower()
    data.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

# Function to query data from a specific month table
def query_data_from_table(table=None):
    conn = sqlite3.connect('expenses.db')
    if table:
        result = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY Date ASC", conn)
    else:
        # Combine data from all tables
        months = ["january", "february", "march", "april", "may", "june", 
                  "july", "august", "september", "october", "november", "december"]
        result = pd.concat([pd.read_sql_query(f"SELECT * FROM {month}", conn) for month in months], ignore_index=True)
    conn.close()
    return result

# Initialize the database
init_db()

# Apply custom CSS for styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #eaf4fc;
        }
        h1, h2, h3 {
            color: #6c63ff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_custom_css()

# Main Streamlit app
st.title("Personal Expense Tracker")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose an option",
    ["Generate Data", "View Data", "Visualize Insights", "Run SQL Query", "Run Predefined SQL Queries"]
)

if option == "Generate Data":
    st.subheader("Generate Expense Data")
    month = st.text_input("Enter the month (e.g., January):", "January")
    if st.button("Generate"):
        try:
            data = generate_data(month)
            load_data_to_db(data, month)
            st.success(f"Data for {month} generated and loaded into the database!")
            st.dataframe(data.head())
        except KeyError:
            st.error("Invalid month entered. Please ensure the month is spelled correctly.")

elif option == "View Data":
    st.subheader("View Expense Data")
    scope = st.selectbox("View scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month to view data (e.g., January):", "January")
        if st.button("View"):
            try:
                table = month.lower()
                data = query_data_from_table(table)
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("View All"):
            try:
                data = query_data_from_table()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Visualize Insights":
    st.subheader("Spending Insights")
    scope = st.selectbox("Visualize scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month to visualize data (e.g., January):", "January")
        if st.button("Visualize"):
            try:
                table = month.lower()
                query = f"SELECT Category, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Category"
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                st.bar_chart(data.set_index("Category"))
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("Visualize All"):
            try:
                data = query_data_from_table()
                insights = data.groupby("Category")["Amount_Paid"].sum().reset_index()
                st.bar_chart(insights.set_index("Category"))
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Run SQL Query":
    st.subheader("Run Custom SQL Query")
    scope = st.selectbox("Query scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month for the query (e.g., January):", "January")
        query = st.text_area("Enter your SQL query:")
        if st.button("Execute"):
            try:
                table = month.lower()
                query = query.replace("{table}", table)
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        query = st.text_area("Enter your SQL query for all months:")
        if st.button("Execute All"):
            try:
                data = query_data_from_table()
                conn = sqlite3.connect('expenses.db')
                data.to_sql("expenses_union", conn, if_exists="replace", index=False)
                result = pd.read_sql_query(query.replace("{table}", "expenses_union"), conn)
                conn.close()
                st.dataframe(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Run Predefined SQL Queries":
    st.subheader("Run Predefined SQL Queries")
    scope = st.selectbox("Query scope", ["Specific Month", "All Months"])
    queries = {
        "Total Spending by Category": "SELECT Category, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Category",
        "Top 5 Highest Spending Transactions": "SELECT * FROM {table} ORDER BY Amount_Paid DESC LIMIT 5",
        "Total Cashback Earned": "SELECT SUM(Cashback) as Total_Cashback FROM {table}",
    }
    query_name = st.selectbox("Choose a predefined query", list(queries.keys()))
    if scope == "Specific Month":
        month = st.text_input("Enter the month for the query (e.g., January):", "January")
        if st.button("Run Query"):
            try:
                table = month.lower()
                query = queries[query_name].format(table=table)
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("Run Query for All Months"):
            try:
                data = query_data_from_table()
                conn = sqlite3.connect('expenses.db')
                data.to_sql("expenses_union", conn, if_exists="replace", index=False)
                query = queries[query_name].replace("{table}", "expenses_union")
                result = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
