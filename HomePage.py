import streamlit as st
import pandas as pd
import ifcopenshell
import ifcopenshell.util.element as ue

session = st.session_state


def database():
    if 'database' not in session:
        path = 'NAAkt uitgebreid.json'
        session['database'] = pd.read_json(path)

    return session['database']


def callback_upload():
    session['is_file_uploaded'] = True
    try:
        session['ifc_file'] = ifcopenshell.file.from_string(session['uploaded_file'].getvalue().decode('utf-8'))
    except AttributeError:
        st.error('Upload nieuwe file')

def change():
    if 'material_changes' not in session:
        session['material_changes'] = {}
    session['material_changes'][session['material_choice']] = naakt()
    st.sidebar.success('{old} -> {new}'.format(old=session['material_choice'], new=naakt()))
    session['materials'].change_name(session['material_choice'], naakt())


def naakt(return_dict=None):
    naam = session['naam_chosen'] if 'naam_chosen' in session else ''
    kenmerk = session['kenmerk_chosen'] if 'kenmerk_chosen' in session else ''
    toepassing = session['toepassing_chosen'] if 'toepassing_chosen' in session else ''
    ef1 = '_' + session['extra_field1'].lower().replace(' ', '-') if 'extra_field1' in session else ''
    ef2 = '_' + session['extra_field2'].lower().replace(' ', '-') if 'extra_field2' in session else ''
    ef3 = '_' + session['extra_field3'].lower().replace(' ', '-') if 'extra_field3' in session else ''
    if return_dict:
        return {
            'naam': naam,
            'kenmerk': kenmerk,
            'toepassing': toepassing,
            'extra_veld1': ef1,
            'extra_veld2': ef2,
            'extra_veld3': ef3
        }
    else:
        return f'{naam}_{kenmerk}_{toepassing}{ef1}{ef2}{ef3}'


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
        session['added_columns'] -= 1


def save():
    if 'save_list' not in session:
        session.save_list = []
    session.save_list.insert(0, naakt())


def reset_list():
    session.save_list = []


def file_uploaded():
    if 'is_file_uploaded' in session and session['uploaded_file'] is not None:
        return True
    else:
        return False


class Materials:

    def get_materials(self) -> dict:
        materials_dict = {}
        with st.spinner('Materialen ophalen...'):
            for material in session['ifc_file'].by_type('IfcMaterial'):
                materials_dict[material.Name] = material
        return materials_dict

    def __init__(self):
        self.data = self.get_materials()
        self.material_names = list(self.data.keys())

    def change_name(self, old_name, new_name):
        if old_name in self.data.keys():
            self.data[old_name].Name = new_name

            if 'changed_items' not in session:
                session['changed_items'] = {}
            session['changed_items'][old_name] = new_name
        else:
            st.error(f'{old_name} bestaat niet')


def main():

    st.set_page_config(
        layout="wide",
        page_title="Naa.K.T. generator")

    header_body = st.container()
    material_body = st.container()
    save_body = st.container()

    st.sidebar.write('maak een NAAK.K.T materiaal benaning aan')
    st.sidebar.write('of verander materialen van een ifc')
    st.sidebar.file_uploader('upload ifc', type=['ifc', 'ifczip'], key='uploaded_file',
                             on_change=callback_upload, label_visibility='collapsed')

    if not file_uploaded():
        with header_body:
            st.image('Logo NAA.K.T.png')
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
    else:
        st.header('Verander de materialen NAA.K.T. benamingen' if 'is_file_uploaded' not in session else
                  "{name} - {longname}".format(name=session['ifc_file'].by_type('IfcProject')[0].Name,
                                               longname=session['ifc_file'].by_type('IfcProject')[0].LongName))


    with material_body:

        st.code(naakt())
        # build up main selectors in 3 big columns and 2 small columns for the '_'
        col1, col2, col3, col_plus, col_button = st.columns([4, 4, 4, 1, 1])
        with col1:
            naam = st.selectbox('Naam', options=database()['Naam'].unique(), label_visibility='collapsed', key='naam_chosen', on_change=callback_naam)
            if 'added_columns' in session and session['added_columns'] > 0:
                st.text_input('vul in:', value='extra-veld-1', key='extra_field1', label_visibility='collapsed')

        with col2:
            st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(), label_visibility='collapsed', key='kenmerk_chosen')
            if 'added_columns' in session and session['added_columns'] > 1:
                st.text_input('test', value='extra-veld-2', key='extra_field2', label_visibility='collapsed')

        with col3:
            st.selectbox('Toepassing', options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(), label_visibility='collapsed', key='toepassing_chosen')
            if 'added_columns' in session and session['added_columns'] > 2:
                st.text_input('test', value='extra-veld-3', key='extra_field3', label_visibility='collapsed')

        with col_plus:
            st.button('+', key='plus_pressed', on_click=plus_pressed)
            if 'added_columns' in session and session['added_columns'] > 0:
                st.button('-', on_click=min_pressed)

        with col_button:
            if not file_uploaded():
                st.button('Save', key='save_pressed', on_click=save)
            else:
                st.button('Change', key='change_pressed', on_click=change)

    if file_uploaded():
        session['materials'] = Materials()
        st.radio('kies', session['materials'].material_names, key='material_choice')

        download_ready = st.sidebar.button('Maak IFC download aan')
        if download_ready:
            filename = f'{session.uploaded_file.name[:-4]}_aangepast.ifc'
            data = session['ifc_file'].to_string()
            st.sidebar.download_button(label='download IFC', data=data, mime='text/plain',
                                       file_name=filename)
        if 'changed_items' in session:
            st.subheader('Aangepaste materialen:')
            st.write('Oud: Nieuw')
            st.write(session['changed_items'])

    else:
        with save_body:
            st.title('')
            st.markdown('---')

            if 'save_list' in session:
                left, saved_list, right = st.columns([2, 8, 2])
                with saved_list:
                    for s in session.save_list:
                        st.code(s)
                with left:
                    st.button('Empty', key='reset_list_pressed', on_click=reset_list)




if __name__ == "__main__":
    main()