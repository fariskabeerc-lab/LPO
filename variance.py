import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load datasets
# ---------------------------
df = pd.read_excel("transactions.xlsx")         # PO file
invoice_df = pd.read_excel("invoice_list.xlsx") # Invoice file

# ---------------------------
# Clean column names
# ---------------------------
def clean_cols(df):
    df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
    return df

df = clean_cols(df)
invoice_df = clean_cols(invoice_df)

# ---------------------------
# Convert necessary columns to datetime
# ---------------------------
df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
invoice_df["Created Date"] = pd.to_datetime(invoice_df["Created Date"], errors="coerce")

# ---------------------------
# Sidebar Page Selection
# ---------------------------
page = st.sidebar.radio("📑 Select Page", ["Transactions Dashboard", "Invoice Analysis"])

# ---------------------------
# Transactions Dashboard
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
    total_sum_all = df["Total"].sum()
    total_count_all = len(df)
    total_qty_all = df["Total Qty"].sum() if "Total Qty" in df.columns else 0

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

    st.markdown(f"**Total Transactions in dataset:** {total_count_all}  |  **Filtered Transactions:** {total_count_filtered}")

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
# Invoice Analysis
# ---------------------------
if page == "Invoice Analysis":
    st.set_page_config(page_title="Invoices Not Converted", layout="wide")
    st.title("📄 Transactions with Invoices Not Yet Converted")

    # Filter POs: Posted = Checked, Converted = Unchecked
    po_filtered = df[(df["Posted"] == "Checked") & (df["Converted"] == "Unchecked")].copy()

    # Ensure numeric columns
    po_filtered["Total"] = pd.to_numeric(po_filtered["Total"], errors="coerce")
    invoice_df["Total"] = pd.to_numeric(invoice_df["Total"], errors="coerce")

    # For each PO, find first matching invoice after Created Date for same Particular
    def match_invoice(row, inv_df):
        matches = inv_df[(inv_df["Particulars"] == row["Particulars"]) &
                         (inv_df["Created Date"] > row["Created Date"])]
        if not matches.empty:
            inv_row = matches.iloc[0]
            return pd.Series({
                "Invoice Tran No": inv_row["Tran No"],
                "Invoice Created Date": inv_row["Created Date"],
                "Invoice Total": inv_row["Total"]
            })
        else:
            return pd.Series({
                "Invoice Tran No": None,
                "Invoice Created Date": None,
                "Invoice Total": 0
            })

    invoice_matches = po_filtered.apply(lambda r: match_invoice(r, invoice_df), axis=1)
    po_with_invoice = pd.concat([po_filtered.reset_index(drop=True), invoice_matches], axis=1)

    # Keep only POs that have matching invoices
    filtered_invoice = po_with_invoice[po_with_invoice["Invoice Tran No"].notnull()]

    # ---------------------------
    # Key Insights (from filtered_invoice only)
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

        st.markdown(f"**Total PO Transactions:** {total_transactions_all}  |  **Filtered Transactions:** {total_transactions_filtered}")

        # Display filtered invoice table with PO Tran No + Invoice Tran No
        display_cols = [
            "Tran No",            # PO Tran No
            "Invoice Tran No",    # Invoice Tran No
            "Particulars",
            "Total",              # PO Total
            "Invoice Total",
            "Created Date",       # PO Created Date
            "Invoice Created Date",
            "Converted",
            "Posted"
        ]
        st.subheader("Filtered Invoice Transactions")
        st.dataframe(
            filtered_invoice[display_cols].sort_values(by="Invoice Created Date", ascending=False),
            use_container_width=True,
            height=600
        )
