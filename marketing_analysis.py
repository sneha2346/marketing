import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# 1. Load Data
df = pd.read_csv('marketing_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

# 2. Calculate Metrics
campaign_agg = df.groupby(['Campaign_ID', 'Campaign_Name', 'Channel']).agg({
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum',
    'Cost/Ad Spend': 'sum',
    'Revenue Generated': 'sum',
    'Customer Acquired': 'sum'
}).reset_index()

campaign_agg['CTR'] = campaign_agg['Clicks'] / campaign_agg['Impressions']
campaign_agg['CR'] = campaign_agg['Conversions'] / campaign_agg['Clicks']
campaign_agg['CPC'] = campaign_agg['Cost/Ad Spend'] / campaign_agg['Clicks']
campaign_agg['CAC'] = campaign_agg['Cost/Ad Spend'] / campaign_agg['Customer Acquired']
campaign_agg['ROI'] = (campaign_agg['Revenue Generated'] - campaign_agg['Cost/Ad Spend']) / campaign_agg['Cost/Ad Spend']
campaign_agg['ROAS'] = campaign_agg['Revenue Generated'] / campaign_agg['Cost/Ad Spend']

campaign_agg.replace([np.inf, -np.inf], np.nan, inplace=True)
campaign_agg.fillna(0, inplace=True)

# 3. Campaign Performance Analysis
sorted_campaigns = campaign_agg.sort_values(by='ROI', ascending=False)

plt.figure(figsize=(12, 6))
sns.barplot(data=sorted_campaigns, x='Campaign_ID', y='ROI', palette='viridis')
plt.title('ROI by Campaign', fontsize=16)
plt.xticks(rotation=45)
plt.axhline(0, color='red', linestyle='--')
plt.tight_layout()
plt.savefig('roi_by_campaign.png')

# 4. Channel-Level Insights
channel_agg = df.groupby('Channel').agg({
    'Cost/Ad Spend': 'sum',
    'Revenue Generated': 'sum',
    'Customer Acquired': 'sum',
    'Conversions': 'sum',
    'Clicks': 'sum'
}).reset_index()

channel_agg['CAC'] = channel_agg['Cost/Ad Spend'] / channel_agg['Customer Acquired']
channel_agg['ROI'] = (channel_agg['Revenue Generated'] - channel_agg['Cost/Ad Spend']) / channel_agg['Cost/Ad Spend']
channel_agg['CR'] = channel_agg['Conversions'] / channel_agg['Clicks']

channel_agg_sorted = channel_agg.sort_values(by='CAC')

plt.figure(figsize=(10, 6))
sns.barplot(data=channel_agg_sorted, x='Channel', y='CAC', palette='rocket')
plt.title('Customer Acquisition Cost (CAC) by Channel', fontsize=16)
plt.tight_layout()
plt.savefig('cac_by_channel.png')

# 5. Visualizing the Conversion Funnel, Revenue vs Cost, and Time Trends
plt.figure(figsize=(10, 6))
sns.scatterplot(data=campaign_agg, x='Cost/Ad Spend', y='Revenue Generated', 
                size='Conversions', sizes=(50, 500), hue='Channel', alpha=0.7)
max_val = min(campaign_agg['Cost/Ad Spend'].max(), campaign_agg['Revenue Generated'].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='Break Even')
plt.title('Revenue vs Cost by Campaign')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('revenue_vs_cost.png')

df['Month'] = df['Date'].dt.to_period('M')
monthly_trends = df.groupby('Month').agg({'Revenue Generated': 'sum', 'Cost/Ad Spend': 'sum'}).reset_index()
monthly_trends['Month'] = monthly_trends['Month'].astype(str)

plt.figure(figsize=(12, 6))
plt.plot(monthly_trends['Month'], monthly_trends['Revenue Generated'], marker='o', label='Revenue', color='green')
plt.plot(monthly_trends['Month'], monthly_trends['Cost/Ad Spend'], marker='x', label='Cost', color='red')
plt.title('Monthly Revenue vs Ad Spend Trends', fontsize=16)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('time_trends.png')

# 6. Advanced Analytics: Clustering & Regression
features = ['ROI', 'CAC', 'ROAS']
X = campaign_agg[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42)
campaign_agg['Performance_Cluster'] = kmeans.fit_predict(X_scaled)

plt.figure(figsize=(10, 6))
sns.scatterplot(data=campaign_agg, x='CAC', y='ROI', hue='Performance_Cluster', s=100, palette='Set1')
plt.title('Campaign Segmentation (K-Means)')
plt.axhline(0, color='black', linestyle='--')
plt.tight_layout()
plt.savefig('clusters.png')

X_reg = campaign_agg[['CTR', 'CR', 'CPC']]
y_reg = campaign_agg['ROI']

reg = LinearRegression()
reg.fit(X_reg, y_reg)
y_pred = reg.predict(X_reg)

campaign_agg['Predicted_ROI'] = y_pred

# 7. Decision & Recommendation Engine
def recommendation(row):
    if row['ROI'] < 0:
        return 'STOP ❌'
    elif row['ROI'] > 0.5 and row['CAC'] < campaign_agg['CAC'].median():
        return 'SCALE UP ✅'
    else:
        return 'OPTIMIZE ⚙️'

campaign_agg['Recommendation'] = campaign_agg.apply(recommendation, axis=1)

# 8. Summary Report Output
scale_up = campaign_agg[campaign_agg['Recommendation'] == 'SCALE UP ✅']['Campaign_Name'].tolist()
stop = campaign_agg[campaign_agg['Recommendation'] == 'STOP ❌']['Campaign_Name'].tolist()
optimize = campaign_agg[campaign_agg['Recommendation'] == 'OPTIMIZE ⚙️']['Campaign_Name'].tolist()

report = f"""# Final Summary Report: Marketing Campaign Performance

## 📊 Overview
Analyzed {len(df)} records spanning {len(campaign_agg)} marketing campaigns across {len(channel_agg)} channels.

## 🏆 Top Performing Channels
Based on CAC and ROI, the most efficient channels are:

{channel_agg_sorted.head(3)[['Channel', 'CAC', 'ROI', 'CR']].to_markdown(index=False)}

## 📉 Worst Performing Channels
{channel_agg_sorted.tail(3)[['Channel', 'CAC', 'ROI', 'CR']].to_markdown(index=False)}

---

## 🧾 Expected Output Summary

### ✅ Campaigns to scale up
*(High ROI + Low CAC + Strong Conversion)*
{', '.join(scale_up) if scale_up else 'None identified'}

### ❌ Campaigns to stop 
*(Negative ROI / High CAC)*
{', '.join(stop) if stop else 'None identified'}

### ⚙️ Campaigns to optimize
*(Moderate Returns, High traffic but low conversion rate)*
{', '.join(optimize) if optimize else 'None identified'}

## 💰 Suggested Budget Distribution
- **Reallocate 100%** of the budget from 'STOP' campaigns.
- **Direct 70%** of freed budget towards 'SCALE UP' campaigns to maximize returns.
- **Allocate 30%** of freed budget to A/B test and refine 'OPTIMIZE' campaigns to improve Conversion Rates.
"""

with open('summary_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("Analysis complete. Check PNG files and summary_report.md")
