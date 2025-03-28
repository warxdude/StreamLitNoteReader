import streamlit as st 
import pandas as pd

def load_df(fileobj):
    if fileobj.name.endswith('.csv'):
       df = pd.read_csv(fileobj)
    elif fileobj.name.endswith('.xlsx'):
       df = pd.read_excel(fileobj)  
    if 'comments' not in df.columns:
        df['comments'] = ''
    if 'correct' not in df.columns:
        df['correct'] = ''
    if 'reviewer' not in df.columns:
        df['reviewer'] = ''
    st.session_state.notes_dataframe=df
    st.session_state.current_file=fileobj.name
    st.session_state.filter_widget_history = []
    if "filter_tracker" in st.session_state:
        st.session_state['filter_tracker'].clear()
    else:
        st.session_state['filter_tracker'] = {}
    for col in df.columns:
        st.session_state['filter_tracker'][col] = { 'selected':False, 'selections': df[col].unique().tolist() }

csv_to_upload=st.file_uploader("Choose an XLSX or CSV file", type=["xlsx","csv"])
try:
    if csv_to_upload is not None: 
        load_df(csv_to_upload)
except Exception as e:
    st.error(f"An error occurred: {e}")

