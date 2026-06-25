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

# --- সুন্দর ডিজাইনের জন্য কাস্টম CSS ---
st.set_page_config(page_title="আরিয়ান টেলিকম", layout="wide")

st.markdown("""
    <style>
    /* ব্যাকগ্রাউন্ড ও টেক্সট কালার */
    .main { background-color: #121212; color: #FFFFFF; }
    .sidebar .sidebar-content { background-color: #1E1E1E; }
    
    /* শিরোনাম বা টাইটেল ডিজাইন */
    .main-title {
        font-family: 'SolaimanLipi', sans-serif;
        color: #FFB300;
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #B0BEC5;
        font-size: 18px;
        margin-bottom: 30px;
    }
    
    /* কার্ড ডিজাইন (লাভ-ক্ষতির জন্য) */
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFB300;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    /* বাটনের সুন্দর ডিজাইন */
    div.stButton > button:first-child {
        background-color: #FFB300;
        color: #121212;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #FFA000;
        color: #000000;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)
# অ্যাপের মূল হেডার (ছবিসহ)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)

st.markdown('<div class="main-title">🔌 আরিয়ান টেলিকম</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">দোকানের মালামাল বাকী দেওয়া সম্পূর্ন নিষেধ</div>', unsafe_allow_html=True)
st.write("---")
df = load_data()

# সাইডবার ডিজাইন
st.sidebar.markdown("<h2 style='color: #FFB300;'>📋 মেনু অপশন</h2>", unsafe_allow_html=True)
choice = st.sidebar.radio("কী করতে চান বাছাই করুন:", ["📦 বর্তমান স্টক দেখুন", "➕ নতুন মালামাল যোগ করুন", "🛒 পণ্য বিক্রি করুন", "📊 লাভ-ক্ষতির হিসাব"])

# --- ১. স্টক দেখুন ---
if choice == "📦 বর্তমান স্টক দেখুন":
    st.markdown("### 📊 বর্তমান স্টক তালিকা")
    if df.empty:
        st.warning("দোকানে এখনও কোনো মালামাল যোগ করা হয়নি। বামদিকের মেনু থেকে যোগ করুন।")
    else:
    # টেবিলটি সুন্দর করে দেখানোর জন্য
        df.style.background_gradient(cmap='YlOrRd', subset=["স্টক (পরিমাণ)"]), 
        use_container_width=True
# --- ২. নতুন মালামাল যোগ করুন ---
elif choice == "➕ নতুন মালামাল যোগ করুন":
    st.markdown("### 📥 নতুন মালামাল এন্ট্রি ফরম")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("পণ্যের নাম (যেমন: Charger, Battery, LED Light):")
            buy_price = st.number_input("ক্রয় মূল্য (প্রতি পিস ৳):", min_value=0.0, step=1.0)
        with col2:
            sell_price = st.number_input("বিক্রয় মূল্য (প্রতি পিস ৳):", min_value=0.0, step=1.0)
            quantity = st.number_input("পরিমাণ (কয়টি স্টকে আনলেন):", min_value=1, step=1)
        
        submitted = st.form_submit_button("💾 স্টকে নিশ্চিত যোগ করুন")
        
        if submitted:
            if p_name:
                if p_name in df["পণ্যের নাম"].values:
                    df.loc[df["পণ্যের নাম"] == p_name, "স্টক (পরিমাণ)"] += quantity
                else:
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
                st.error("⚠️ দয়া করে পণ্যের নাম সঠিকভাবে লিখুন।")

# --- ৩. পণ্য বিক্রি করুন ---
elif choice == "🛒 পণ্য বিক্রি করুন":
    st.markdown("### 💸 নতুন বিক্রয় এন্ট্রি")
    if df.empty:
        st.warning("বিক্রি করার মতো কোনো পণ্য স্টকে নেই। আগে নতুন মালামাল যোগ করুন।")
    else:
        available_products = df[df["স্টক (পরিমাণ)"] > 0]["পণ্যের নাম"].tolist()
        if not available_products:
            st.error("⚠️ দুঃখিত, দোকানের সব পণ্যের স্টক শেষ!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                p_to_sell = st.selectbox("কোন পণ্যটি বিক্রি হলো?", available_products)
                current_stock = df.loc[df["পণ্যের নাম"] == p_to_sell, "স্টক (পরিমাণ)"].values[0]
                st.info(f"💡 এই পণ্যটি বর্তমানে স্টকে আছে: {current_stock} টি")
            with col2:
                sell_qty = st.number_input("কয়টি বিক্রি করলেন?", min_value=1, max_value=int(current_stock), step=1)
            
            if st.button("🛍️ বিক্রি নিশ্চিত করুন"):
                df.loc[df["পণ্যের নাম"] == p_to_sell, "স্টক (পরিমাণ)"] -= sell_qty
                df.loc[df["পণ্যের নাম"] == p_to_sell, "মোট বিক্রি (পরিমাণ)"] += sell_qty
                save_data(df)
                st.success(f"✅ {p_to_sell} - {sell_qty}টি বিক্রি সফলভাবে নথিভুক্ত হয়েছে!")

# --- ৪. লাভ-ক্ষতির হিসাব ---
elif choice == "📊 লাভ-ক্ষতির হিসাব":
    st.markdown("### 📈 দোকান ও বেচাকেনার আর্থিক হিসাব")
    
    if df.empty or df["মোট বিক্রি (পরিমাণ)"].sum() == 0:
        st.info("এখনও কোনো পণ্য বিক্রি হয়নি। বিক্রি শুরু হলে এখানে হিসাব দেখতে পাবেন।")
    else:
        df["মোট বিক্রয় মূল্য"] = df["মোট বিক্রি (পরিমাণ)"] * df["বিক্রয় মূল্য (টাকা)"]
        df["মোট ক্রয় মূল্য"] = df["মোট বিক্রি (পরিমাণ)"] * df["ক্রয় মূল্য (টাকা)"]
        df["লাভ"] = df["মোট বিক্রয় মূল্য"] - df["মোট ক্রয় মূল্য"]
        
        total_sales = df["মোট বিক্রয় মূল্য"].sum()
        total_profit = df["লাভ"].sum()
        
        # সুন্দর কার্ড আকারে ডিসপ্লে
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #B0BEC5; margin: 0; font-size: 16px;">💰 মোট বিক্রি</p>
                <h2 style="color: #FFB300; margin: 5px 0 0 0;">{total_sales:,.2f} ৳</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 5px solid #00E676;">
                <p style="color: #B0BEC5; margin: 0; font-size: 16px;">📈 মোট নিট লাভ</p>
                <h2 style="color: #00E676; margin: 5px 0 0 0;">{total_profit:,.2f} ৳</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("<br>", unsafe_allow_html=True)
        st.write("#### 📋 পণ্যভিত্তিক বিক্রয়ের বিস্তারিত বিবরণ:")
        st.dataframe(df[["পণ্যের নাম", "মোট বিক্রি (পরিমাণ)", "মোট বিক্রয় মূল্য", "লাভ"]], use_container_width=True)
