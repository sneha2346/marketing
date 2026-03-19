import json
import os

def generate_notebook():
    notebook = {
     "cells": [],
     "metadata": {
      "kernelspec": {
       "display_name": "Python 3",
       "language": "python",
       "name": "python3"
      },
      "language_info": {
       "name": "python",
       "version": "3.9"
      }
     },
     "nbformat": 4,
     "nbformat_minor": 4
    }

    def add_markdown(text):
        # Handle array of strings as required by Jupyter
        lines = [line + '\n' for line in text.strip().split('\n')]
        if lines:
            lines[-1] = lines[-1].strip('\n') # Remove trailing newline from last line
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": lines
        })

    def add_code(text):
        lines = [line + '\n' for line in text.strip().split('\n')]
        if lines:
            lines[-1] = lines[-1].strip('\n')
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines
        })

    # --- MARKDOWN AND CODE CELLS ---
    
    add_markdown('''# Marketing Campaign Performance and ROI Optimization
## Objective
Analyze marketing campaign data to evaluate performance, calculate ROI, CAC, and other key metrics, and provide actionable recommendations on budget allocation.
''')

    add_code('''# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
''')

    add_markdown('''## 1. Load Data''')
    add_code('''# Load the generated marketing data
df = pd.read_csv('marketing_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
print(f"Dataset Shape: {df.shape}")
df.head()''')

    add_markdown('''## 2. Calculate Key Metrics
We will calculate:
- **CTR (Click Through Rate)** = Clicks / Impressions
- **Conversion Rate (CR)** = Conversions / Clicks
- **CPC (Cost per Click)** = Cost / Clicks
- **CAC (Customer Acquisition Cost)** = Cost / Customers Acquired
- **ROI (Return on Investment)** = (Revenue - Cost) / Cost
- **ROAS (Return on Ad Spend)** = Revenue / Cost
''')

    add_code('''# Aggregate data by Campaign
campaign_agg = df.groupby(['Campaign_ID', 'Campaign_Name', 'Channel']).agg({
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum',
    'Cost/Ad Spend': 'sum',
    'Revenue Generated': 'sum',
    'Customer Acquired': 'sum'
}).reset_index()

# Calculate Metrics
campaign_agg['CTR'] = campaign_agg['Clicks'] / campaign_agg['Impressions']
campaign_agg['CR'] = campaign_agg['Conversions'] / campaign_agg['Clicks']
campaign_agg['CPC'] = campaign_agg['Cost/Ad Spend'] / campaign_agg['Clicks']
campaign_agg['CAC'] = campaign_agg['Cost/Ad Spend'] / campaign_agg['Customer Acquired']
campaign_agg['ROI'] = (campaign_agg['Revenue Generated'] - campaign_agg['Cost/Ad Spend']) / campaign_agg['Cost/Ad Spend']
campaign_agg['ROAS'] = campaign_agg['Revenue Generated'] / campaign_agg['Cost/Ad Spend']

# Replace infinities/NAs if any
campaign_agg.replace([np.inf, -np.inf], np.nan, inplace=True)
campaign_agg.fillna(0, inplace=True)

print("Aggregated Campaign Metrics Preview:")
campaign_agg[['Campaign_ID', 'Channel', 'ROI', 'CAC', 'ROAS']].head()''')

    add_markdown('''## 3. Campaign Performance Analysis
Identify the Top 5 and Bottom 5 campaigns based on ROI.''')

    add_code('''# Sort by ROI
sorted_campaigns = campaign_agg.sort_values(by='ROI', ascending=False)
top_5 = sorted_campaigns.head(5)
bottom_5 = sorted_campaigns.tail(5)

print("🌟 Top 5 Campaigns by ROI:")
display(top_5[['Campaign_Name', 'Channel', 'ROI', 'CAC', 'ROAS', 'Revenue Generated', 'Cost/Ad Spend']])

print("\\n⚠️ Bottom 5 Campaigns by ROI:")
display(bottom_5[['Campaign_Name', 'Channel', 'ROI', 'CAC', 'ROAS', 'Revenue Generated', 'Cost/Ad Spend']])''')

    add_code('''# Plot: ROI by Campaign
plt.figure(figsize=(12, 6))
sns.barplot(data=sorted_campaigns, x='Campaign_ID', y='ROI', palette='viridis')
plt.title('ROI by Campaign', fontsize=16)
plt.xticks(rotation=45)
plt.axhline(0, color='red', linestyle='--')
plt.tight_layout()
plt.savefig('roi_by_campaign.png')
plt.show()''')

    add_markdown('''## 4. Channel-Level Insights
Analyze metrics aggregated by marketing channel.''')

    add_code('''channel_agg = df.groupby('Channel').agg({
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
display(channel_agg_sorted)

# Plot: CAC by Channel
plt.figure(figsize=(10, 6))
sns.barplot(data=channel_agg_sorted, x='Channel', y='CAC', palette='rocket')
plt.title('Customer Acquisition Cost (CAC) by Channel', fontsize=16)
plt.tight_layout()
plt.savefig('cac_by_channel.png')
plt.show()''')

    add_markdown('''## 5. Visualizing the Conversion Funnel, Revenue vs Cost, and Time Trends''')

    add_code('''# Revenue vs Cost Scatter Plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=campaign_agg, x='Cost/Ad Spend', y='Revenue Generated', 
                size='Conversions', sizes=(50, 500), hue='Channel', alpha=0.7)
# Ideal line where Revenue = Cost (Break Even)
max_val = min(campaign_agg['Cost/Ad Spend'].max(), campaign_agg['Revenue Generated'].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='Break Even')
plt.title('Revenue vs Cost by Campaign')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('revenue_vs_cost.png')
plt.show()''')

    add_code('''# Time Series Trends (Monthly)
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
plt.show()''')

    add_markdown('''## 6. Advanced Analytics: Clustering & Regression
We will cluster campaigns into High, Medium, and Low Performance groups using K-Means.
We will also fit a basic linear regression to predict ROI based on CTR and CR.''')

    add_code('''# Clustering
features = ['ROI', 'CAC', 'ROAS']
X = campaign_agg[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42)
campaign_agg['Performance_Cluster'] = kmeans.fit_predict(X_scaled)

# Map clusters to descriptive names based on mean ROI
cluster_means = campaign_agg.groupby('Performance_Cluster')['ROI'].mean().sort_values()
cluster_mapping = {
    cluster_means.index[0]: 'Low Performance',
    cluster_means.index[1]: 'Medium Performance',
    cluster_means.index[2]: 'High Performance'
}
campaign_agg['Performance_Segment'] = campaign_agg['Performance_Cluster'].map(cluster_mapping)

plt.figure(figsize=(10, 6))
sns.scatterplot(data=campaign_agg, x='CAC', y='ROI', hue='Performance_Segment', s=100, palette='Set1')
plt.title('Campaign Segmentation (K-Means)')
plt.axhline(0, color='black', linestyle='--')
plt.tight_layout()
plt.savefig('clusters.png')
plt.show()''')

    add_code('''# Regression to predict ROI
from sklearn.metrics import r2_score

X_reg = campaign_agg[['CTR', 'CR', 'CPC']]
y_reg = campaign_agg['ROI']

reg = LinearRegression()
reg.fit(X_reg, y_reg)
y_pred = reg.predict(X_reg)

campaign_agg['Predicted_ROI'] = y_pred
print(f"Regression R^2 Score: {r2_score(y_reg, y_pred):.4f}")
print("Coefficients [CTR, CR, CPC]:", reg.coef_)''')

    add_markdown('''## 7. Decision & Recommendation Engine
Based on the data and metrics above, we map campaigns to recommendations:
- **Scale Up (Invest More):** High ROI (>0.5) + Low CAC 
- **Optimize:** Positive ROI (0 to 0.5) OR High Traffic but Low Conversion (CR < mean)
- **Stop:** Negative ROI (< 0)''')

    add_code('''def recommendation(row):
    if row['ROI'] < 0:
        return 'STOP ❌'
    elif row['ROI'] > 0.5 and row['CAC'] < campaign_agg['CAC'].median():
        return 'SCALE UP ✅'
    else:
        return 'OPTIMIZE ⚙️'

campaign_agg['Recommendation'] = campaign_agg.apply(recommendation, axis=1)

print("💡 Final Campaign Recommendations:")
display(campaign_agg[['Campaign_Name', 'Channel', 'ROI', 'CAC', 'Recommendation']].sort_values(by='ROI', ascending=False))''')

    add_markdown('''## 8. Summary Report Output
Writing the final findings to `summary_report.md`.''')

    add_code('''scale_up = campaign_agg[campaign_agg['Recommendation'] == 'SCALE UP ✅']['Campaign_Name'].tolist()
stop = campaign_agg[campaign_agg['Recommendation'] == 'STOP ❌']['Campaign_Name'].tolist()
optimize = campaign_agg[campaign_agg['Recommendation'] == 'OPTIMIZE ⚙️']['Campaign_Name'].tolist()

report = f"""# Final Summary Report: Marketing Campaign Performance

## 📊 Overview
Analyzed {len(df)} records spanning {len(campaign_agg)} marketing campaigns.

## 🏆 Top Performing Channels
Based on CAC and ROI, the most efficient channels are:
{(channel_agg_sorted.head(3)[['Channel', 'CAC', 'ROI']].to_markdown(index=False))}

---

## 🧾 Expected Output Summary

### ✅ Campaigns to scale up (High ROI, Low CAC)
{', '.join(scale_up) if scale_up else 'None'}

### ❌ Campaigns to stop (Negative ROI, High CAC)
{', '.join(stop) if stop else 'None'}

### ⚙️ Campaigns to optimize (Moderate Returns, Low CR)
{', '.join(optimize) if optimize else 'None'}

### 💰 Suggested Budget Distribution
- Reallocate 100% of the budget from 'STOP' campaigns.
- Direct 70% of freed budget towards 'SCALE UP' campaigns.
- Allocate 30% of freed budget to A/B test 'OPTIMIZE' campaigns to improve Conversion Rates.
"""

with open('summary_report.md', 'w') as f:
    f.write(report)
print("Summary report generated successfully as 'summary_report.md'")''')

    # Save notebook
    with open('marketing_analysis.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    print("Notebook 'marketing_analysis.ipynb' generated successfully.")

if __name__ == "__main__":
    generate_notebook()
