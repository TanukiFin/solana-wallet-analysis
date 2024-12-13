# conda activate crypto
# streamlit run Home.py

import streamlit as st
import requests
import time
import json

api_key = "17b80ebe-e038-4233-8b65-a3861417664f"


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

tx = st.text_input("tx", "64ZPpHJZqv5PLaSvPDJgSpY37uAUU2u9NfN3Ao2kNCyjGacpV9yGvLYjfyZCnAEei2c8Bg2dTL8ew2LCh22U93ue")

webhook_url = st.text_input("webhook_url")
confirm1 = st.button("Confirm", key="confirm1")


if confirm1:
    st.write("目前查詢TX: " + tx)
    data = fetch_transactions_by_sig(sig_list=[tx])
    st.write(data)

    
    r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    if r.status_code == 200:
        st.write("webhook傳送成功")
    else:
        st.write("webhook傳送失敗")
