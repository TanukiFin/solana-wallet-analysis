import requests
import pandas as pd
import re
import streamlit as st
import time
import random
import warnings
warnings.filterwarnings("ignore")

from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solders.signature import Signature
                        
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 10) 
pd.set_option('display.max_colwidth', 30) 

api_key = ["814e2855-a7f8-4d84-b0bc-82cedf5694e3",
           "e10ad31d-205d-4bd2-ad35-e261cd901f38",
           "6d8bfbc2-44f3-4c30-b31e-c1322741dce8",
           "4a53c62c-2be7-4030-8e51-7f4867bf16c4",
           "f5678270-3a1a-4868-ba6a-1d70a0891966",
           "8c5ca67a-9aa2-4986-905f-2a95b1927b34",
           "12728bae-550f-4f59-a42c-94b89d9e86b8",
           "0c496773-5e98-428a-90da-4b24095db327"]

exchange = pd.read_csv("exchange.csv")

def fetch_1transactions(address="4NVoofLVJqExqFCLGEaw2hfNT7pDRd1Rzbas1XR8f2YY"):
    randNum = random.randint(0, len(api_key) - 1)
    url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key[randNum]}"
    response = requests.get(url)
    data = response.json()
    return  data   


def fetch_all_transactions(address="4NVoofLVJqExqFCLGEaw2hfNT7pDRd1Rzbas1XR8f2YY"):
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
                #print("錯誤：", data)
                counter.write("總共TX數:"+str(len(transactions)))
                return  transactions  
        
        transactions = transactions + data
        
        if data and len(data) > 0:
            print("已獲取交易：", len(transactions))
            last_signature = data[-1]["signature"]
            counter.write(str(len(transactions)))

        else:
            print("沒有更多的交易了")
            counter.write("總共TX數:"+str(len(transactions)))
            break

    return  transactions   


def getBalance(address):
    try:
        randNum = random.randint(0, len(api_key) - 1)
        url = f"https://mainnet.helius-rpc.com/?api-key={api_key[randNum]}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [
                address
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        
        return response.json()['result']['value'] / 10e8
    
    except:
        print(response.json())
        return 0


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
            #print(f"{token_name} Failed to fetch price:", data)
            pass
            
    else:
        #print(f"{token_name} Failed to fetch price:", response.status_code)
        pass
    
    return price


def parse_transactions(transactions, address, threshold, jup_check=True):
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
    df = df[["sender","amount","token_name","receiver","UTC","signature"]]
    
    if jup_check == True:
        df["amount"] = df["amount"].astype(float).round(2)
        df = df.query("token_name.str.len() < 10") # 排除 token_name 是地址的

        # 取得 token price by Jupiter Api
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
    
    elif jup_check == False:
        sendTX = df.query(f"sender=='{address}'")
        receiveTX = df.query(f"receiver=='{address}'")

        sendTX_group = sendTX.groupby(["receiver"]).count()
        receiveTX_group = receiveTX.groupby(["sender"]).count()
    
    return sendTX_group, receiveTX_group


def recent_tx_count(address="AYhux5gJzCoeoc1PoJ1VxwPDe22RwcvpHviLDD1oCGvW"): 
    try:
        data = fetch_1transactions(address)
        current_timestamp = time.time()
        one_hour_ago_timestamp = current_timestamp - 7200 # 最近2hr 
        recent_timestamps = [transaction['timestamp'] for transaction in data if transaction['timestamp'] >= one_hour_ago_timestamp]
        return data, len(recent_timestamps)
    except:
        print("error recent_tx_count: "+address)
        return data, 0


def exchange_deposit_address_check(ddd, address):
    sss, rrr = parse_transactions(ddd, address, 10, jup_check=False)
    idx = sss.index.get_level_values("receiver").isin(exchange["address"])
    contains_exchange = sss.index.get_level_values("receiver")[idx]
    if contains_exchange.any():
        exchange_name = exchange.loc[exchange['address'] == contains_exchange[0], 'exchange'].values[0]
    else:
        exchange_name = False

    return exchange_name


def find_associated_wallet(sendTX_group, receiveTX_group):
    send_usd = sendTX_group.groupby("receiver").agg(send=("usd", "sum"), sendTX=("tx_count", "sum")).sort_values(["send"],ascending=False)
    receive_usd = receiveTX_group.groupby("sender").agg(receive=("usd", "sum"), receiveTX=("tx_count", "sum")).sort_values(["receive"],ascending=False)
    total_interact = pd.concat([send_usd, receive_usd], axis=1)
    total_interact.columns = ["sendUSD", "sendTX","receiveUSD","receiveTX"]
    total_interact = total_interact.fillna(0)
    total_interact.insert(0, "totalUSD", total_interact["sendUSD"] + total_interact["receiveUSD"])
    total_interact.insert(1, "totalTX", total_interact["sendTX"] + total_interact["receiveTX"])
    total_interact = total_interact.sort_values("totalUSD", ascending=False)


    # 判斷是否為 cex 發錢，標記為 cex
    address_list = total_interact.index
    total_interact.insert(0, "mark", "")
    total_interact["lastTx"] = ""

    for i in range(len(exchange)):
        try:
            eidx = address_list.get_loc(exchange["address"].loc[i])
            total_interact["mark"].iloc[eidx] = exchange["exchange"].loc[i]
        except:
            pass

    # 查每個地址的 tx, sol balance
    total_interact["SOL bal."] = 0
    count = 0
    for aaa in total_interact.index:
        if  total_interact["mark"].loc[aaa] == "":  # 尚未標記成 cex 則繼續
            print(aaa)
            total_interact.at[aaa, "SOL bal."] = getBalance(aaa)
            ddd, txs = recent_tx_count(aaa)

            # 2hr Txs > 50, 可能是某合約地址/cex/bot
            if txs > 50: 
                total_interact["mark"].loc[aaa] = "🤖"

            # 判斷是否為打錢去 cex
            if total_interact["receiveTX"].loc[aaa] == 0 and total_interact["sendTX"].loc[aaa] > 1:
                exchangeTF = exchange_deposit_address_check(ddd, aaa)
                print(exchangeTF)
                if exchangeTF != False:
                    total_interact["mark"].loc[aaa] = "its "+exchangeTF 

            # 計算最後交易日
            lastTx = pd.to_datetime(ddd[0]["timestamp"], unit='s').strftime('%Y-%m-%d')        
            total_interact["lastTx"].loc[aaa] = lastTx
            count += 1
            if count > 7:
                pass
                #break

    total_interact["SOL bal."] = total_interact["SOL bal."].round(4)
    
    # 高機率是小號
    total_interact.loc[(total_interact['sendTX'] >= 3) & (total_interact['receiveTX'] >= 3), 'mark'] = "🔗"

    return total_interact