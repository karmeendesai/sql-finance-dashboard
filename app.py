import streamlit as st
import plotly.express as px
import pandas as pd
from queries import all_transactions

# page set up
st.set_page_config(
    page_title="Personal Finance Dashboard",
    layout="wide"
)

# title and sub-header
st.title("SQL-Powered Personal Finance Dashboard")
st.write("This dashboard uses SQL queries on a SQLite database to analyze spending patterns.")

# load data
transactions_df = all_transactions()
transactions_df["transaction_date"] = pd.to_datetime(transactions_df["transaction_date"])

# sidebar filter
st.sidebar.header("Filters")

# reset button
if st.sidebar.button("Reset Filters"):
    st.session_state.selected_categories = sorted(transactions_df["category_name"].unique())
    st.session_state.selected_types = sorted(transactions_df["transaction_type"].unique())

# category filter
categories = sorted(transactions_df["category_name"].unique())

# sets default selected values = ALL categories
if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = categories

# fetches all unique category names and creates a multi-select dropdown
selected_categories = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=st.session_state.selected_categories,
    key="category_filter"
)

# save user category selection
st.session_state.selected_categories = selected_categories

# transaction type filter
transaction_types = sorted(transactions_df["transaction_type"].unique())

# sets default values = ALL types
if "selected_types" not in st.session_state:
    st.session_state.selected_types = transaction_types

# fetches all unique transaction types and creates a multi-select dropdown
selected_types = st.sidebar.multiselect(
    "Transaction Type",
    options=transaction_types,
    default=st.session_state.selected_types,
    key="type_filter"
)

# save user transaction selection
st.session_state.selected_types = selected_types

# finds date range
min_date = transactions_df["transaction_date"].min()
max_date = transactions_df["transaction_date"].max()

# creates date range selector in sidebar
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# creates a copy of the full transaction table
filtered_df = transactions_df.copy()

# keeps only transaction between user selected start and end date
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["transaction_date"] >= pd.to_datetime(start_date)) &
        (filtered_df["transaction_date"] <= pd.to_datetime(end_date))
    ]

# only keeps rows where category is one of the selected categories
# only keeps rows where transaction type is one of the selected types
filtered_df = filtered_df[
    filtered_df["category_name"].isin(selected_categories) &
    filtered_df["transaction_type"].isin(selected_types)
]

# split income and expenses
expense_df = filtered_df[filtered_df["transaction_type"] == "Expense"]
income_df = filtered_df[filtered_df["transaction_type"] == "Income"]

# calculates main metrics
total_expenses = expense_df["amount"].sum()
total_income = income_df["amount"].sum()
net_savings = total_income - total_expenses
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

# financial overview title (adds section heading)
st.markdown("### Financial Overview")

# creates 4 side-by-side dashboard cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_expenses:,.2f}")
col3.metric("Net Savings", f"${net_savings:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:,.1f}%")

st.divider()

# groups expenses by category
category_df = (
    expense_df.groupby("category_name", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "total_spent"})
    .sort_values("total_spent", ascending=False)
)

# creates monthly expense totals
monthly_expense_df = (
    expense_df.assign(month=expense_df["transaction_date"].dt.to_period("M").astype(str))
    .groupby("month", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "total_spent"})
)

# creates monthly income totals
monthly_income_df = (
    income_df.assign(month=income_df["transaction_date"].dt.to_period("M").astype(str))
    .groupby("month", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "total_income"})
)

# combined monthly income and expense
monthly_combined = pd.merge(
    monthly_expense_df,
    monthly_income_df,
    on="month",
    how="outer"
).fillna(0)         # replaces missing values with 0

# calculates monthly savings for each month
if not monthly_combined.empty:
    monthly_combined["savings"] = (
        monthly_combined["total_income"] - monthly_combined["total_spent"]
    )

# finds the top 5 merchants by total spending
# calculates the number of transactions per merchant and total amount spent per merchant
merchant_df = (
    expense_df.groupby("merchant", as_index=False)
    .agg(transaction_count=("merchant", "count"), total_amount=("amount", "sum"))
    .sort_values("total_amount", ascending=False)
    .head(5)
)

# displays a quick insight
if not category_df.empty:
    top_category = category_df.iloc[0]["category_name"]
    st.info(f"Highest spending category: {top_category}")

# creates chart layout
left, right = st.columns(2)

# spending by category - bar chart
with left:
    st.subheader("Category_level Spending Breakdown")
    if not category_df.empty:
        fig_category = px.bar(
            category_df, 
            x="category_name",
            y="total_spent",
            title="Total Spending by Category"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.info("No expense data available for the selected filters.")

# monthly income/expenses/savings - line chart
with right:
    st.subheader("Monthly Financial Trends")
    if not monthly_combined.empty:
        fig_monthly = px.line(
            monthly_combined,
            x="month",
            y=["total_income", "total_spent", "savings"],
            markers=True,
            title="Monthly Financial Trend"
        )
        st.plotly_chart(fig_monthly, use_container_wdith=True)
    else:
        st.info("No monthly data available for the selected filters.")

st.divider()

# creates second chart layout
left2, right2 = st.columns(2)

# creates a pie chart showing what % of spending belongs to each category
with left2:
    st.subheader("Spending Distribution")
    if not category_df.empty:
        fig_pie = px.pie(
            category_df,
            names="category_name",
            values="total_spent",
            title="Spending Distribution by Category"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No expense data available for the selected filters.")

# displays the top merchants table
with right2:
    st.subheader("Top Spending Merchants")
    st.dataframe(merchant_df, use_container_width=True)

st.divider()

# displays the filtered transactions table
st.subheader("Transaction History")
st.dataframe(filtered_df, use_container_width=True)