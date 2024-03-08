import requests
import pandas as pd
import re
import streamlit as st
import warnings
warnings.filterwarnings("ignore")
                        
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 10) 
pd.set_option('display.max_colwidth', 30) 

api_key = "814e2855-a7f8-4d84-b0bc-82cedf5694e3"


def fetch_transactions(address="4NVoofLVJqExqFCLGEaw2hfNT7pDRd1Rzbas1XR8f2YY"):
    url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key}"
    last_signature = None
    transactions = []
    counter = st.empty()   
    while True:
        if last_signature:
            url_with_signature = f"{url}&before={last_signature}"
        else:
            url_with_signature = url
        response = requests.get(url_with_signature)
        data = response.json()

        if 'error' in data:
            print("錯誤：", data)
            counter.write("總共TX數:",str(len(transactions)))
            return  transactions  

        transactions = transactions + data
        
        if data and len(data) > 0:
            print("已獲取交易：", len(transactions))
            last_signature = data[-1]["signature"]
            counter.write(str(len(transactions)))

        else:
            print("沒有更多的交易了")
            counter.write("總共TX數:",str(len(transactions)))
            break

    return  transactions   

def fetch_jupiter_price(token_name= "SOL"):
    url = "https://price.jup.ag/v4/price"
    params = {"ids": token_name}
    price = 0

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            price = data["data"][token_name]["price"]
            
        except:
            print(f"{token_name} Failed to fetch price:", data)
            
    else:
        print(f"{token_name} Failed to fetch price:", response.status_code)
    
    return price

def parse_transactions(transactions, address, threshold):
    df = pd.DataFrame(transactions)
    df["UTC"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df = df.query("type=='TRANSFER'& not description.str.contains('multiple') & not description.str.contains('0 SOL')")

    def parse_description(description):
        matches = re.findall(r'(\w+) transferred ([\d.]+) (\w+) to (\w+)\.', description)
        if matches:
            sender_address, amount, token_name, receiver_address = matches[0]
            return sender_address, amount, token_name, receiver_address
        else:
            return None, None, None, None
        
    df["sender"], df["amount"], df["token_name"], df["receiver"] = zip(*df["description"].apply(parse_description))
    df = df[["sender","amount","token_name","receiver","UTC","signature"]]#.reset_index(drop=True)
    df["amount"] = df["amount"].astype(float).round(2)


    token_list = df["token_name"].unique()
    token_price = {}
    for token in token_list:
        price = fetch_jupiter_price(token)
        token_price[token] = price
        
    df["USD"] = df.apply(lambda row: row["amount"] * token_price.get(row["token_name"], 0), axis=1)
    df["USD"] = df["USD"].astype(float).round(0)
    df = df.query(f"USD > {threshold}")

    sendTX = df.query(f"sender=='{address}'")
    receiveTX = df.query(f"receiver=='{address}'")

    sendTX_group = sendTX.groupby(["receiver", "token_name"]).agg(total_amount=("amount", "sum"), usd=("USD", "sum"), tx_count=("amount", "count")).sort_values("usd",ascending=False)
    receiveTX_group = receiveTX.groupby(["sender", "token_name"]).agg(total_amount=("amount", "sum"), usd=("USD", "sum"), tx_count=("amount", "count")).sort_values("usd",ascending=False)
    
    return sendTX_group, receiveTX_group