import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_marketing_data(num_records=1500, filename='marketing_data.csv'):
    np.random.seed(42)
    random.seed(42)
    
    channels = ['Google Ads', 'Facebook', 'Instagram', 'Email', 'LinkedIn', 'Twitter', 'TikTok']
    regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East']
    segments = ['Young Adults', 'Professionals', 'Students', 'Retirees', 'General']
    
    # Create 20 distinct campaigns
    campaigns = []
    for i in range(1, 21):
        channel = random.choice(channels)
        campaigns.append({
            'Campaign_ID': f'CMP_{i:03d}',
            'Campaign_Name': f'{channel} - Promo {i}',
            'Channel': channel,
            'Base_Impression': random.uniform(0.5, 2.0),
            'Base_CTR': random.uniform(0.01, 0.08),
            'Base_CR': random.uniform(0.02, 0.15),
            'Base_CPC': random.uniform(0.5, 5.0),
            'Base_AOV': random.uniform(20, 200)
        })
        
    start_date = datetime(2025, 1, 1)
    
    data = []
    for _ in range(num_records):
        camp = random.choice(campaigns)
        
        date = start_date + timedelta(days=random.randint(0, 365))
        region = random.choice(regions)
        segment = random.choice(segments)
        
        impressions = int(np.random.normal(10000, 2000) * camp['Base_Impression'])
        impressions = max(100, impressions)
        
        clicks = int(impressions * camp['Base_CTR'] * random.uniform(0.8, 1.2))
        conversions = int(clicks * camp['Base_CR'] * random.uniform(0.7, 1.3))
        
        # If conversions exceed clicks due to randomness, cap it
        conversions = min(conversions, clicks)
        
        cost = clicks * camp['Base_CPC'] * random.uniform(0.9, 1.1)
        customers_acquired = int(conversions * random.uniform(0.8, 1.0))
        revenue = conversions * camp['Base_AOV'] * random.uniform(0.8, 1.2)
        
        # Inject artificial high/low performers
        camp_num = int(camp['Campaign_ID'].split('_')[1])
        if camp_num <= 5: # High performers
            revenue *= random.uniform(1.8, 2.5)
            cost *= random.uniform(0.5, 0.8)
        elif camp_num >= 15: # Low performers
            revenue *= random.uniform(0.3, 0.7)
            cost *= random.uniform(1.2, 2.0)
            
        data.append({
            'Campaign_ID': camp['Campaign_ID'],
            'Campaign_Name': camp['Campaign_Name'],
            'Channel': camp['Channel'],
            'Date': date.strftime('%Y-%m-%d'),
            'Impressions': impressions,
            'Clicks': clicks,
            'Conversions': conversions,
            'Cost/Ad Spend': round(cost, 2),
            'Revenue Generated': round(revenue, 2),
            'Customer Acquired': customers_acquired,
            'Region': region,
            'Audience Segment': segment
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values(by=['Date', 'Campaign_ID'])
    
    # Ensure minimum data quality
    df['Cost/Ad Spend'] = df['Cost/Ad Spend'].apply(lambda x: max(1.0, x))
    
    df.to_csv(filename, index=False)
    print(f"Generated {len(df)} records and saved to {filename}")

if __name__ == "__main__":
    generate_marketing_data()
