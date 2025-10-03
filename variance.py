import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_excel("transactions.xlsx")

# ---------------------------
# Clean column names
# ---------------------------
df.columns = df.columns.str.strip().str.replace("\n","").str.replace("\r","")

# Make sure 'Posted' and 'Converted' columns exist
for col in ['Posted', 'Converted']:
    if col not in df.columns:
        st.error(f"Column '{col}' not found in the dataset!")
        st.stop()

# ---------------------------
# Metrics based on full dataset
# ---------------------------
total_sum_all = df["Total"].sum()
total_count_all = len(df)
total_qty_all = df["Total Qty"].sum() if "Total Qty" in df.columns else 0

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Transaction Dashboard")

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

# Function to map checkbox selections
def filter_options(col):
    checked = st.sidebar.checkbox(f"{col} Checked", value=True)
    unchecked = st.sidebar.checkbox(f"{col} Unchecked", value=True)
    # Determine which values to include
    include = []
    if checked:
        include.append("Yes")   # Assuming 'Yes' indicates checked
    if unchecked:
        include.append("No")    # Assuming 'No' indicates unchecked
    if not include:  # If nothing selected, default to all
        include = df[col].unique().tolist()
    return include

# Apply filters
posted_filter = filter_options("Posted")
converted_filter = filter_options("Converted")

df_filtered = df[(df['Posted'].isin(posted_filter)) & (df['Converted'].isin(converted_filter))]

# ---------------------------
# Metrics for filtered data
# ---------------------------
total_sum_filtered = df_filtered["Total"].sum()
total_count_filtered = len(df_filtered)
total_qty_filtered = df_filtered["Total Qty"].sum() if "Total Qty" in df_filtered.columns else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Sum of Total (Filtered)", f"{total_sum_filtered:,.2f}")
with col2:
    st.metric("🧾 Number of Transactions (Filtered)", total_count_filtered)
with col3:
    st.metric("📦 Total Quantity (Filtered)", f"{total_qty_filtered:,.0f}")

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
# Full Transactions Table (filtered)
# ---------------------------
st.subheader("Filtered Transactions Table")
st.dataframe(
    df_filtered[
        ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]
    ],
    use_container_width=True,
    height=600
)
