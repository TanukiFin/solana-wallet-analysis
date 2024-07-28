# conda activate crypto
# streamlit run Home.py

import streamlit as st
import requests
import time
import json

api_key = "12a476fe-a758-47da-bd31-4c4942430f23"


st.set_page_config(
    page_title="crypto",
    page_icon="💸",
    layout="wide",
)

# no footer
def no_footer():
    st.markdown("""
    <style>
    .css-9s5bis.edgvbvh3
    {
        visibility: hidden;
    }
    .css-h5rgaw.egzxvld1
    {
        visibility: hidden;
    }
    </style>
    """,unsafe_allow_html=True) #用HTML unsafe_allow_html=True


def fetch_transactions_by_address(address, params={}): # max: 100 txs
    while True:
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key}"
            response = requests.get(url, params=params )
            data = response.json()
            return  data   
        except:
            print("error fetch_transactions_by_address: wait for 10 sec...")
            time.sleep(10)
    
def fetch_transactions_by_sig(sig_list):
    url = f"https://api.helius.xyz/v0/transactions/?api-key={api_key}"
    headers = {
            'Content-Type': 'application/json',
    }
    param = {
        "transactions": sig_list
            #["593wEz7afr4bH8puUEeqVeDsFAcWSnwydmU4NkHDFX19Hdvf2i5tJF6WheU6RRd6F7jHgUh6kEvujiUPCo36x8Do",
            #"4DCrERdsW3q6QZtaswEw4Ut9qDWLFKixUxmZUvLvSYC3mxVk4eSBk2RLHXcTC6TkFb93eycvPiTeWC71kFFQiyj9"]
    }

    response = requests.post(url, headers=headers, data=json.dumps(param))
    data = response.json()
    
    return  data   


# Input 區

address = st.text_input("Address", "CbX4X1AsaRYmMibzbfSEdYs5e1zTUQ77JR4x9BsVd2F7")
confirm1 = st.button("Confirm", key="confirm1")

if confirm1:
    st.write("目前查詢地址: " + address)
    data = fetch_transactions_by_address(address=address)
    st.write(data[0:5])


tx = st.text_input("Tx", "4fkGUXsFauSqczCky6VNd6HeDYe3vhvuVh2h1wrSkArgJUi5kXeC1c2po3TAzNQtdwwf8KvE1pr6ML7QvJ5684m4")
confirm2 = st.button("Confirm", key="confirm2")


if confirm2:
    st.write("目前查詢TX: " + tx)
    data = fetch_transactions_by_sig(sig_list=[tx])
    st.write(data)
