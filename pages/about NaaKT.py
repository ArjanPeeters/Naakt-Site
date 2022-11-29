import streamlit as st
from HomePage import sidebar

st.set_page_config(page_title="about Naa.K.T. Materiaal benaming",
                   layout='wide')

st.sidebar.image('Logo NAA.K.T.png')
st.sidebar.markdown('---')
st.sidebar.markdown('&emsp;gemaakt door:')
st.sidebar.image('BIMnerd_Logo.png')
st.sidebar.markdown('---')
st.sidebar.write('Aangemaakte materiaal benamingen worden anoniem opgeslagen voor analyse')

st.header('Over NAA.K.T.')
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