import streamlit as st
import pandas as pd

session = st.session_state


def database():
    if 'database' not in session:
        path = 'NAAkt uitgebreid.json'
        session['database'] = pd.read_json(path)

    return session['database']


def naakt():
    return '{naam}_{kenmerk}_{toepassing}'.format(
        naam=session['naam_gekozen'] if 'naam_gekozen' in session else '',
        kenmerk=session['kenmerk_gekozen'] if 'kenmerk_gekozen' in session else '',
        toepassing=session['toepassing_gekozen'] if 'toepassing_gekozen' in session else '')


def callback_naam():
    if 'kenmerk_gekozen' in session:
        session.pop('kenmerk_gekozen')
    if 'toepassing_gekozen' in session:
        session.pop('toepassing_gekozen')


def reset():
    if 'naam_gekozen' in session:
        session.pop('naam_gekozen')
    if 'kenmerk_gekozen' in session:
        session.pop('kenmerk_gekozen')
    if 'toepassing_gekozen' in session:
        session.pop('toepassing_gekozen')


def save():
    if 'save_list' not in session:
        session.save_list = []
    session.save_list.insert(0, naakt())


def reset_list():
    session.save_list = []


def main():

    #set the page config
    st.set_page_config(
        layout="wide",
        page_title="Naa.K.T. generator"
    )

    header_body = st.container()
    material_body = st.container()
    save_body = st.container()

    with header_body:
        logo, explain = st.columns(2)
        with logo:
            st.image('Logo NAA.K.T.png')
        with explain:
            st.title("")
            with st.expander('Over NAA.K.T.'):

                naakt_explain = """
                # NAA.K.T. Eenduidige materiaalbenaming
                ## HÉT EZELSBRUGGETJE VOOR EENDUIDIGE MATERIAALBENAMING
                Prefabbeton, gewapend beton, grindbeton, ihw, ihwg of tpg. Zelf snappen we allemaal wat die ander bedoelt, maar onze computers nog steeds niet. Tijd om daarvoor te zorgen. Rondom BIM maakten we in de BIM basis ILS al afspraken met elkaar om eenduidig samen te werken. Nu introduceren we een verdieping op een van die afspraken, in de vorm van eenduidige materiaalbenaming. Zo weten we branchebreed waar we het over hebben. En je computer ook.
    
                ## EENDUIDIGE MATERIAALBENAMING
                Duurzaamheidsspecialisten, leveranciers, ontwikkelaars, bouwers en architecten hebben de handen ineengeslagen en een standaard ontwikkeld waarvan de bibliotheek zó helder en eenvoudig is dat die voor elke BIM-gebruiker duidelijk is, van modelleur tot eindgebruiker. Een eenduidige materiaalbenaming, die generiek genoeg om branchebreed toe te kunnen passen en specifiek genoeg om van toegevoegde waarde te zijn.
    
                ## WAT IS NAA.K.T.?
                Het aanhouden van een vaste volgorde in de naamgeving zorgt voor betrouwbare data. Maar hoe onthoud je die volgorde? Simpel, met het ezelsbruggetje NAA.K.T.: NAAm_Kenmerk_Toepassing. In drie makkelijk te onthouden stappen leg je de essentie van een materiaal voortaan altijd helder en eenduidig vast.
                
                [Link naar meer informatie op de BIM Basis ILS site](https://www.bimloket.nl/p/682/1-NAAKT-Eenduidige-materiaalbenaming)
                
                """
                st.markdown(naakt_explain)


    with material_body:

        st.code(naakt())
        # build up main selectors in 3 big columns and 2 small columns for the '_'
        col_reset, col1, col2, col3, col_save = st.columns([1, 4, 4, 4, 1])
        with col1:
            naam = st.selectbox('Naam', options=database()['Naam'].unique(), label_visibility='collapsed', key='naam_gekozen', on_change=callback_naam)

        with col2:
            st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(), label_visibility='collapsed', key='kenmerk_gekozen')

        with col3:
            st.selectbox('Toepassing', options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(), label_visibility='collapsed', key='toepassing_gekozen')

        with col_reset:
            st.button('Reset', key='reset_pressed', on_click=reset)

        with col_save:
            st.button('Save', key='save_pressed', on_click=save)

    with save_body:
        st.title('')
        st.markdown('---')

        if 'save_list' in session:
            left, saved_list, right = st.columns([1, 4, 9])
            with saved_list:
                for s in session.save_list:
                    st.code(s)
            with left:
                st.button('Empty', key='reset_list_pressed', on_click=reset_list)


if __name__ == "__main__":
    main()