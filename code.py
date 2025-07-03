import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Data Loading and Preprocessing ---
# Load the dataset
try:
    df = pd.read_csv("Data Model - Pizza Sales.xlsx - pizza_sales.csv")
    print("CSV loaded successfully.")
    # print(df.head()) # Commenting out to keep output concise for final code
    # print(df.info()) # Commenting out to keep output concise for final code
except FileNotFoundError:
    print("Error: 'Data Model - Pizza Sales.xlsx - pizza_sales.csv' not found. Please ensure the file is in the correct directory.")
    exit() # Exit if file not found as further operations will fail

# Convert 'order_date' to datetime objects
df['order_date'] = pd.to_datetime(df['order_date'])
# Convert 'order_time' to datetime.time objects (assuming it's in a time format)
df['order_time'] = pd.to_datetime(df['order_time']).dt.time

print("\n--- Data Preprocessing Complete ---")
# print(df.info()) # Commenting out to keep output concise for final code


# --- 2. Key Performance Indicators (KPIs) Calculation ---
print("\n--- Calculating KPIs ---")
total_revenue = df['total_price'].sum()
total_orders = df['order_id'].nunique()
avg_order_value = total_revenue / total_orders
total_pizzas_sold = df['quantity'].sum()
avg_pizzas_per_order = total_pizzas_sold / total_orders

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Order Value: ${avg_order_value:,.2f}")
print(f"Total Pizzas Sold: {total_pizzas_sold:,}")
print(f"Total Orders: {total_orders:,}")
print(f"Average Pizzas Per Order: {avg_pizzas_per_order:,.2f}")


# --- 3. Monthly Trend for Orders (Line Chart) ---
print("\n--- Generating Monthly Trend for Orders Chart ---")
df['month_name'] = df['order_date'].dt.strftime('%B')
df['month_num'] = df['order_date'].dt.month
monthly_orders = df.groupby(['month_num', 'month_name']).agg(
    Total_Orders=('order_id', 'nunique')
).reset_index().sort_values('month_num')

plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_orders, x='month_name', y='Total_Orders', marker='o')
plt.title('Monthly Trend for Orders')
plt.xlabel('Month')
plt.ylabel('Total Orders')
plt.grid(True)
plt.show()


# --- 4. % of Sales by Pizza Category (Donut Chart) ---
print("\n--- Generating % of Sales by Pizza Category Chart ---")
category_sales = df.groupby('pizza_category').agg(
    Total_Revenue=('total_price', 'sum')
).reset_index()

total_revenue_all = category_sales['Total_Revenue'].sum()
category_sales['PCT'] = (category_sales['Total_Revenue'] / total_revenue_all) * 100

plt.figure(figsize=(8, 8))
plt.pie(category_sales['PCT'], labels=category_sales['pizza_category'], autopct='%1.1f%%', startangle=90, pctdistance=0.85)
plt.title('% of Sales by Pizza Category')
plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
plt.show()


# --- 5. % of Sales by Pizza Size (Bar Chart) ---
print("\n--- Generating % of Sales by Pizza Size Chart ---")
size_sales = df.groupby('pizza_size').agg(
    Total_Revenue=('total_price', 'sum')
).reset_index()

total_revenue_all_size = size_sales['Total_Revenue'].sum() # Recalculate total revenue in case subset was used
size_sales['PCT'] = (size_sales['Total_Revenue'] / total_revenue_all_size) * 100

# Define order for sizes to ensure correct display
size_order = ['S', 'M', 'L', 'XL', 'XXL']
size_sales['pizza_size'] = pd.Categorical(size_sales['pizza_size'], categories=size_order, ordered=True)
size_sales = size_sales.sort_values('pizza_size')

plt.figure(figsize=(10, 6))
sns.barplot(data=size_sales, x='pizza_size', y='PCT', palette='viridis')
plt.title('% of Sales by Pizza Size')
plt.xlabel('Pizza Size')
plt.ylabel('Percentage of Sales (%)')
plt.show()


# --- 6. Top 5 Best Sellers by Revenue (Bar Chart) ---
print("\n--- Generating Top 5 Best Sellers by Revenue Chart ---")
top_5_revenue = df.groupby('pizza_name').agg(
    Total_Revenue=('total_price', 'sum')
).reset_index().sort_values('Total_Revenue', ascending=False).head(5)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_5_revenue, x='Total_Revenue', y='pizza_name', palette='plasma')
plt.title('Top 5 Best Sellers by Revenue')
plt.xlabel('Total Revenue ($)')
plt.ylabel('Pizza Name')
plt.show()


# --- 7. Top 5 Best Sellers by Quantity (Bar Chart) ---
print("\n--- Generating Top 5 Best Sellers by Quantity Chart ---")
top_5_quantity = df.groupby('pizza_name').agg(
    Total_Quantity_Sold=('quantity', 'sum')
).reset_index().sort_values('Total_Quantity_Sold', ascending=False).head(5)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_5_quantity, x='Total_Quantity_Sold', y='pizza_name', palette='magma')
plt.title('Top 5 Best Sellers by Quantity')
plt.xlabel('Total Quantity Sold')
plt.ylabel('Pizza Name')
plt.show()


# --- 8. Top 5 Best Sellers by Total Orders (Bar Chart) ---
print("\n--- Generating Top 5 Best Sellers by Total Orders Chart ---")
top_5_orders = df.groupby('pizza_name').agg(
    Total_Orders=('order_id', 'nunique')
).reset_index().sort_values('Total_Orders', ascending=False).head(5)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_5_orders, x='Total_Orders', y='pizza_name', palette='viridis')
plt.title('Top 5 Best Sellers by Total Orders')
plt.xlabel('Total Orders')
plt.ylabel('Pizza Name')
plt.show()


# --- 9. Daily Trend for Total Orders (Line Chart) ---
print("\n--- Generating Daily Trend for Total Orders Chart ---")
df['day_of_week'] = df['order_date'].dt.day_name()
daily_orders = df.groupby('day_of_week').agg(
    Total_Orders=('order_id', 'nunique')
).reset_index()

# Define order for days of the week to ensure correct display
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_orders['day_of_week'] = pd.Categorical(daily_orders['day_of_week'], categories=day_order, ordered=True)
daily_orders = daily_orders.sort_values('day_of_week')

plt.figure(figsize=(10, 6))
sns.lineplot(data=daily_orders, x='day_of_week', y='Total_Orders', marker='o')
plt.title('Daily Trend for Total Orders')
plt.xlabel('Day of Week')
plt.ylabel('Total Orders')
plt.grid(True)
plt.show()


# --- 10. Conceptual Dashboard Layout (Multiple Plots in one figure) ---
# This section demonstrates how you might arrange several plots together,
# but it's a static representation and not an interactive Tableau dashboard.
print("\n--- Generating Conceptual Dashboard Layout ---")
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(20, 28)) # Adjusted for more plots
fig.suptitle('Pizza Sales Dashboard (Conceptual Layout with Key Visuals)', fontsize=20, y=1.02) # Adjusted title position

# KPI Section (often text-based, so represented conceptually here)
axes[0, 0].text(0.1, 0.8, f"Total Revenue: ${total_revenue:,.2f}", fontsize=14, weight='bold')
axes[0, 0].text(0.1, 0.65, f"Total Orders: {total_orders:,}", fontsize=14)
axes[0, 0].text(0.1, 0.5, f"Avg Order Value: ${avg_order_value:,.2f}", fontsize=14)
axes[0, 0].text(0.1, 0.35, f"Total Pizzas Sold: {total_pizzas_sold:,}", fontsize=14)
axes[0, 0].text(0.1, 0.2, f"Avg Pizzas Per Order: {avg_pizzas_per_order:,.2f}", fontsize=14)
axes[0, 0].set_title('Key Performance Indicators', fontsize=16)
axes[0, 0].axis('off') # Hide axes for text

# Monthly Trend for Orders
sns.lineplot(data=monthly_orders, x='month_name', y='Total_Orders', marker='o', ax=axes[0, 1])
axes[0, 1].set_title('Monthly Trend for Orders', fontsize=16)
axes[0, 1].set_xlabel('Month', fontsize=12)
axes[0, 1].set_ylabel('Total Orders', fontsize=12)
axes[0, 1].grid(True)

# % of Sales by Pizza Category
axes[1, 0].pie(category_sales['PCT'], labels=category_sales['pizza_category'], autopct='%1.1f%%', startangle=90, pctdistance=0.85)
axes[1, 0].set_title('% of Sales by Pizza Category', fontsize=16)
centre_circle_cat = plt.Circle((0,0), 0.70, fc='white')
axes[1, 0].add_artist(centre_circle_cat)
axes[1, 0].axis('equal')

# % of Sales by Pizza Size
sns.barplot(data=size_sales, x='pizza_size', y='PCT', palette='viridis', ax=axes[1, 1])
axes[1, 1].set_title('% of Sales by Pizza Size', fontsize=16)
axes[1, 1].set_xlabel('Pizza Size', fontsize=12)
axes[1, 1].set_ylabel('Percentage of Sales (%)', fontsize=12)

# Top 5 Best Sellers by Revenue
sns.barplot(data=top_5_revenue, x='Total_Revenue', y='pizza_name', palette='plasma', ax=axes[2, 0])
axes[2, 0].set_title('Top 5 Best Sellers by Revenue', fontsize=16)
axes[2, 0].set_xlabel('Total Revenue ($)', fontsize=12)
axes[2, 0].set_ylabel('Pizza Name', fontsize=12)

# Top 5 Best Sellers by Quantity
sns.barplot(data=top_5_quantity, x='Total_Quantity_Sold', y='pizza_name', palette='magma', ax=axes[2, 1])
axes[2, 1].set_title('Top 5 Best Sellers by Quantity', fontsize=16)
axes[2, 1].set_xlabel('Total Quantity Sold', fontsize=12)
axes[2, 1].set_ylabel('Pizza Name', fontsize=12)

# Top 5 Best Sellers by Total Orders
sns.barplot(data=top_5_orders, x='Total_Orders', y='pizza_name', palette='viridis', ax=axes[3, 0])
axes[3, 0].set_title('Top 5 Best Sellers by Total Orders', fontsize=16)
axes[3, 0].set_xlabel('Total Orders', fontsize=12)
axes[3, 0].set_ylabel('Pizza Name', fontsize=12)

# Daily Trend for Total Orders
sns.lineplot(data=daily_orders, x='day_of_week', y='Total_Orders', marker='o', ax=axes[3, 1])
axes[3, 1].set_title('Daily Trend for Total Orders', fontsize=16)
axes[3, 1].set_xlabel('Day of Week', fontsize=12)
axes[3, 1].set_ylabel('Total Orders', fontsize=12)
axes[3, 1].grid(True)

plt.tight_layout(rect=[0, 0.03, 1, 0.98]) # Adjust layout to prevent title overlap and fit all plots
plt.show()

print("\n--- All charts generated and conceptual dashboard layout displayed. ---")
print("Note: For an interactive dashboard as shown in screenshots, Tableau Desktop is required.")
print("This code provides the data processing and static visualization components using Python.")
