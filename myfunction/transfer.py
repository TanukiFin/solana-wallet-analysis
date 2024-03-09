import requests
import pandas as pd
import re
import streamlit as st
import time
import random
import warnings
warnings.filterwarnings("ignore")
                        
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 10) 
pd.set_option('display.max_colwidth', 30) 

api_key = ["814e2855-a7f8-4d84-b0bc-82cedf5694e3",
           "e10ad31d-205d-4bd2-ad35-e261cd901f38",
           "6d8bfbc2-44f3-4c30-b31e-c1322741dce8"]


def fetch_transactions(address="4NVoofLVJqExqFCLGEaw2hfNT7pDRd1Rzbas1XR8f2YY"):
    last_signature = None
    transactions = []
    counter = st.empty()   
    while True:
        randNum = random.randint(0, len(api_key) - 1)
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key[randNum]}"

        if last_signature:
            url_with_signature = f"{url}&before={last_signature}"
        else:
            url_with_signature = url
        response = requests.get(url_with_signature)
        data = response.json()
        
        if "error" in data:
            if "exceeded limit for api" in data:
                print(data)
                time.sleep(3)
                continue   # 暫停1秒繼續跑
            else:
                print("錯誤：", data)
                counter.write("總共TX數: " + str(len(transactions)))
                return  transactions  
        
        transactions = transactions + data

        if data and len(data) > 0:
            print("已獲取TX: ", len(transactions))
            last_signature = data[-1]["signature"]
            counter.write("已獲取TX數: " + str(len(transactions)))

        else:
            print("沒有更多的交易了")
            counter.write("總共TX數: " + str(len(transactions)))
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

def find_associated_wallet(sendTX_group, receiveTX_group):
    send_usd = sendTX_group.groupby("receiver").agg(send=("usd", "sum"), sendTX=("tx_count", "sum")).sort_values(["send"],ascending=False)
    receive_usd = receiveTX_group.groupby("sender").agg(receive=("usd", "sum"), receiveTX=("tx_count", "sum")).sort_values(["receive"],ascending=False)
    total_interact = pd.concat([send_usd, receive_usd], axis=1)
    total_interact.columns = ["sendUSD", "sendTX","receiveUSD","receiveTX"]
    total_interact = total_interact.fillna(0)
    total_interact.insert(0, "totalUSD", total_interact["sendUSD"] + total_interact["receiveUSD"])
    total_interact.insert(1, "totalTX", total_interact["sendTX"] + total_interact["receiveTX"])
    total_interact = total_interact.sort_values("totalUSD", ascending=False)
    return total_interact
