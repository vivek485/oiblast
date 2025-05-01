from curl_cffi.requests import Session
import json
import time
import pandas as pd
import streamlit as st

session = Session()

# Critical headers (copy from browser's network tab)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.nseindia.com",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_nse_data():


    try:
        # First visit to market data page (required for cookie setup)
        session.get(
            "https://www.nseindia.com/market-data/live-equity-market",
            headers=headers,
            impersonate="chrome120"
        )
        
        # Add small delay to mimic human behavior
        time.sleep(1.5)
        
        # Make API request with proper referer
        response = session.get(
            "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O",
            headers=headers,
            impersonate="chrome120"
        )
        if response.status_code == 200:
            return response.json()


    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    data = fetch_nse_data()
    if data:
        
        d = (data['data'])
        df = pd.DataFrame(d)
        result_df = df[['symbol', 'pChange']].copy()
        df_sorted = result_df.sort_values(by='pChange', ascending=False).reset_index(drop=True)
        dfb = result_df[result_df.pChange > 2]
        dfs = (result_df[result_df.pChange < -2]).sort_values(by='pChange',ascending=True)
        #print(dfb)
        #print(dfs)
        buylist = dfb['symbol'].to_list()
        selllist = dfs['symbol'].to_list()
        #print(buylist)
        #print(selllist)




    else:
        print("Failed to fetch data")


resp = session.get('https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings',headers=headers,impersonate="chrome120")
data1 = resp.json()
data1 = data1['data']
df1 = pd.DataFrame(data1)
df2 = df1[['symbol' , 'avgInOI']].copy()
df2b = df2[df2.avgInOI > 7]
lst = df2b['symbol'].to_list()

buycommon = list(set(lst) & set(buylist))
sellcommon = list(set(lst) & set(selllist))

filtered_df = dfb[dfb['symbol'].isin(buycommon)] \
               .sort_values('pChange', ascending=False) \
               .reset_index(drop=True)
filtered_dfs = dfs[dfs['symbol'].isin(sellcommon)] \
               .sort_values('pChange', ascending=False) \
               .reset_index(drop=True)
filtered_dfoib = df2[df2['symbol'].isin(buycommon)] \
               .sort_values('avgInOI', ascending=False) \
               .reset_index(drop=True)
filtered_dfois = df2[df2['symbol'].isin(sellcommon)] \
               .sort_values('avgInOI', ascending=True) \
               .reset_index(drop=True)

mergedbuy=pd.merge(filtered_df,filtered_dfoib,on='symbol', how='inner')
mergedsell=pd.merge(filtered_dfs,filtered_dfois,on='symbol', how='inner')
# print(mergedbuy)
# print(mergedsell)
st.write(mergedbuy)
st.write(mergedsell)