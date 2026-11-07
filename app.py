import joblib
import pandas as pd
import streamlit as st

# Configure application metadata and layout
st.set_page_config(
    page_title="Customer Propensity Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS styling for executive dashboard metrics and status badges
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700; }
    .badge-high { background-color: #DEF7EC; color: #03543F; padding: 6px 14px; border-radius: 16px; font-weight: 600; display: inline-block; }
    .badge-low { background-color: #FEECDC; color: #9C4221; padding: 6px 14px; border-radius: 16px; font-weight: 600; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# 1. Load ML Pipeline Artifact
@st.cache_resource
def load_pipeline():
    return joblib.load('models/subscription_model_pipeline.pkl')

try:
    model = load_pipeline()
except Exception as err:
    st.error(f"Failed to load pipeline artifact: {err}")
    st.info("Verify 'subscription_model_pipeline.pkl' exists inside the 'models/' directory.")
    st.stop()

# Feature domain boundaries matching training dataset
KNOWN_ITEMS = [
    "Blouse", "Sweater", "Jeans", "Sandals", "Handbag", "Socks", "Dress",
    "Coat", "Shirt", "Shoes", "Skirt", "Sunglasses", "Pants", "Hat", "Jewelry",
    "Hoodie", "Belt", "Backpack", "Scarf", "Boots", "Shorts", "Gloves"
]

ALL_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
    "New Hampshire", "New Jersey", "New Mexico", "New York", 
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
    "West Virginia", "Wisconsin", "Wyoming"
]

# 2. Header Dashboard
st.title("🎯 Customer Subscription Propensity Scorecard")
st.caption("Predictive Analytics Platform for Retail Subscription Conversion")
st.divider()

# 3. Interactive Inputs
st.sidebar.header("Customer Profile")

# Preset scenario toggles for instant recruiter evaluation
preset = st.sidebar.radio("Test Scenario Presets", ["Default Profile", "High Loyalty Customer", "New Visitor"], horizontal=True)

if preset == "High Loyalty Customer":
    default_age, default_amount, default_prev, default_discount, default_freq = 38, 180.0, 25, "Yes", "Weekly"
elif preset == "New Visitor":
    default_age, default_amount, default_prev, default_discount, default_freq = 22, 35.0, 1, "No", "Annually"
else:
    default_age, default_amount, default_prev, default_discount, default_freq = 35, 65.0, 12, "Yes", "Monthly"

with st.sidebar.expander("Demographics & Identity", expanded=True):
    age = st.number_input("Age", min_value=18, max_value=100, value=default_age)
    gender = st.selectbox("Gender", ["Male", "Female"])
    location = st.selectbox("State / Location", options=ALL_STATES, index=16)

with st.sidebar.expander("Purchasing Behavior", expanded=True):
    category = st.selectbox("Product Category", ["Clothing", "Footwear", "Outerwear", "Accessories"])
    item_purchased = st.selectbox("Item Purchased", options=KNOWN_ITEMS, index=0)
    purchase_amount = st.number_input("Purchase Amount ($)", min_value=5.0, max_value=500.0, value=default_amount, step=5.0)
    previous_purchases = st.number_input("Prior Purchases Count", min_value=0, max_value=100, value=default_prev)
    frequency_of_purchases = st.selectbox("Purchase Frequency", ["Weekly", "Fortnightly", "Monthly", "Annually", "Bi-Weekly", "Quarterly", "Every 3 Months"], index=2)

with st.sidebar.expander("Order Attributes", expanded=False):
    size = st.selectbox("Size", ["S", "M", "L", "XL"])
    color = st.selectbox("Color", ["Gray", "Maroon", "Turquoise", "Black", "White"])
    season = st.selectbox("Season", ["Winter", "Spring", "Summer", "Fall"])
    review_rating = st.slider("Review Rating", min_value=1.0, max_value=5.0, value=4.2, step=0.1)
    shipping_type = st.selectbox("Shipping Method", ["Express", "Free Shipping", "Next Day Air", "Standard", "Store Pickup", "2-Day Shipping"])
    discount_applied = st.radio("Discount Applied?", ["Yes", "No"], index=0 if default_discount == "Yes" else 1)
    payment_method = st.selectbox("Payment Method", ["Venmo", "Cash", "Credit Card", "PayPal", "Debit Card"])

# Feature engineering transformations
freq_days_map = {
    "Weekly": 7, "Fortnightly": 14, "Bi-Weekly": 14,
    "Monthly": 30, "Quarterly": 90, "Every 3 Months": 90, "Annually": 365
}
purchase_frequency_days = freq_days_map.get(frequency_of_purchases, 30)

if age < 30:
    age_group = "Young Adult"
elif age < 45:
    age_group = "Adult"
elif age < 60:
    age_group = "Middle-aged"
else:
    age_group = "Senior"

# Construct feature DataFrame for inference
input_df = pd.DataFrame([{
    'age': age,
    'gender': gender,
    'item_purchased': item_purchased,
    'category': category,
    'purchase_amount': purchase_amount,
    'location': location,
    'size': size,
    'color': color,
    'season': season,
    'review_rating': review_rating,
    'shipping_type': shipping_type,
    'discount_applied': discount_applied,
    'previous_purchases': previous_purchases,
    'payment_method': payment_method,
    'frequency_of_purchases': frequency_of_purchases,
    'age_group': age_group,
    'purchase_frequency_days': purchase_frequency_days
}])

# 4. Perform Inference
prediction = model.predict(input_df)[0]
probability = model.predict_proba(input_df)[0][1]

# 5. Output Tabs
tab1, tab2, tab3 = st.tabs(["📊 Prediction Overview", "🔍 Raw Feature Payload", "⚙️ Model Details"])

with tab1:
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("Subscription Propensity Score")
        score_percentage = probability * 100
        
        st.metric(
            label="Conversion Probability",
            value=f"{score_percentage:.1f}%",
            delta=f"{(probability - 0.50)*100:+.1f}% vs 50% Threshold"
        )
        
        st.progress(float(probability))
        
        if prediction == 1:
            st.markdown('<div class="badge-high">🎯 High Propensity Subscriber</div>', unsafe_allow_html=True)
            st.markdown("""
            **Strategic Recommendation:**
            * Target with premium onboarding incentives (e.g., free express shipping).
            * Offer annual plan conversion discounts to increase Customer Lifetime Value (CLV).
            """)
        else:
            st.markdown('<div class="badge-low">⚠️ Low Propensity Customer</div>', unsafe_allow_html=True)
            st.markdown("""
            **Strategic Recommendation:**
            * Avoid costly subscription acquisition discounts.
            * Retain customer on standard transaction channels with seasonal promotions.
            """)

    with col_right:
        st.subheader("Key Input Drivers")
        m1, m2 = st.columns(2)
        m1.metric("Lifetime Orders", f"{previous_purchases}")
        m2.metric("Order Amount", f"${purchase_amount:.2f}")
        
        m3, m4 = st.columns(2)
        m3.metric("Purchase Cadence", f"{purchase_frequency_days} Days")
        m4.metric("Discount Active", f"{discount_applied}")

with tab2:
    st.subheader("Feature Vector Sent to Scikit-Learn Pipeline")
    st.dataframe(input_df, use_container_width=True)

with tab3:
    st.subheader("Pipeline Specifications")
    st.json({
        "Model Architecture": "Scikit-Learn Classification Pipeline",
        "Preprocessing Strategy": "ColumnTransformer (StandardScaler, OneHotEncoder)",
        "Feature Dimensions": len(input_df.columns),
        "Inference Artifact": "models/subscription_model_pipeline.pkl",
        "Target Variable": "Subscription Status (0 = Non-Subscriber, 1 = Subscriber)"
    })