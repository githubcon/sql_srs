import streamlit as st
import pandas as pd
import numpy as np
import duckdb



#st.write(st.image)

st.write("""
# SQL SRS
Spaced Repetition System SQL pratice
""")

option = st.selectbox(
    "What would you like to review ?",
    ("Joins", "GroupBy", "Windows Function"),
    index=None,
    placeholder="Select a theme...",
)

data = {"a": [1,2,3], "b": [4,5,6]}
df = pd.DataFrame(data)


tab1, tab2, tab3 = st.tabs(["cat", "Dog", "Owl"])

with tab1:
    #st.header("A cat")
    #st.image("data:image/jpeg;base64,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", width=200)
    text_input = st.text_area(label= "Entrer votre code")
    result = duckdb.query(text_input).df()
    st.write(f"Vous avez entré la query suivante : {text_input}")
    st.dataframe(result)

with tab2:
    st.header("A dog")
    st.image("data:image/jpeg;base64,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", width=200)

with tab3:
    st.header("An owl")
    st.image("data:image/jpeg;base64,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", width=200)


