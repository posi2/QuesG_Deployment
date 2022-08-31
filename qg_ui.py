import streamlit as st
import pipeline


if __name__ == '__main__':
    st.title('Question Generation Demo')
    starting_text = st.text_area('Let generate the questions from your text or article')

    obj_pipeline = pipeline.Pipeline()
    
    if starting_text:
        fill_up, ques  = obj_pipeline.prediction(starting_text)
        st.markdown(f'Fill Up \n {fill_up}')
        st.markdown(f'Wh \n {ques}')