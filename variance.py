import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load datasets
# ---------------------------
df = pd.read_excel("transactions.xlsx")       # Transaction table
invoice_df = pd.read_excel("invoice_list.xlsx")  # Invoice table

# ---------------------------
# Clean column names
# ---------------------------
df.columns = df.columns.str.strip()
invoice_df.columns = invoice_df.columns.str.strip()

# ---------------------------
# Sidebar Page Selection
# ---------------------------
page = st.sidebar.radio("📑 Select Page", ["Transactions Dashboard", "Invoices Not Converted"])

# ---------------------------
# Transactions Dashboard Page
# ---------------------------
if page == "Transactions Dashboard":
    st.set_page_config(page_title="Transaction Dashboard", layout="wide")
    st.title("📊 Transaction Dashboard")

    # Sidebar Filters
    st.sidebar.header("Filters")
    po_status = st.sidebar.selectbox(
        "PO Status",
        options=["All"] + sorted(df["Posted"].dropna().unique().tolist()),
        index=0
    )
    converted_status = st.sidebar.selectbox(
        "Converted Status",
        options=["All"] + sorted(df["Converted"].dropna().unique().tolist()),
        index=0
    )

    # Apply filters
    df_filtered = df.copy()
    if po_status != "All":
        df_filtered = df_filtered[df_filtered["Posted"] == po_status]
    if converted_status != "All":
        df_filtered = df_filtered[df_filtered["Converted"] == converted_status]

    # Metrics
    total_sum_filtered = df_filtered["Total"].sum()
    total_count_filtered = len(df_filtered)
    total_qty_filtered = df_filtered["Total Qty"].sum() if "Total Qty" in df_filtered.columns else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Sum of Total", f"{total_sum_filtered:,.2f}")
    with col2:
        st.metric("🧾 Number of Transactions", total_count_filtered)
    with col3:
        st.metric("📦 Total Quantity", f"{total_qty_filtered:,.0f}")

    # Top 30 transactions
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

    # Full table
    st.subheader("Filtered Transactions Table")
    st.dataframe(
        df_filtered[
            ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]
        ],
        use_container_width=True,
        height=600
    )

# ---------------------------
# Invoices Not Converted Page
# ---------------------------
if page == "Invoices Not Converted":
    st.set_page_config(page_title="Invoices Not Converted", layout="wide")
    st.title("📄 Transactions with Invoices Not Yet Converted")

    # Sidebar Filters
    st.sidebar.header("Filters")
    po_status_inv = st.sidebar.selectbox(
        "PO Status",
        options=["All"] + sorted(df["Posted"].dropna().unique().tolist()),
        index=0
    )
    converted_status_inv = st.sidebar.selectbox(
        "Converted Status",
        options=["All"] + sorted(df["Converted"].dropna().unique().tolist()),
        index=0
    )

    # Merge transactions with invoice list
    # Use 'Tran No' as key; adjust if 'Particulars' is the correct key
    merged_df = pd.merge(
        invoice_df,
        df,
        on=["Tran No"],  
        suffixes=("_inv", "_po")
    )

    filtered_df = merged_df.copy()

    # Apply filters
    if po_status_inv != "All":
        filtered_df = filtered_df[filtered_df["Posted_po"] == po_status_inv]
    if converted_status_inv != "All":
        filtered_df = filtered_df[filtered_df["Converted_po"] == converted_status_inv]

    # Only show transactions with invoices where Converted = Unchecked
    final_df = filtered_df[filtered_df["Converted_po"] == "Unchecked"]

    st.markdown(f"**Total Transactions:** {len(final_df)}")

    st.dataframe(
        final_df[
            ["Tran No", "Particulars", "Total_po", "Invoice Print Date", "Converted_po", "Posted_po"]
        ].sort_values(by="Invoice Print Date", ascending=False),
        use_container_width=True,
        height=600
    )
