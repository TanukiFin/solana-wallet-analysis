import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt

from solana.rpc.api import Client

st.set_page_config(
    page_title="page_title",
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

