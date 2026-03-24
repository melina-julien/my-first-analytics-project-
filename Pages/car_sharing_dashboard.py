import streamlit as st
import pandas as pd

# -----------------------------
# 1. LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# -----------------------------
# 2. MERGE DATASETS
# -----------------------------
trips_merged = trips.merge(cars, left_on="car_id", right_on="id")
trips_merged = trips_merged.merge(cities, left_on="city_id", right_on="city_id")

# IMPORTANT : renommer les colonnes dupliquées
trips_merged = trips_merged.rename(columns={
    "id_x": "trip_id",      # id du trajet
    "id_y": "car_id_real"   # id de la voiture
})

# -----------------------------
# 3. CLEAN USELESS COLUMNS
# -----------------------------
cols_to_drop = ["city_id", "id_customer"]
trips_merged = trips_merged.drop(columns=[c for c in cols_to_drop if c in trips_merged.columns])

# -----------------------------
# 4. FIX DATE FORMAT
# -----------------------------
trips_merged["pickup_date"] = pd.to_datetime(trips_merged["pickup_time"]).dt.date
trips_merged["dropoff_date"] = pd.to_datetime(trips_merged["dropoff_time"]).dt.date

# -----------------------------
# 5. SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

brands = trips_merged["brand"].unique()
selected_brands = st.sidebar.multiselect("Select Car Brand", brands)

if selected_brands:
    trips_merged = trips_merged[trips_merged["brand"].isin(selected_brands)]

# -----------------------------
# 6. BUSINESS METRICS
# -----------------------------
total_trips = len(trips_merged)
total_distance = trips_merged["distance"].sum()

top_car = (
    trips_merged.groupby("model")["revenue"]
    .sum()
    .idxmax()
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Trips", total_trips)

with col2:
    st.metric("Top Car Model by Revenue", top_car)

with col3:
    st.metric("Total Distance (km)", f"{total_distance:,.2f}")

# -----------------------------
# 7. DATA PREVIEW
# -----------------------------
st.subheader("Preview of Merged Trips Data")
st.write(trips_merged.head())

# -----------------------------
# 8. VISUALIZATIONS
# -----------------------------

# Trips Over Time
st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date")["trip_id"].count()
st.line_chart(trips_over_time)

# Revenue per Car Model
st.subheader("Revenue per Car Model")
revenue_per_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_per_model)

# Revenue Over Time
st.subheader("Revenue Over Time")
revenue_time = trips_merged.groupby("pickup_date")["revenue"].sum()
st.area_chart(revenue_time)