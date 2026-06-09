import streamlit as st
import pandas as pd
import os

# ডাটাবেজ ফাইল সেটআপ
DATA_FILE = "dokan_inventory.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["পণ্যের নাম", "ক্রয় মূল্য (টাকা)", "বিক্রয় মূল্য (টাকা)", "স্টক (পরিমাণ)", "মোট বিক্রি (পরিমাণ)"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# অ্যাপের মূল ডিজাইন
st.title("🔌 ভাই ভাই ইলেকট্রনিক্স - হিসাব ব্যবস্থাপক")
st.write("আপনার দোকানের মালামাল এবং বেচাকেনার সহজ হিসাব।")
st.sidebar.header("মেনু অপশন")

df = load_data()
choice = st.sidebar.selectbox("কী করতে চান বাছাই করুন:", ["স্টক দেখুন", "নতুন মালামাল যোগ করুন", "পণ্য বিক্রি করুন", "লাভ-ক্ষতির হিসাব"])

# --- ১. স্টক দেখুন ---
if choice == "স্টক দেখুন":
    st.header("📦 বর্তমান স্টক তালিকা")
    if df.empty:
        st.warning("দোকানে এখনও কোনো মালামাল যোগ করা হয়নি।")
    else:
        st.dataframe(df, use_container_width=True)

# --- ২. নতুন মালামাল যোগ করুন ---
elif choice == "নতুন মালামাল যোগ করুন":
    st.header("➕ নতুন মালামাল এন্ট্রি করুন")
    
    with st.form("add_form", clear_on_submit=True):
        p_name = st.text_input("পণ্যের নাম (যেমন: LED Bulb, Switch, Wire):")
        buy_price = st.number_input("ক্রয় মূল্য (প্রতি পিস):", min_value=0.0, step=1.0)
        sell_price = st.number_input("বিক্রয় মূল্য (প্রতি পিস):", min_value=0.0, step=1.0)
        quantity = st.number_input("পরিমাণ (কয়টি এনেছেন):", min_value=1, step=1)
        
        submitted = st.form_submit_button("স্টকে যোগ করুন")
        
        if submitted:
            if p_name:
                if p_name in df["পণ্যের নাম"].values:
                    # পণ্য আগে থেকেই থাকলে স্টক বাড়িয়ে দেবে
                    df.loc[df["পণ্যের নাম"] == p_name, "স্টক (পরিমাণ)"] += quantity
                else:
                    # নতুন পণ্য যোগ করবে
                    new_row = {
                        "পণ্যের নাম": p_name, 
                        "ক্রয় মূল্য (টাকা)": buy_price, 
                        "বিক্রয় মূল্য (টাকা)": sell_price, 
                        "স্টক (পরিমাণ)": quantity, 
                        "মোট বিক্রি (পরিমাণ)": 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                save_data(df)
                st.success(f"🎉 {p_name} সফলভাবে স্টকে যোগ হয়েছে!")
            else:
                st.error("দয়া করে পণ্যের নাম লিখুন।")

# --- ৩. পণ্য বিক্রি করুন ---
elif choice == "পণ্য বিক্রি করুন":
    st.header("🛒 পণ্য বিক্রয় এন্ট্রি")
    if df.empty:
        st.warning("বিক্রি করার মতো কোনো পণ্য স্টকে নেই। আগে পণ্য যোগ করুন।")
    else:
        available_products = df[df["স্টক (পরিমাণ)"] > 0]["পণ্যের নাম"].tolist()
        if not available_products:
            st.error("⚠️ দুঃখিত, সব পণ্যের স্টক শেষ!")
        else:
            p_to_sell = st.selectbox("কোন পণ্যটি বিক্রি হয়েছে?", available_products)
            current_stock = df.loc[df["পণ্যের নাম"] == p_to_sell, "স্টক (পরিমাণ)"].values[0]
            
            st.info(f"বর্তমানে এই পণ্যটি স্টকে আছে: {current_stock} টি")
            sell_qty = st.number_input("কয়টি বিক্রি করলেন?", min_value=1, max_value=int(current_stock), step=1)
            
            if st.button("বিক্রি নিশ্চিত করুন"):
                # স্টক কমানো এবং বিক্রি বাড়ানো
                df.loc[df["পণ্যের নাম"] == p_to_sell, "স্টক (পরিমাণ)"] -= sell_qty
                df.loc[df["পণ্যের নাম"] == p_to_sell, "মোট বিক্রি (পরিমাণ)"] += sell_qty
                save_data(df)
                st.success(f"✅ {p_to_sell} - {sell_qty}টি বিক্রি নথিভুক্ত হয়েছে!")

# --- ৪. লাভ-ক্ষতির হিসাব ---
elif choice == "লাভ-ক্ষতির হিসাব":
    st.header("📊 বেচাকেনা ও লাভের হিসাব")
    
    if df.empty or df["মোট বিক্রি (পরিমাণ)"].sum() == 0:
        st.info("এখনও কোনো পণ্য বিক্রি হয়নি। বিক্রি হলে এখানে হিসাব দেখাবে।")
    else:
        # হিসাব নিকাশ
        df["মোট বিক্রয় মূল্য"] = df["মোট বিক্রি (পরিমাণ)"] * df["বিক্রয় মূল্য (টাকা)"]
        df["মোট ক্রয় মূল্য"] = df["মোট বিক্রি (পরিমাণ)"] * df["ক্রয় মূল্য (টাকা)"]
        df["লাভ"] = df["মোট বিক্রয় মূল্য"] - df["মোট ক্রয় মূল্য"]
        
        total_sales = df["মোট বিক্রয় মূল্য"].sum()
        total_profit = df["লাভ"].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💰 মোট বিক্রি (টাকা)", value=f"{total_sales:,.2f} ৳")
        with col2:
            st.metric(label="📈 মোট লাভ (টাকা)", value=f"{total_profit:,.2f} ৳", delta=f"{total_profit:,.2f} ৳")
            
        st.write("### পণ্যভিত্তিক বিক্রয়ের বিবরণ:")
        st.dataframe(df[["পণ্যের নাম", "মোট বিক্রি (পরিমাণ)", "মোট বিক্রয় মূল্য", "লাভ"]], use_container_width=True)
