import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

# Set page layout
st.set_page_config(layout="wide", page_title="🔥 Tinder Swipe Dashboard")
sns.set_style("whitegrid")

# Load data
df = pd.read_csv("tinder_swipe_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()
df['day_period'] = df['hour'].apply(lambda x: 'Day' if 6 <= x < 18 else 'Night')
df['user_type'] = df['app_opens_today'].apply(lambda x: 'Frequent' if x > 5 else 'Occasional')

# Age groups
age_bins = [18, 24, 30, 36, 45, 60]
age_labels = ['18-24', '25-30', '31-36', '37-45', '46+']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)

# App open groups
last_bin = max(11, df['app_opens_today'].dropna().max() + 1)
app_bins = [0, 1, 3, 5, 10, last_bin]
app_labels = ['0', '1-2', '3-4', '5-9', '10+']
df['app_open_group'] = pd.cut(df['app_opens_today'], bins=app_bins, labels=app_labels, right=False)

# Tinder-like colors
tinder_palette = ['#FD5068', '#FDCB58', '#A0D8B3']

# Sidebar Filters
st.sidebar.header("🔍 Filters")
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()

selected_gender = st.sidebar.multiselect("Gender", df['gender'].unique())
selected_age = st.sidebar.multiselect("Age Group", df['age_group'].dropna().unique())
selected_sub = st.sidebar.multiselect("Subscription", df['subscription'].dropna().unique())
selected_range = st.sidebar.date_input("Date Range", [min_date, max_date])

search_clicked = st.sidebar.button("🔎 Search")
reset_clicked = st.sidebar.button("🔄 Reset")

# Apply filters only if Search is clicked
if reset_clicked:
    filtered = df.copy()
    selected_gender = []
    selected_age = []
    selected_sub = []
    selected_range = [min_date, max_date]
elif search_clicked:
    filtered = df[
        (df['gender'].isin(selected_gender) if selected_gender else True) &
        (df['age_group'].isin(selected_age) if selected_age else True) &
        (df['subscription'].isin(selected_sub) if selected_sub else True) &
        (df['timestamp'].dt.date.between(*selected_range))
    ]
else:
    filtered = df.copy()

# KPIs
st.title("🔥 Tinder Swipe Behavior Dashboard")
st.caption("Quick insights into user activity and swiping patterns.")

st.markdown("""
<div style="border:1px solid red; padding:10px; border-radius:5px;">
    ⚠️ <strong>Disclaimer:</strong> This dashboard uses <em>synthetic demo data</em> for educational and portfolio purposes only.
    It does <strong>not</strong> contain or reflect any real Tinder user data.
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Swipes", len(filtered))
col2.metric("Match Rate", f"{(filtered['match'] == 'Yes').mean():.2%}")
col3.metric("Right Swipe %", f"{(filtered['swipe_direction'] == 'Right').mean():.2%}")
col4.metric("Active Users", filtered['user_id'].nunique())

tabs = st.tabs(["Overview", "Conversions", "Time Trends", "Retention"])

with tabs[0]:
    st.subheader("Swipe Direction by Gender")
    st.caption("Shows how often each gender swipes left, right, or superlike.")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=filtered, x='swipe_direction', hue='gender',
                  hue_order=['Male', 'Female', 'Other'], palette=tinder_palette, ax=ax)
    st.pyplot(fig)

    st.subheader("Swipe Direction by Age Group")
    st.caption("Tracks how users of different age ranges interact.")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=filtered, x='age_group', hue='swipe_direction',
                  hue_order=['Left', 'Right', 'Superlike'], palette=tinder_palette, ax=ax)
    st.pyplot(fig)

    st.subheader("Match Count by Gender")
    st.caption("Who is getting the most matches?")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=filtered[filtered['match'] == 'Yes'], x='gender', palette=tinder_palette, ax=ax)
    st.pyplot(fig)

with tabs[1]:
    st.subheader("Right Swipe Conversion by Age")
    st.caption("Right swipes as % of total swipes in each age group.")
    age_swipe = filtered.groupby('age_group')['swipe_direction'].value_counts().unstack().fillna(0)
    age_swipe['conversion'] = age_swipe.get('Right', 0) / age_swipe.sum(axis=1)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=age_swipe.index, y=age_swipe['conversion'], color='#FDCB58', ax=ax)
    ax.set_ylim(0, 1)
    st.pyplot(fig)

    st.subheader("Conversion Rate by Subscription")
    st.caption("How do paid tiers affect swipe success?")
    sub_swipe = filtered.pivot_table(index='subscription', columns='swipe_direction', aggfunc='size', fill_value=0)
    sub_swipe['conversion'] = sub_swipe.get('Right', 0) / sub_swipe.sum(axis=1)
    sub_swipe = sub_swipe.reset_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=sub_swipe, x='subscription', y='conversion', palette=tinder_palette, ax=ax)
    st.pyplot(fig)

with tabs[2]:
    st.subheader("App Opens Today Distribution")
    st.caption("Frequency of daily app opens by users.")
    kde_toggle = st.checkbox("Show KDE Curve", value=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(data=filtered, x='app_opens_today', bins=10, kde=kde_toggle, color='#FFABAB', ax=ax)
    st.pyplot(fig)

    st.subheader("Swipes by Hour of Day")
    st.caption("Hourly swipe activity to find peak engagement times.")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(data=filtered, x='hour', bins=24, kde=True, color='#81B29A', ax=ax)
    st.pyplot(fig)

    st.subheader("Right Swipes: Day vs Night")
    st.caption("Are people more right-swipe happy at night?")
    right_swipes = filtered[filtered['swipe_direction'] == 'Right']
    day_night_counts = right_swipes['day_period'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(x=day_night_counts.index, y=day_night_counts.values,
                palette=['#81D4FA', '#4DB6AC'], ax=ax)
    st.pyplot(fig)

    st.subheader("Swipe Activity Heatmap")
    st.caption("Swipe patterns across week and time of day.")
    heatmap_data = filtered.pivot_table(index='day_of_week', columns='hour',
                                        values='user_id', aggfunc='count').fillna(0)
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(ordered_days)
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(heatmap_data, cmap='YlGnBu', ax=ax)
    st.pyplot(fig)

with tabs[3]:
    st.subheader("Swipe Direction by User Type")
    st.caption("Frequent users vs occasional swipers.")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=filtered, x='swipe_direction', hue='user_type', palette=tinder_palette, ax=ax)
    st.pyplot(fig)

    st.subheader("Match Count by Subscription")
    st.caption("Total matches across subscription tiers.")
    matched_df = filtered[filtered['match'] == 'Yes']
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=matched_df, x='subscription', palette=tinder_palette, ax=ax)
    st.pyplot(fig)

    st.subheader("Right Swipe Ratio Distribution")
    st.caption("How many users swipe right over 90% of the time?")
    user_summary = filtered.groupby('user_id')['swipe_direction'].value_counts().unstack().fillna(0)
    user_summary['right_ratio'] = user_summary.get('Right', 0) / user_summary.sum(axis=1)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(user_summary['right_ratio'], bins=20, kde=True, color='#FF7158', ax=ax)
    st.pyplot(fig)

    st.subheader("Retention Proxy by App Opens")
    st.caption("Groups users by how often they open the app.")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(data=filtered, x='app_open_group', palette=tinder_palette, ax=ax)
    st.pyplot(fig)

st.markdown("---")
st.markdown("*© 2025 | Dashboard for demo & learning purposes only | Data is synthetic*")
