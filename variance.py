import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_excel("transactions.xlsx")
df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Transaction Dashboard")

# ---------------------------
# Sidebar Filters (checkbox style)
# ---------------------------
st.sidebar.header("Filters")

# Function to create standard checkbox filters
def create_checkbox_filter(column_name, label):
    unique_values = df[column_name].dropna().unique().tolist()
    
    # Default all checked
    checked_values = []
    for val in unique_values:
        if st.sidebar.checkbox(f"{label}: {val}", value=True):
            checked_values.append(val)
    
    # If none selected, select all automatically
    if not checked_values:
        checked_values = unique_values
    return checked_values

# Apply checkbox filters
posted_values = create_checkbox_filter("Posted", "PO Status")
converted_values = create_checkbox_filter("Converted", "Converted Status")

# Filter the dataframe
df_filtered = df[(df["Posted"].isin(posted_values)) & (df["Converted"].isin(converted_values))]

# ---------------------------
# Metrics based on full dataset
# ---------------------------
total_sum_all = df["Total"].sum()
total_count_all = len(df)
total_qty_all = df["Total Qty"].sum() if "Total Qty" in df.columns else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Sum of Total", f"{total_sum_all:,.2f}")
with col2:
    st.metric("🧾 Number of Transactions", total_count_all)
with col3:
    st.metric("📦 Total Quantity", f"{total_qty_all:,.0f}")

# ---------------------------
# Top 30 transactions by Total for graph
# ---------------------------
df_top30 = df_filtered.sort_values(by="Total", ascending=False).head(30)

st.subheader("Top 30 Transactions by Total Value (Filtered)")

fig = px.bar(
    df_top30,
    x="Total",
    y="Particulars",
    orientation="h",
    text="Total",
    hover_data=["Tran No", "Tran Date", "Discount", "Net Total"],
    color_discrete_sequence=["teal"]
)

fig.update_traces(
    texttemplate="%{text:,.2f}",
    textposition="outside",
    marker=dict(line=dict(width=1, color="white"))
)

fig.update_layout(
    xaxis_title="Total Value",
    yaxis_title="Particulars",
    yaxis=dict(autorange="reversed"),
    xaxis=dict(gridcolor="gray"),
    height=800,
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#1e1e1e",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Full Transactions Table
# ---------------------------
st.subheader("Filtered Transactions Table")

st.dataframe(
    df_filtered[
        ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]
    ],
    use_container_width=True,
    height=600
)
