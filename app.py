import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Mobile optimized layout
st.set_page_config(page_title="SB Online Point", layout="centered", page_icon="🏪")

# Files management
DATA_FILE = "inventory.csv"
SALES_FILE = "sales.csv"

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Service/Item", "Stock", "Cost", "Price"])

def load_sales():
    if os.path.exists(SALES_FILE): return pd.read_csv(SALES_FILE)
    return pd.DataFrame(columns=["Date", "Customer", "Service", "Charge", "Tax", "Total"])

# Initialize data
if 'inv' not in st.session_state: st.session_state.inv = load_data()
if 'sales' not in st.session_state: st.session_state.sales = load_sales()

# Sidebar for Menu
st.sidebar.title("SB Online")
menu = ["📈 Dashboard", "➕ Add Service/Stock", "🧾 New Billing", "📋 Records"]
choice = st.sidebar.radio("Go to", menu)

st.header("🏪 SB Online Point")

# --- 1. Dashboard ---
if choice == "📈 Dashboard":
    total_revenue = st.session_state.sales["Total"].sum()
    st.metric("Total Collection", f"₹{total_revenue}")
    st.subheader("Available Services/Stock")
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- 2. Add Service/Stock ---
elif choice == "➕ Add Service/Stock":
    with st.form("add_form"):
        name = st.text_input("Service Name (e.g., Aadhaar Download, Photocopy)")
        stock = st.number_input("Stock (Use 999 for digital services)", min_value=1)
        cost = st.number_input("Your Cost", min_value=0.0)
        price = st.number_input("Customer Price", min_value=0.0)
        
        if st.form_submit_button("Save Service"):
            new_data = pd.DataFrame([[name, stock, cost, price]], columns=st.session_state.inv.columns)
            st.session_state.inv = pd.concat([st.session_state.inv, new_data], ignore_index=True)
            st.session_state.inv.to_csv(DATA_FILE, index=False)
            st.success("Service Added!")

# --- 3. New Billing ---
elif choice == "🧾 New Billing":
    if st.session_state.inv.empty:
        st.warning("Please add services first!")
    else:
        with st.form("bill_form"):
            cust = st.text_input("Customer Name")
            serv = st.selectbox("Select Service", st.session_state.inv["Service/Item"])
            
            # Service Charge & Tax Logic
            tax_rate = st.selectbox("GST/Tax %", [0, 5, 12, 18])
            discount = st.number_input("Discount (₹)", min_value=0.0)
            
            if st.form_submit_button("Generate Bill"):
                idx = st.session_state.inv.index[st.session_state.inv["Service/Item"] == serv][0]
                base_price = st.session_state.inv.at[idx, "Price"]
                
                tax_amt = (base_price * tax_rate) / 100
                total = base_price + tax_amt - discount
                
                new_sale = pd.DataFrame([[datetime.now().strftime("%d-%m-%y"), cust, serv, base_price, tax_amt, total]], 
                                        columns=st.session_state.sales.columns)
                
                st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
                st.session_state.sales.to_csv(SALES_FILE, index=False)
                
                # Update Stock
                st.session_state.inv.at[idx, "Stock"] -= 1
                st.session_state.inv.to_csv(DATA_FILE, index=False)
                
                st.balloons()
                st.success(f"Bill Created! Total: ₹{total}")

# --- 4. Records ---
elif choice == "📋 Records":
    st.subheader("Transaction History")
    st.dataframe(st.session_state.sales, use_container_width=True)
    # Download Button
    csv = st.session_state.sales.to_csv(index=False).encode('utf-8')
    st.download_button("Download Sales Report", csv, "SB_Online_Report.csv", "text/csv")
