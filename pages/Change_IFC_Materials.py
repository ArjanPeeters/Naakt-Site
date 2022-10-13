import streamlit as st
import ifcopenshell
import ifcopenshell.util.element as ue
from HomePage import database, naakt, callback_naam
import pandas as pd
from easygui import filesavebox

session = st.session_state


def callback_upload():
    st.sidebar.success('file geüpload')
    session['is_file_uploaded'] = True
    session['ifc_file'] = ifcopenshell.file.from_string(session['uploaded_file'].getvalue().decode('utf-8'))


def change():
    if 'material_changes' not in session:
        session['material_changes'] = {}
    session['material_changes'][session['material_choice']] = naakt()
    st.sidebar.success('{old} -> {new}'.format(old=session['material_choice'], new=naakt()))
    session['materials'].change_name(session['material_choice'], naakt())


def save_to_file():
    filename = session['uploaded_file'].name # [:-4]
    print(filename)
    new_filename = filesavebox(title='Save IFC', default="{}_aangepast.ifc".format(filename),
                               filetypes=['ifc'])
    if new_filename is not None:
        with st.spinner('saving...'):
            session['ifc_file'].write(new_filename)
        st.balloons()


class Materials:

    def get_materials(self) -> dict:
        materials_dict = {}
        with st.spinner('Materialen ophalen...'):
            for material in session['ifc_file'].by_type('IfcMaterial'):
                materials_dict[material.Name] = material
        st.sidebar.success('Geladen')
        return materials_dict

    def __init__(self):
        self.data = self.get_materials()
        self.material_names = list(self.data.keys())

    def change_name(self, old_name, new_name):
        if old_name in self.data.keys():
            self.data[old_name].Name = new_name
        else:
            st.error(f'{old_name} bestaat niet')


def main():
    st.set_page_config(
        layout="wide",
        page_title="Change IFC Materials"
    )
    loading_placeholder = st.empty()
    st.header('Verander de materialen NAA.K.T. benamingen' if 'is_file_uploaded' not in session else
              "{name} - {longname}".format(name=session['ifc_file'].by_type('IfcProject')[0].Name,
                                           longname=session['ifc_file'].by_type('IfcProject')[0].LongName))

    file_uploader = st.sidebar.file_uploader('Kies een IFC file', type=['ifc', 'ifczip'], key='uploaded_file',
                                             on_change=callback_upload)

    if 'is_file_uploaded' in session and session['is_file_uploaded']:

        if 'material_choice' in session:
            material_body = st.container()

            with material_body:
                st.header("change: {} --->".format(session.material_choice))
                st.header(naakt())
                # build up main selectors in 3 big columns and 2 small columns for the '_'
                col_naam, col_kenmerk, col_toepassing, col_save = st.columns([4, 4, 4, 1])

                with col_naam:
                    naam = st.selectbox('Naam', options=database()['Naam'].unique(), label_visibility='collapsed',
                                        key='naam_gekozen', on_change=callback_naam)

                with col_kenmerk:
                    st.selectbox('Kenmerk', options=database().loc[database()['Naam'] == naam, 'Kenmerk'].unique(),
                                 label_visibility='collapsed', key='kenmerk_gekozen')

                with col_toepassing:
                    st.selectbox('Toepassing',
                                 options=database().loc[database()['Naam'] == naam, 'Toepassing'].unique(),
                                 label_visibility='collapsed', key='toepassing_gekozen')

                with col_save:
                    st.button('Change', key='save_pressed', on_click=change)

        session['materials'] = Materials()
        st.radio('kies', session['materials'].material_names, key='material_choice')

        st.sidebar.button('save to IFC', on_click=save_to_file)

        #st.write(session.material_changes)



if __name__ == "__main__":
    main()