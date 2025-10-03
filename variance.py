import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Transaction & Invoice Dashboard", layout="wide")

# ---------------------------
# Load datasets
# ---------------------------
df = pd.read_excel("transactions.xlsx")      # PO dataset
invoice_df = pd.read_excel("invoice_list.xlsx")  # Invoice dataset

# Clean column names
df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
invoice_df.columns = invoice_df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")

# ---------------------------
# Sidebar Page Selection
# ---------------------------
page = st.sidebar.radio("📑 Select Page", ["Transactions Dashboard", "Invoice Analysis"])

# ---------------------------
# Transactions Dashboard
# ---------------------------
if page == "Transactions Dashboard":
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
        options=["All"] + sorted(df["Converted"].fillna("Unchecked").unique().tolist()), 
        index=0
    )

    # Apply filters
    df_filtered = df.copy()
    if po_status != "All":
        df_filtered = df_filtered[df_filtered["Posted"] == po_status]
    if converted_status != "All":
        df_filtered = df_filtered[df_filtered["Converted"] == converted_status]

    # ---------------------------
    # Key Metrics
    # ---------------------------
    total_sum_filtered = df_filtered["Total"].sum()
    total_count_filtered = len(df_filtered)
    total_qty_filtered = df_filtered.get("Total Qty", pd.Series([0])).sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Sum of Total", f"{total_sum_filtered:,.2f}")
    with col2:
        st.metric("🧾 Number of Transactions", total_count_filtered)
    with col3:
        st.metric("📦 Total Quantity", f"{total_qty_filtered:,.0f}")

    st.markdown(f"**Total Transactions in Dataset:** {len(df)} | **Filtered Transactions:** {total_count_filtered}")

    # ---------------------------
    # Top 30 transactions graph
    # ---------------------------
    df_top30 = df_filtered.sort_values(by="Total", ascending=False).head(30)
    st.subheader("Top 30 Transactions by Total Value")
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
    # Full table (dark mode)
    # ---------------------------
    st.subheader("Filtered Transactions Table")
    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    gb.configure_default_column(
        cellStyle=JsCode("""
        function(params) {
            return {'color': 'white', 'backgroundColor': '#1e1e1e'};
        }
        """)
    )
    AgGrid(df_filtered, gridOptions=gb.build(), height=600)

# ---------------------------
# Invoice Analysis
# ---------------------------
if page == "Invoice Analysis":
    st.title("📄 Transactions with Invoices Not Yet Converted")

    # Filter POs: Posted = Checked, Converted = Unchecked
    po_filtered = df[(df["Posted"] == "Checked") & (df["Converted"] == "Unchecked")].copy()

    # Ensure numeric columns
    po_filtered["Total"] = pd.to_numeric(po_filtered["Total"], errors="coerce")
    invoice_df["Total"] = pd.to_numeric(invoice_df["Total"], errors="coerce")

    # Merge POs with invoices after PO created date
    invoice_df_renamed = invoice_df.rename(columns={
        "Tran No": "Invoice Tran No",
        "Created Date": "Invoice Created Date",
        "Total": "Invoice Total",
        "Particulars": "Invoice Particulars"
    })

    merged_df = po_filtered.merge(
        invoice_df_renamed,
        left_on="Particulars",
        right_on="Invoice Particulars",
        how="left"
    )
    merged_df = merged_df[merged_df["Invoice Created Date"] > merged_df["Created Date"]]

    # Keep only POs with matching invoices
    filtered_invoice = merged_df[merged_df["Invoice Tran No"].notnull()]

    # ---------------------------
    # Key Insights
    # ---------------------------
    if filtered_invoice.empty:
        st.info("No transactions match the criteria.")
    else:
        total_po_value = filtered_invoice["Total"].sum()
        total_invoice_value = filtered_invoice["Invoice Total"].sum()
        total_transactions_filtered = len(filtered_invoice)
        total_transactions_all = len(po_filtered)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total PO Value", f"{total_po_value:,.2f}")
        with col2:
            st.metric("🧾 Total Transactions", total_transactions_filtered)
        with col3:
            st.metric("💳 Total Invoice Value", f"{total_invoice_value:,.2f}")

        st.markdown(f"**Total PO Transactions:** {total_transactions_all} | **Filtered Transactions:** {total_transactions_filtered}")

        # ---------------------------
        # Display filtered invoice table (dark mode)
        # ---------------------------
        display_cols = [
            "Tran No",
            "Invoice Tran No",
            "Particulars",
            "Invoice Particulars",
            "Total",
            "Invoice Total",
            "Created Date",
            "Invoice Created Date",
            "Converted",
            "Posted"
        ]
        st.subheader("Filtered Invoice Transactions")
        gb_inv = GridOptionsBuilder.from_dataframe(filtered_invoice[display_cols].sort_values(by="Invoice Created Date", ascending=False))
        gb_inv.configure_default_column(
            cellStyle=JsCode("""
            function(params) {
                return {'color': 'white', 'backgroundColor': '#1e1e1e'};
            }
            """)
        )
        AgGrid(filtered_invoice[display_cols].sort_values(by="Invoice Created Date", ascending=False), gridOptions=gb_inv.build(), height=600)
