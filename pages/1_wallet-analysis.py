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

# 顏色
# st.markdown("""<span style="color:blue">some *blue* text</span>.""",unsafe_allow_html=True)

# 內文
st.header("header")
st.text("still building...")


# Input 區

c1, c2 = st.columns([2,1], gap="large")
address = c1.text_input("Address", "CbX4X1AsaRYmMibzbfSEdYs5e1zTUQ77JR4x9BsVd2F7")
threshold =  c2.number_input("最小USD價值:", value=10)
confirm = st.button("Confirm")

# 按下確認後
if confirm:
    st.write("目前查詢地址: " + address)

    with st.spinner("執行中..."):
        
        transactions = transfer.fetch_all_transactions(address)
        sendTX_group, receiveTX_group = transfer.parse_transactions(transactions, address, threshold)
        total_interact = transfer.find_associated_wallet(sendTX_group, receiveTX_group)
        total_interact.columns = ["🏷️mark","totalUSD","totalTX","📤sendUSD", "📤sendTX","📥receiveUSD","📥receiveTX","🕙lastTx","💵SOL bal."]

    st.markdown("### 🔗**高度相關地址 Highly associated wallet**")
    st.write(total_interact)

    st.markdown("### **send**")
    st.write(sendTX_group)

    st.markdown("### **receive**")
    st.write(receiveTX_group)
