import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Styling ---
sns.set_style("whitegrid")
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

# Tinder palette
tinder_palette = ['#FD5068', '#FDCB58', '#A0D8B3']

pd.set_option('display.max_columns', None)
df = pd.read_csv("tinder_swipe_data.csv")

# Timestamp and hour extraction
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()

# Gender vs swipe direction
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='swipe_direction', hue='gender', palette=tinder_palette, hue_order=['Male', 'Female', 'Other'])
plt.title('Swipe Direction by Gender')
plt.tight_layout()
plt.show()

# Age group vs swipe behavior
age_bins = [18, 24, 30, 36, 45, 60]
age_labels = ['18-24', '25-30', '31-36', '37-45', '46+']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='age_group', hue='swipe_direction', palette=tinder_palette, hue_order=['Left', 'Right', 'Superlike'])
plt.title('Swipe Direction by Age Group')
plt.tight_layout()
plt.show()

# Swipe match rate by gender
plt.figure(figsize=(9, 5))
sns.countplot(data=df[df['match'] == 'Yes'], x='gender', palette=tinder_palette)
plt.title('Swipe Match Count by Gender')
plt.tight_layout()
plt.show()

# App open frequency analysis
plt.figure(figsize=(9, 5))
sns.histplot(data=df, x='app_opens_today', bins=10, kde=True, color='#FFABAB')
plt.title('App Opens Today Distribution')
plt.tight_layout()
plt.show()

# Swipe timing patterns
plt.figure(figsize=(9, 5))
sns.histplot(data=df, x='hour', bins=24, kde=True, color='#81B29A')
plt.title('Swipes by Hour of Day')
plt.tight_layout()
plt.show()

# Repeat swipers
df['user_type'] = df['app_opens_today'].apply(lambda x: 'Frequent' if x > 5 else 'Occasional')
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='swipe_direction', hue='user_type', palette=tinder_palette)
plt.title('Swipe Direction by User Type')
plt.tight_layout()
plt.show()

# Conversion rate by age group
age_swipe = df.groupby('age_group')['swipe_direction'].value_counts().unstack().fillna(0)
age_swipe['conversion_rate'] = age_swipe['Right'] / age_swipe.sum(axis=1)
plt.figure(figsize=(9, 5))
sns.barplot(x=age_swipe.index, y=age_swipe['conversion_rate'], color='#FDCB58')
plt.title('Conversion Rate by Age Group')
plt.ylim(0, 1)
plt.tight_layout()
plt.show()

# Conversion rate by subscription
subscription_swipe = df.pivot_table(index='subscription', columns='swipe_direction', aggfunc='size', fill_value=0)
subscription_swipe['conversion_rate'] = subscription_swipe['Right'] / subscription_swipe.sum(axis=1)
subscription_swipe = subscription_swipe.reset_index()
plt.figure(figsize=(9, 5))
sns.barplot(data=subscription_swipe, x='subscription', y='conversion_rate', palette=tinder_palette)
plt.title('Conversion Rate by Subscription Type')
plt.tight_layout()
plt.show()

# Match count by subscription
matched_df = df[df['match'] == 'Yes']
plt.figure(figsize=(9, 5))
sns.countplot(data=matched_df, x='subscription', palette=tinder_palette)
plt.title('Match Count by Subscription Type')
plt.tight_layout()
plt.show()

# Repeat right swipers
user_swipe_summary = df.groupby('user_id')['swipe_direction'].value_counts().unstack().fillna(0)
user_swipe_summary['right_ratio'] = user_swipe_summary['Right'] / user_swipe_summary.sum(axis=1)
plt.figure(figsize=(9, 5))
sns.histplot(user_swipe_summary['right_ratio'], bins=20, kde=True, color='#FF7158')
plt.title('Distribution of Right Swipe Ratio per User')
plt.tight_layout()
plt.show()

# Day vs Night Swipe Pattern
df['day_period'] = df['hour'].apply(lambda x: 'Day' if 6 <= x < 18 else 'Night')
right_swipes = df[df['swipe_direction'] == 'Right']
day_night_counts = right_swipes['day_period'].value_counts()
plt.figure(figsize=(7, 4))
sns.barplot(x=day_night_counts.index, y=day_night_counts.values, palette=['#81D4FA', '#4DB6AC'])
plt.title('Right Swipes: Day vs Night')
plt.tight_layout()
plt.show()

# Heatmap of swipes by day and hour
heatmap_data = df.pivot_table(index='day_of_week', columns='hour', values='user_id', aggfunc='count').fillna(0)
ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = heatmap_data.reindex(ordered_days)
plt.figure(figsize=(14, 6))
sns.heatmap(heatmap_data, cmap='YlGnBu')
plt.title('Swipe Activity by Day of Week and Hour')
plt.tight_layout()
plt.show()

# Retention proxy (App opens)
max_opens = df['app_opens_today'].dropna().max()
last_bin = max(11, max_opens + 1)
app_bins = [0, 1, 3, 5, 10, last_bin]
app_labels = ['0', '1-2', '3-4', '5-9', '10+']
df['app_open_group'] = pd.cut(df['app_opens_today'], bins=app_bins, labels=app_labels, right=False)
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x='app_open_group', palette=tinder_palette)
plt.title('User Distribution by App Open Frequency')
plt.tight_layout()
plt.show()



























































































