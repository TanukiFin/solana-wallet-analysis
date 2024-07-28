# conda activate crypto
# streamlit run Home.py

import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
from myfunction import transfer
import requests
import json
import datetime
import random
import time
import pandas as pd


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
            randNum = random.randint(0, len(api_key) - 1)
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key[randNum]}"
            response = requests.get(url, params=params )
            data = response.json()
            return  data   
        except:
            print("error fetch_transactions_by_address: wait for 10 sec...")
            time.sleep(10)
    

def fetch_transactions_by_address(address, params={}): # max: 100 txs
    while True:
        try:
            randNum = random.randint(0, len(api_key) - 1)
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key[randNum]}"
            response = requests.get(url, params=params )
            data = response.json()
            return  data   
        except:
            print("error fetch_transactions_by_address: wait for 10 sec...")
            time.sleep(10)
    


# Input 區

c1, c2 = st.columns([2,1], gap="large")
address = c1.text_input("Address", "CbX4X1AsaRYmMibzbfSEdYs5e1zTUQ77JR4x9BsVd2F7")
threshold =  c2.number_input("最小USD價值:", value=10)
confirm = st.button("Confirm")

if confirm:
    st.write("目前查詢地址: " + address)
      
    data = fetch_transactions_by_address(address=address)
    st.write(data)


c1, c2 = st.columns([2,1], gap="large")
address = c1.text_input("Tx", "CbX4X1AsaRYmMibzbfSEdYs5e1zTUQ77JR4x9BsVd2F7")
threshold =  c2.number_input("最小USD價值:", value=10)
confirm = st.button("Confirm")

if confirm:
    st.write("目前查詢地址: " + address)
      
    data = fetch_transactions_by_address(address=address)
    st.write(data)
