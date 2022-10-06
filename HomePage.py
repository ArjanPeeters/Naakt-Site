import streamlit as st
import pandas as pd

session = st.session_state
# set the lists for Naam Kenmerk en Toepassing in the session state

def database():

    if 'database' not in session:
        path = 'NAAkt uitgebreid.json'
        session['database'] = pd.read_json(path)

    return session['database']

session['naam'] = database().Naam.unique()
session['kenmerk'] = database().Kenmerk.unique()
session['toepassing'] = toepassing = database().Toepassing.unique()


def callback_naam():
    session.pop('kenmerk_gekozen')
    session.pop('toepassing_gekozen')


def reset():
    session.pop('naam_gekozen')
    session.pop('kenmerk_gekozen')
    session.pop('toepassing_gekozen')


def copy2clipboard():
    st.success('gekopieerd')


def main():

    #set the page config
    st.set_page_config(
        layout="wide",
        page_title="Naa.K.T. generator",
        page_icon="✍️",
    )

    st.image('Logo NAA.K.T.png')

    naakt = '{naam}_{kenmerk}_{toepassing}'.format(
        naam=session['naam_gekozen'] if 'naam_gekozen' in session else '',
        kenmerk=session['kenmerk_gekozen'] if 'kenmerk_gekozen' in session else '',
        toepassing=session['toepassing_gekozen'] if 'toepassing_gekozen' in session else ''
    )

    # build up main selectors in 3 big columns and 2 small columns for the '_'
    reset_col, col1, col2, col3, col4, col5, copy_col = st.columns([1,4, 1, 4, 1, 4,1])
    with col1:
        st.markdown("""<div style="text-align: right"><h1> {} </h1></div><br>""".format(session['naam_gekozen'] if 'naam_gekozen' in session else 'Naam'), unsafe_allow_html=True)
        naam = st.selectbox('Naam', options=session['naam'], label_visibility='collapsed', key='naam_gekozen', on_change=callback_naam)

    with col3:
        st.markdown("""<div style="text-align: center"><h1> {} </h1></div><br>""".format(session['kenmerk_gekozen'] if 'kenmerk_gekozen' in session else 'Kenmerk'), unsafe_allow_html=True)
        kenmerk = st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(), label_visibility='collapsed', key='kenmerk_gekozen')

    with col5:
        st.markdown("""<div style="text-align: left"><h1> {} </h1></div><br>""".format(session['toepassing_gekozen'] if 'toepassing_gekozen' in session else 'Toepassing'), unsafe_allow_html=True)
        toepassing = st.selectbox('Toepassing', options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(), label_visibility='collapsed', key='toepassing_gekozen')

    with col4:
        st.markdown("""<div style="text-align: center"><h1> _ </h1></div><br>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style="text-align: center"><h1> _ </h1></div><br>""", unsafe_allow_html=True)

    with reset_col:
        st.button('Reset', key='reset_pressed', on_click=reset)

    with copy_col:
        st.button('Copy', key='copy_pressed', on_click=copy2clipboard)


if __name__ == "__main__":
    main()