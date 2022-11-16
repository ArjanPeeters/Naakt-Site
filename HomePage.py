import streamlit as st
import pandas as pd
import ifcopenshell
import ifcopenshell.util.element as ue
import csv
import pyairtable as at

session = st.session_state


@st.experimental_singleton
def table():
    return at.Table(
        api_key=st.secrets['airtable_key'],
        base_id=st.secrets['naakt_db'],
        table_name='Naakt DB'
    )


def database():
    if 'database' not in session:
        path = 'NAAkt uitgebreid.json'
        session['database'] = pd.read_json(path)

    return session['database']


def callback_upload():
    session['is_file_uploaded'] = True
    try:
        session['ifc_file'] = ifcopenshell.file.from_string(session['uploaded_ifc_file'].getvalue().decode('utf-8'))
    except AttributeError:
        st.error('Upload nieuwe file')


def change(old=None, new=None):
    old_material = old if old is not None else session['material_choice']
    new_material = new if new is not None else naakt()

    if 'material_changes' not in session:
        session['material_changes'] = {}
    session['material_changes'][old_material] = new_material
    st.success('{old} -> {new}'.format(old=old_material, new=new_material))
    session['materials'].change_name(old_material, new_material)

    split_name = new_material.split('_')
    send_dict = {}
    _keys = ['naam', 'kenmerk', 'toepassing', 'extra_veld1', 'extra_veld2', 'extra_veld3']
    for field in range(len(split_name)):
        send_dict[_keys[field]] = split_name[field]
    send_dict['oude_benaming'] = old_material
    send_dict['benaming'] = new_material
    table().create(send_dict)


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


def upload_changes():
    change_dict = pd.read_csv(session['uploaded_csv_file']).to_dict('records')
    counter = 0
    for material_change in change_dict:
        change(old=material_change['oud'], new=material_change['nieuw'])
        counter += 1

    st.success(f'{counter} materialen aangepast')


def file_uploaded():
    if 'is_file_uploaded' in session and session['uploaded_ifc_file'] is not None:
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
        if old_name in self.material_names:
            self.data[old_name].Name = new_name

            if 'changed_items' not in session:
                session['changed_items'] = {}
            session['changed_items'][old_name] = new_name
        elif new_name in self.material_names:
            st.warning(f'{old_name} is al aangepast voor {new_name}')
        else:
            st.error(f'{old_name} bestaat niet')


def main():
    st.set_page_config(
        layout="wide",
        page_title="Naa.K.T. generator")

    header_body = st.container()
    material_body = st.container()
    save_body = st.container()

    st.sidebar.image('Logo NAA.K.T.png')
    st.sidebar.write('maak een NAA.K.T materiaal benaming aan')
    st.sidebar.write('of verander materialen van een ifc')
    st.sidebar.file_uploader('upload ifc', type=['ifc', 'ifczip'], key='uploaded_ifc_file',
                             on_change=callback_upload, label_visibility='collapsed')
    sidebar_downloader = st.sidebar.container()  # for later filling with download buttons
    st.sidebar.markdown('---')
    st.sidebar.write('made by')
    st.sidebar.write(f"primaryColor; {st.get_option('theme.primaryColor')}")

    if not file_uploaded():
        with header_body:
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
        with header_body:

            st.header("{name} - {longname}".format(name=session['ifc_file'].by_type('IfcProject')[0].Name,
                                                   longname=session['ifc_file'].by_type('IfcProject')[0].LongName))
            if 'material_choice' in session:
                st.subheader('Verander: ' + session['material_choice'])
                st.subheader('Naar: ' + naakt())
            else:
                st.subheader('Kies een materiaal')

    with material_body:

        if not file_uploaded():
            st.code(naakt())
        # build up main selectors in 3 big columns and 2 small columns for the '_'
        col1, col2, col3, col_plus, col_button = st.columns([4, 4, 4, 1, 2])
        with col1:
            naam = st.selectbox('Naam', options=database()['Naam'].unique(), label_visibility='collapsed',
                                key='naam_chosen', on_change=callback_naam)
            if 'added_columns' in session and session['added_columns'] > 0:
                st.text_input('vul in:', value='extra-veld-1', key='extra_field1', label_visibility='collapsed')

        with col2:
            st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(),
                         label_visibility='collapsed', key='kenmerk_chosen')
            if 'added_columns' in session and session['added_columns'] > 1:
                st.text_input('test', value='extra-veld-2', key='extra_field2', label_visibility='collapsed')

        with col3:
            st.selectbox('Toepassing', options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(),
                         label_visibility='collapsed', key='toepassing_chosen')
            if 'added_columns' in session and session['added_columns'] > 2:
                st.text_input('test', value='extra-veld-3', key='extra_field3', label_visibility='collapsed')

        with col_plus:
            st.button('+', key='plus_pressed', on_click=plus_pressed)
            if 'added_columns' in session and session['added_columns'] > 0:
                st.button('-', on_click=min_pressed)

        with col_button:
            if not file_uploaded():
                st.button('Save', key='save_pressed', on_click=save)
                st.checkbox('reset on save', key='reset on save')
            else:
                st.button('Change', key='change_pressed', on_click=change)

    if file_uploaded():
        session['materials'] = Materials()
        st.radio('kies', session['materials'].material_names, key='material_choice')

        download_ready = sidebar_downloader.button('Maak IFC download aan')
        if download_ready:
            filename = f'{session.uploaded_ifc_file.name[:-4]}_aangepast.ifc'
            data = session['ifc_file'].to_string()
            sidebar_downloader.download_button(label='download IFC', data=data, mime='text/plain',
                                       file_name=filename)

        col_upload_changes, col_download_changes = st.columns(2)

        with col_upload_changes:
            st.write('Upload csv bestand met aanpassingen')
            st.file_uploader('upload csv', key='uploaded_csv_file', type=['.txt', '.csv'],
                             on_change=upload_changes, label_visibility='collapsed')

        if 'changed_items' in session:
            with col_download_changes:
                st.write('download aanpassingen voor hergebruik')
                temp_dict = {'oud': session['changed_items'].keys(), 'nieuw': session['changed_items'].values()}
                csv_file = pd.DataFrame(temp_dict).to_csv().encode('utf-8')
                fn = f'Aanpassingen_{session.uploaded_ifc_file.name[:-4]}.csv'
                st.download_button(label='download aanpassingen', data=csv_file, mime='application/octet-stream',
                                   file_name=fn)
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

    # st.write(session)


if __name__ == "__main__":
    main()
