import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Enhanced Pizza Sales Dashboard")

st.title("🍕 Enhanced Pizza Sales Dashboard")

# --- Data Loading and Preprocessing ---
@st.cache_data # Cache data to prevent re-loading on every rerun
def load_data():
    try:
        df = pd.read_csv("Data Model - Pizza Sales.xlsx - pizza_sales.csv")
        df['order_date'] = pd.to_datetime(df['order_date'])
        # Convert 'order_time' to datetime.time objects
        # Using a fixed format for parsing time to avoid issues with different string formats
        df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(str(x), '%H:%M:%S').time())
        return df
    except FileNotFoundError:
        st.error("Error: 'Data Model - Pizza Sales.xlsx - pizza_sales.csv' not found. Please ensure the file is in the correct directory.")
        st.stop() # Stop the app if data file is missing
    except Exception as e:
        st.error(f"An error occurred while loading or processing the data: {e}")
        st.stop()

df = load_data()

if df is None:
    st.stop() # Stop if data loading failed

# --- Filters ---
st.sidebar.header("Filter Options")

# Date Range Filter
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df_filtered = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered['order_date'].dt.date >= start_date) & (df_filtered['order_date'].dt.date <= end_date)].copy()
elif len(date_range) == 1:
    # If only one date is selected, filter for that specific day
    selected_date = date_range[0]
    df_filtered = df_filtered[df_filtered['order_date'].dt.date == selected_date].copy()
else:
    st.sidebar.warning("Please select a start and end date for the filter.")

# Pizza Category Filter
all_categories = df_filtered['pizza_category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Select Pizza Category(s)",
    options=all_categories,
    default=all_categories # Select all by default
)
if selected_categories:
    df_filtered = df_filtered[df_filtered['pizza_category'].isin(selected_categories)].copy()

# Pizza Size Filter
all_sizes = df_filtered['pizza_size'].unique().tolist()
selected_sizes = st.sidebar.multiselect(
    "Select Pizza Size(s)",
    options=all_sizes,
    default=all_sizes # Select all by default
)
if selected_sizes:
    df_filtered = df_filtered[df_filtered['pizza_size'].isin(selected_sizes)].copy()

# Pizza Name Filter (Top N for performance/usability)
all_pizza_names = df_filtered['pizza_name'].unique().tolist()
selected_pizza_names = st.sidebar.multiselect(
    "Select Pizza Name(s)",
    options=all_pizza_names,
    default=all_pizza_names # Select all by default
)
if selected_pizza_names:
    df_filtered = df_filtered[df_filtered['pizza_name'].isin(selected_pizza_names)].copy()


if df_filtered.empty:
    st.warning("No data available for the selected filters. Please adjust the filters.")
    st.stop()


# --- Key Performance Indicators (KPIs) ---
st.header("Key Performance Indicators (KPIs)")

# Recalculate KPIs based on filtered data
total_revenue = df_filtered['total_price'].sum()
total_orders = df_filtered['order_id'].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0
total_pizzas_sold = df_filtered['quantity'].sum()
avg_pizzas_per_order = total_pizzas_sold / total_orders if total_orders else 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
with kpi_col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
with kpi_col2:
    st.metric(label="Average Order Value", value=f"${avg_order_value:,.2f}")
with kpi_col3:
    st.metric(label="Total Pizzas Sold", value=f"{total_pizzas_sold:,}")
with kpi_col4:
    st.metric(label="Total Orders", value=f"{total_orders:,}")
with kpi_col5:
    st.metric(label="Avg Pizzas Per Order", value=f"{avg_pizzas_per_order:,.2f}")

st.markdown("---")

# --- Sales Trends and Insights ---
st.header("Sales Trends and Performance")

trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    # --- Monthly Trend for Orders (Line Chart) ---
    st.subheader("Monthly Trend for Orders")
    df_filtered['month_name'] = df_filtered['order_date'].dt.strftime('%B')
    df_filtered['month_num'] = df_filtered['order_date'].dt.month
    monthly_orders = df_filtered.groupby(['month_num', 'month_name']).agg(
        Total_Orders=('order_id', 'nunique')
    ).reset_index().sort_values('month_num')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=monthly_orders, x='month_name', y='Total_Orders', marker='o', ax=ax)
    ax.set_title('Monthly Trend for Orders')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Orders')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)


with trend_col2:
    # --- Daily Trend for Total Orders (Line Chart) ---
    st.subheader("Daily Trend for Total Orders")
    df_filtered['day_of_week'] = df_filtered['order_date'].dt.day_name()
    daily_orders = df_filtered.groupby('day_of_week').agg(
        Total_Orders=('order_id', 'nunique')
    ).reset_index()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_orders['day_of_week'] = pd.Categorical(daily_orders['day_of_week'], categories=day_order, ordered=True)
    daily_orders = daily_orders.sort_values('day_of_week')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=daily_orders, x='day_of_week', y='Total_Orders', marker='o', ax=ax)
    ax.set_title('Daily Trend for Total Orders')
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Total Orders')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# --- New Segments: Hourly Trends ---
st.header("Hourly Analysis")
hourly_col1, hourly_col2 = st.columns(2)

with hourly_col1:
    # --- Hourly Trend for Orders ---
    st.subheader("Total Orders by Hour of Day")
    # Extract hour from order_time (datetime.time object)
    df_filtered['order_hour'] = df_filtered['order_time'].apply(lambda x: x.hour)
    hourly_orders = df_filtered.groupby('order_hour').agg(
        Total_Orders=('order_id', 'nunique')
    ).reset_index().sort_values('order_hour')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=hourly_orders, x='order_hour', y='Total_Orders', marker='o', ax=ax)
    ax.set_title('Total Orders by Hour of Day')
    ax.set_xlabel('Hour of Day (24-hour)')
    ax.set_ylabel('Total Orders')
    ax.set_xticks(range(0, 24, 2)) # Show every other hour
    ax.grid(True)
    st.pyplot(fig)

with hourly_col2:
    # --- Hourly Trend for Revenue ---
    st.subheader("Total Revenue by Hour of Day")
    hourly_revenue = df_filtered.groupby('order_hour').agg(
        Total_Revenue=('total_price', 'sum')
    ).reset_index().sort_values('order_hour')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=hourly_revenue, x='order_hour', y='Total_Revenue', marker='o', ax=ax)
    ax.set_title('Total Revenue by Hour of Day')
    ax.set_xlabel('Hour of Day (24-hour)')
    ax.set_ylabel('Total Revenue ($)')
    ax.set_xticks(range(0, 24, 2)) # Show every other hour
    ax.grid(True)
    st.pyplot(fig)

st.markdown("---")


# --- Category, Size, and Top Sellers Analysis ---
st.header("Product Performance")

prod_col1, prod_col2 = st.columns(2)

with prod_col1:
    # --- % of Sales by Pizza Category (Donut Chart) ---
    st.subheader("% of Sales by Pizza Category")
    category_sales = df_filtered.groupby('pizza_category').agg(
        Total_Revenue=('total_price', 'sum')
    ).reset_index()

    total_revenue_cat = category_sales['Total_Revenue'].sum()
    if total_revenue_cat > 0: # Avoid division by zero
        category_sales['PCT'] = (category_sales['Total_Revenue'] / total_revenue_cat) * 100
    else:
        category_sales['PCT'] = 0

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(category_sales['PCT'], labels=category_sales['pizza_category'], autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    ax.set_title('% of Sales by Pizza Category')
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    st.pyplot(fig)


with prod_col2:
    # --- % of Sales by Pizza Size (Bar Chart) ---
    st.subheader("% of Sales by Pizza Size")
    size_sales = df_filtered.groupby('pizza_size').agg(
        Total_Revenue=('total_price', 'sum')
    ).reset_index()

    total_revenue_size = size_sales['Total_Revenue'].sum()
    if total_revenue_size > 0: # Avoid division by zero
        size_sales['PCT'] = (size_sales['Total_Revenue'] / total_revenue_size) * 100
    else:
        size_sales['PCT'] = 0

    size_order = ['S', 'M', 'L', 'XL', 'XXL']
    size_sales['pizza_size'] = pd.Categorical(size_sales['pizza_size'], categories=size_order, ordered=True)
    size_sales = size_sales.sort_values('pizza_size')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=size_sales, x='pizza_size', y='PCT', palette='viridis', ax=ax)
    ax.set_title('% of Sales by Pizza Size')
    ax.set_xlabel('Pizza Size')
    ax.set_ylabel('Percentage of Sales (%)')
    st.pyplot(fig)


top_sellers_col1, top_sellers_col2 = st.columns(2)

with top_sellers_col1:
    # --- Top 5 Best Sellers by Revenue (Bar Chart) ---
    st.subheader("Top 5 Best Sellers by Revenue")
    top_5_revenue = df_filtered.groupby('pizza_name').agg(
        Total_Revenue=('total_price', 'sum')
    ).reset_index().sort_values('Total_Revenue', ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top_5_revenue, x='Total_Revenue', y='pizza_name', palette='plasma', ax=ax)
    ax.set_title('Top 5 Best Sellers by Revenue')
    ax.set_xlabel('Total Revenue ($)')
    ax.set_ylabel('Pizza Name')
    st.pyplot(fig)

with top_sellers_col2:
    # --- Top 5 Best Sellers by Quantity (Bar Chart) ---
    st.subheader("Top 5 Best Sellers by Quantity")
    top_5_quantity = df_filtered.groupby('pizza_name').agg(
        Total_Quantity_Sold=('quantity', 'sum')
    ).reset_index().sort_values('Total_Quantity_Sold', ascending=False).head(5)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=top_5_quantity, x='Total_Quantity_Sold', y='pizza_name', palette='magma', ax=ax)
    ax.set_title('Top 5 Best Sellers by Quantity')
    ax.set_xlabel('Total Quantity Sold')
    ax.set_ylabel('Pizza Name')
    st.pyplot(fig)


# You could add another chart here for Top 5 by Total Orders if space allows
# with st.container():
#     st.subheader("Top 5 Best Sellers by Total Orders")
#     top_5_orders = df_filtered.groupby('pizza_name').agg(
#         Total_Orders=('order_id', 'nunique')
#     ).reset_index().sort_values('Total_Orders', ascending=False).head(5)
#     fig, ax = plt.subplots(figsize=(12, 6))
#     sns.barplot(data=top_5_orders, x='Total_Orders', y='pizza_name', palette='viridis', ax=ax)
#     ax.set_title('Top 5 Best Sellers by Total Orders')
#     ax.set_xlabel('Total Orders')
#     ax.set_ylabel('Pizza Name')
#     st.pyplot(fig)


st.markdown("---")
st.markdown("This interactive dashboard allows you to explore pizza sales data with various filters and insights into trends, product performance, and hourly activity.")
