import streamlit as st

def main():
    review_page = st.Page("misc_pages/review.py",title="Review Notes",icon=":material/edit_document:")
    load_csv = st.Page("misc_pages/load_csv.py",title="Load Note Data",icon=":material/dataset:")
    pg = st.navigation([review_page, load_csv])
    st.set_page_config(page_title="LLM Note Reviewer",layout="wide")
    # Initialize DataFrame in session state
    pg.run()
    

if __name__ == "__main__":
    st.session_state["row_selected"] = -1
    main()