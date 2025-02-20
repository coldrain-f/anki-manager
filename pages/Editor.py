import streamlit as st

import pandas as pd
from datetime import datetime

if "cards" not in st.session_state:
    st.session_state["cards"] = {
        "Expression": [None],
        "Meaning": [None],
        "Example_JP": [None],
        "Example_KR": [None],  
    }

st.set_page_config(layout="wide")

st.title("Editor")

cards = st.session_state["cards"]

df = pd.DataFrame(cards)
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

edited_df.insert(1, "Reading", [None])
edited_df.insert(4, "Example_JP_Reading", [None])

csv = edited_df.to_csv(index=False, header=False)

# 현재 시간을 밀리초까지 포함하여 포맷팅
current_time = datetime.now().strftime("%Y%m%d")
file_name = f'cards_{current_time}.csv'

st.download_button(
    label="Download CSV",
    data=csv,
    file_name=file_name,
    mime='text/csv'
)