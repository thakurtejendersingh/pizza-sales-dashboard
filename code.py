import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("pizza_sales.csv", parse_dates=["order_date"])

# Data preprocessing
df['order_time'] = pd.to_datetime(df['order_time'], format='%H:%M:%S').dt.time
df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S').apply(lambda x: x.hour)
df['day_of_week'] = df['order_date'].dt.day_name()

# Title
st.title("🍕 Pizza Sales Dashboard")
st.markdown("A Business Intelligence Dashboard for Plato's Pizza")

# KPI Section
total_revenue = df['total_price'].sum()
total_orders = df['order_id'].nunique()
avg_order_value = total_revenue / total_orders
total_pizzas = df['quantity'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders}")
col3.metric("Avg Order Value", f"${avg_order_value:.2f}")
col4.metric("Total Pizzas Sold", f"{total_pizzas}")

st.markdown("---")

# Revenue over time
st.subheader("📈 Total Revenue Over Time")
rev_over_time = df.groupby("order_date")['total_price'].sum().reset_index()
fig1 = px.line(rev_over_time, x="order_date", y="total_price", title="Revenue Trend")
st.plotly_chart(fig1, use_container_width=True)

# Revenue by hour
st.subheader("🕒 Revenue by Hour of Day")
rev_by_hour = df.groupby("hour")['total_price'].sum().reset_index()
fig2 = px.bar(rev_by_hour, x="hour", y="total_price", title="Hourly Revenue")
st.plotly_chart(fig2, use_container_width=True)

# Revenue by weekday
st.subheader("📅 Revenue by Day of Week")
rev_by_day = df.groupby("day_of_week")['total_price'].sum().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
).reset_index()
fig3 = px.bar(rev_by_day, x="day_of_week", y="total_price", title="Revenue by Day")
st.plotly_chart(fig3, use_container_width=True)

# Best and worst-selling pizzas
st.subheader("🍕 Best & Worst Selling Pizzas")
pizza_sales = df.groupby("pizza_name")['quantity'].sum().reset_index().sort_values(by="quantity", ascending=False)
fig4 = px.bar(pizza_sales.head(10), x="quantity", y="pizza_name", orientation="h", title="Top 10 Best-Selling Pizzas")
fig5 = px.bar(pizza_sales.tail(10), x="quantity", y="pizza_name", orientation="h", title="Bottom 10 Worst-Selling Pizzas")
st.plotly_chart(fig4, use_container_width=True)
st.plotly_chart(fig5, use_container_width=True)

# Seating utilization
st.subheader("🪑 Seating Utilization Estimate")
orders_per_day = df.groupby("order_date")['order_id'].nunique().mean()
seats = 60
tables = 15
max_daily_capacity = tables * (12 * 60 / 45)  # Assuming 45 min avg turnover, 12 hours/day
utilization_pct = min(100, round((orders_per_day / max_daily_capacity) * 100, 2))
st.write(f"Estimated Daily Seating Utilization: **{utilization_pct}%**")

st.markdown("---")
st.markdown("📌 Created using Streamlit, Plotly & Pandas | Data: Maven Pizza Challenge")

