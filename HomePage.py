import streamlit as st
import pandas as pd
import csv
import pyairtable as at
import streamlit_nested_layout

session = st.session_state


# @st.experimental_singleton
def table():
    return at.Table(
        api_key=st.secrets['airtable_key'],
        base_id=st.secrets['naakt_db'],
        table_name='Naakt DB'
    )


# @st.experimental_singleton
def database():
    if 'database' not in session:
        path = 'NAAkt uitgebreid.json'
        session['database'] = pd.read_json(path)

    return session['database']


def naakt(return_dict=None):
    naam = session['naam_chosen'] if 'naam_chosen' in session else ''
    kenmerk = session['kenmerk_chosen'] if 'kenmerk_chosen' in session else ''
    toepassing = session['toepassing_chosen'] if 'toepassing_chosen' in session else ''
    ef1 = '_' + session['extra_field1'].lower().replace(' ', '-') if 'extra_field1' in session else ''
    ef2 = '_' + session['extra_field2'].lower().replace(' ', '-') if 'extra_field2' in session else ''
    ef3 = '_' + session['extra_field3'].lower().replace(' ', '-') if 'extra_field3' in session else ''
    naakt_string = f'{naam}_{kenmerk}_{toepassing}{ef1}{ef2}{ef3}'
    naakt_dict = {
        'benaming': naakt_string,
        'naam': naam,
        'kenmerk': kenmerk,
        'toepassing': toepassing,
        'extra_veld1': ef1[1:],
        'extra_veld2': ef2[1:],
        'extra_veld3': ef3[1:]
    }

    if return_dict:
        return naakt_dict
    else:
        return naakt_string


def callback_naam():
    if 'kenmerk_chosen' in session:
        session.pop('kenmerk_chosen')
    if 'toepassing_chosen' in session:
        session.pop('toepassing_chosen')


def plus_pressed():
    if 'added_columns' not in session:
        session['added_columns'] = 0

    if session['added_columns'] == 3:
        st.warning('max 3 extra momenteel')
    else:
        session['added_columns'] += 1


def min_pressed():
    if 'added_columns' in session:
        field = f"extra_field{session['added_columns']}"
        session.pop(field)
        session['added_columns'] -= 1


def save():
    if 'save_list' not in session:
        session.save_list = []
    session.save_list.insert(0, naakt())
    table().create(naakt(return_dict=True))
    if session['reset on save']:
        session['extra_field1'] = ''
        session['extra_field2'] = ''
        session['extra_field3'] = ''


def reset_list():
    session.save_list = []


def main():
    st.set_page_config(page_title="Naa.K.T. Materiaal benaming")

    st.sidebar.image('Logo NAA.K.T.png')
    st.sidebar.markdown('---')
    st.sidebar.markdown('&emsp;gemaakt door:')
    st.sidebar.image('BIMnerd_Logo.png')
    st.sidebar.markdown('---')
    st.sidebar.write('Aangemaakte materiaal benamingen worden anoniem opgeslagen voor analyse')

    header_body = st.container()
    material_body = st.container()
    save_body = st.container()

    header_body.write('maak een NAA.K.T materiaal benaming aan')

    with material_body:


        st.code(naakt())

        # build up main selectors in 3 big columns and 2 small columns for the '_'

        outer_cols = st.columns([12, 3])

        with outer_cols[0]:
            col1, col2, col3 = st.columns(3)
            with col1:
                naam = st.selectbox('Naam', options=database()['Naam'].unique(), label_visibility='collapsed',
                                    key='naam_chosen', on_change=callback_naam)

            with col2:
                st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(),
                             label_visibility='collapsed', key='kenmerk_chosen')

            with col3:
                st.selectbox('Toepassing', options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(),
                             label_visibility='collapsed', key='toepassing_chosen')

            col_add1, col_add2, col_add3 = st.columns(3)

            if 'added_columns' in session and session['added_columns'] > 0:
                with col_add1:
                    st.text_input('vul in:', value='extra-veld-1', key='extra_field1', label_visibility='collapsed')

            if 'added_columns' in session and session['added_columns'] > 1:
                with col_add2:
                    st.text_input('test', value='extra-veld-2', key='extra_field2', label_visibility='collapsed')

            if 'added_columns' in session and session['added_columns'] > 2:
                with col_add3:
                    st.text_input('test', value='extra-veld-3', key='extra_field3', label_visibility='collapsed')

        with outer_cols[1]:
            col_plus, col_button = st.columns([1, 2])
            with col_plus:
                st.button('+', key='plus_pressed', on_click=plus_pressed)
                if 'added_columns' in session and session['added_columns'] > 0:
                    st.button('-', on_click=min_pressed)

            with col_button:
                st.button('Save', key='save_pressed', on_click=save)
                st.checkbox('reset on save', key='reset on save')

        # Make extra section with columns so it builds up normaly on small screen width


    with save_body:
        st.title('')
        st.markdown('---')

        if 'save_list' in session:
            left, saved_list, right = st.columns([1, 4, 1])
            with saved_list:
                for s in session.save_list:
                    st.code(s)
            with left:
                st.button('Empty', key='reset_list_pressed', on_click=reset_list)
            with right:
                _string = '\n'.join(session['save_list'])
                st.download_button(label='download', data=f"{_string}")

    # st.write(session)


if __name__ == "__main__":
    main()
