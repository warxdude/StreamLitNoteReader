import streamlit as st 
import re

custom_css = """
<style>
textarea {
    font-size: 18px !important; /* Change font size here */
}
</style>
"""
# r"(Medications Prior to Admission)(?:[:])?$"
note_headers=[  r"(Current\s?(Facility-Administered)?)?\s?Medications\s?(Prior to Admission)?:?\s+",
                r"Objective:?\s+",
                r"Subjective:?\s+",
                r"Allergies:?\s+",
                r"Labs(/Studies)?:?\s+",
                r"Assessment\s?((and|&|/) plan)?:?\s+",
                r"Vital Signs:?\s+",
                r"(Past\s)?(Social|Medical|Surgical|Family) History:?\s+",
                r"Chief Complaint:?\s+",
                r"Plan:?\s+",
                r"Physical Exam:?\s+",
                r"History of Present(ing)? Illness:?\s+",
                r"Review of Systems:?\s+",
                r"History and Presentation:?\s+",
                r"(Active|Principal) Problems?:?\s+",
                r"Radiology:?\s+",
                r"Diagnostic Impression:?\s+",
                r"Review of Systems:?\s+"
                 ]

@st.dialog("Add Your Comments")
def add_feedback(idx):
    orig_df_idx = st.session_state.filtered_df.loc[idx,"index"]
    current_comments = st.session_state.notes_dataframe.loc[orig_df_idx,"comments"]
    current_result = st.session_state.notes_dataframe.loc[orig_df_idx,"correct"]
    current_reviewer = st.session_state.notes_dataframe.loc[orig_df_idx,"reviewer"]
    comment = st.text_input("Feedback:", value=current_comments)
    reviewer_initials = st.text_input("Initials:",value=current_reviewer,max_chars=4)
    correct_result = st.toggle("Correct:", value=False if current_result == "" or current_result == 'No' else True)
    if st.button("Submit",type="primary"):
        if len(comment) > 1 and len(reviewer_initials) > 1:
            st.session_state.notes_dataframe.loc[orig_df_idx,"comments"] = comment
            st.session_state.notes_dataframe.loc[orig_df_idx,"reviewer"] = reviewer_initials
            st.session_state.notes_dataframe.loc[orig_df_idx,"correct"] = 'Yes' if correct_result else 'No'
            st.rerun()
        else:
            st.warning("Check your comment and initials before submitting.  Click the 'X' to close")

def split_and_create_dict(text, headers):
    patterns = "(" + "|".join(s for s in headers) + ")"
    matches = list(re.finditer(patterns, text,re.IGNORECASE))
    result_dict = {}
    for i, match in enumerate(matches):
        m_key=match.group(0).strip()
        start=match.end()
        if i==0:
          result_dict[""]=text[0:match.start()].strip()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        value = re.sub(r"^:","",text[start:end].strip())
        result_dict[m_key] = value
    return result_dict

def refreshDf():
    
    st.session_state.filtered_df = st.session_state.notes_dataframe.copy()
    for key in st.session_state.filter_tracker:
        if len(st.session_state.filter_tracker[key]['selections']) > 0: 
            st.session_state.filtered_df = st.session_state.filtered_df[st.session_state.filtered_df[key].isin(st.session_state.filter_tracker[key]['selections'])]
    st.session_state.filtered_df=st.session_state.filtered_df.reset_index()

def resetFilters():
   
   temp_df = st.session_state.notes_dataframe.copy()
   for col in temp_df.columns:
       st.session_state['filter_tracker'][col] = { 'selected':False, 'selections':  temp_df[col].unique().tolist()  }
   st.session_state.col_select_key = []
   refreshDf()

   
def row_selected():

    if len(st.session_state.dataframe.selection.rows) > 0:
       for idx in st.session_state.dataframe.selection.rows:
          
           with mainContainer:
               st.markdown(custom_css, unsafe_allow_html=True)
               with st.expander("See Note",expanded=True):
                      col1, col2 = st.columns([0.12,0.88])
                      with col1:
                        show_fmt = st.toggle("Format Note",value=True, key=f"note_fmt_{idx}")
                      with col2:
                        if st.button("Comments", icon=":material/comment:",type="primary"):
                            add_feedback(idx)
                      if show_fmt:
                          textDict = split_and_create_dict(st.session_state.filtered_df.loc[idx,"note_text"], note_headers)
                          noteSections = [f"{re.sub(r":$","",k.strip())}{"" if k == "" else ":"}\n{re.sub(r"^\s+","",v)}" for k, v in textDict.items()]
                          formattedNote = "\n\n".join(noteSections) 
                          st.text_area("Note", formattedNote,height=800,key=f"sel_{idx}")
                      else:
                          st.text_area("Note", st.session_state.filtered_df.loc[idx,"note_text"],height=800,key=f"sel_{idx}")
                     
                         
    else:
       with mainContainer:
         st.info("Select row to display note text")       


def applyFilters(**kwargs):
    session_key = kwargs['key']
    selected_options = st.session_state[session_key]
    if len(selected_options) > 0:
        for opt in selected_options:
            last = set(st.session_state.filter_tracker[session_key]['selections'])
            cur = set(selected_options)
            diff = list(last.difference(cur))
            st.session_state.filter_tracker[session_key]['selections'] = [x for x in st.session_state.filter_tracker[session_key]['selections'] if x not in diff]
            if opt not in st.session_state.filter_tracker[session_key]['selections'] and st.session_state.filter_tracker[session_key]['selected']:
                    st.session_state.filter_tracker[session_key]['selections'].append(opt)
            
    else:
        st.session_state.filter_tracker[session_key]['selected'] = False
        st.session_state.filter_tracker[session_key]['selections'] = st.session_state.notes_dataframe[session_key].unique().tolist()
    enableFilters()


def enableFilters():
   
   last = set(st.session_state.filter_widget_history)
   cur = set(st.session_state.col_select_key)
   diff = list(last.difference(cur))
   for key in st.session_state.col_select_key:
        if not st.session_state.filter_tracker[key]['selected']: 
            st.session_state.filter_tracker[key]['selected'] = True
            st.session_state.filter_tracker[key]['selections'].clear()

   # reset removed filter option back to unselected and restore all options
   if diff is not None:
    for old_key in diff:
        st.session_state.filter_tracker[old_key]['selected'] = False
        st.session_state.filter_tracker[old_key]['selections'] = st.session_state.notes_dataframe[old_key].unique().tolist() 
   
   refreshDf()
   st.session_state.filter_widget_history=st.session_state.col_select_key

try:
    if "notes_dataframe" in st.session_state:
        
        filterContainer = st.sidebar.container(key='filter_container')
        mainContainer = st.container(key="Main")
        refreshDf()
        with filterContainer:
             st.multiselect("Select Filter Columns",
                            st.session_state.filter_tracker.keys(), 
                            key='col_select_key', 
                            on_change=enableFilters)
             st.button("Clear",on_click=resetFilters,type="primary")
             for key in st.session_state.filter_tracker:
                 if st.session_state.filter_tracker[key]['selected']:
                    st.multiselect(key,st.session_state.notes_dataframe[key].unique().tolist(),key=key,kwargs={"key":key},on_change=applyFilters, default=st.session_state.filter_tracker[key]['selections'])
        with mainContainer:            
            with st.expander("View Data", expanded=True):
                    dfWidget=st.dataframe(st.session_state.filtered_df,
                                    selection_mode=['single-row'],
                                    key="dataframe",
                                    on_select="rerun")
                    row_selected()

    else:
       st.info('Select file to load into dataframe.')
except Exception as e:
     st.error(f"An error occurred: {e}")