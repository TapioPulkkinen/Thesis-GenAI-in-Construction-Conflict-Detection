import streamlit as st

st.header("Ohjeet testipenkkiohjelman käytölle / Instruction for the testbench program")

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()


kontti = st.container(border=True)
with kontti:
    kieli = st.radio(label="**Valitse ohjeiden kieli / Choose instruction's language**", options=["Suomi", "English"],
                 horizontal=True)

if kieli == "Suomi":
    st.markdown("""
**Huomio:** Jos et halua itse lukea ohjeita läpi, voit myös kopioida kaikki tämän sivun ohjeet, antaa ne kielimallille (esim. ChatGPT) ja ohjeistaa sitä opastamaan sinua vaihevaiheelta. 
#### Sisällysluettelo
0. Yleisopas
1. Tietokanta yhteyden luominen

## 0. Yleisopas
- Jos valitset oman tietokannan, käyttäjällä tulee olla luku ja kirjoitusoikeus sen ko. taulukkoon.
- **OpenAI API mallien hinnoittelu:** https://openai.com/pricing
""")

    with st.expander("**1 Tietokanta yhteyden avaaminen**"):
        st.markdown("""
## 1. Tietokanta yhteyden luominen
##### Alkukirjautuminen
Ensimmäinen vaihe: Varmista, että olet kirjautunut sisään, kun saavut tälle sivulle. Sinun tulee kirjautua sisään kotisivulta, jotta voit jatkaa eteenpäin. Jos et ole kirjautunut sisään, virheviesti kehottaa sinua tekemään niin.
Tietokantatunnusten Asetus
Tietokantavaihtoehdot: Tarjolla on kolme menetelmää tulosten kirjaamiseen:

Backend: Käytä määriteltyä taustajärjestelmän tietokantaa, jos sinulla on siihen pääsy. Paikallisissa järjestelmissä salasanaa ei ehkä vaadita, mutta muussa tapauksessa sinun on syötettävä se.
Käyttäjän oma tietokanta: Jos päätät käyttää omaa MySQL-tietokantaasi, sinua pyydetään syöttämään tietokantapalvelimesi osoite, käyttäjänimesi, salasanasi ja tietokantasi nimi. Tämä vaihtoehto on merkitty testaamattomaksi, ja se ilmoittaa, onnistuiko yhteys vai ei.
CSV-tiedosto: Valitse datan kirjaaminen .csv-tiedostoon, jos et halua käyttää tietokantaa. Muista, että data voi kadota, jos sitä ei tallenneta istunnon aikana, erityisesti jos sivu päivitetään ilman manuaalista tallennusta.
Yhteyden alustaminen: Valitse haluamasi menetelmä ja syötä tarvittavat tiedot, ja klikkaa sitten "Alusta yhteys" asettaaksesi yhteyden. Onnistumisviesti vahvistaa, että tunnukset on tallennettu tai ilmoittaa mahdollisista yhteysvirheistä.

#### Istunnon tunnuksen asetus
Oletusarvoisesti sinulle luodaan istunnon tunnus, mutta voit muokata sitä tiettyjen vaatimusten mukaisesti (enintään 100 merkkiä, sallitut merkit sisältävät A-Ö, a-ö, _, -, 0-9). Tämä on tärkeää istuntosi datan ainutlaatuisen seurannan kannalta.
#### Datan ja taulukoiden hallinta
Taulukoiden luominen tai asettaminen: Sinun on joko luotava uusia taulukoita tulosten kirjaamista varten tai asetettava olemassa olevia. Varmista, että ne täyttävät määritellyt vaatimukset. Käyttöliittymä tarjoaa mahdollisuuden valita olemassa oleva taulukko tai syöttää uusi, sekä määritellä sen käyttötarkoituksen.
Yhteyden testaus, päivittäminen ja sulkeminen: Saatavilla on painikkeita tietokantayhteyden testaamiseen, päivittämiseen tai kokonaan sulkemiseen. Nämä ovat hyödyllisiä vianmäärityksessä tai asetustesi nollaamisessa.
Nykyisten taulukoiden katselu: Laajennettavassa osiossa voit nähdä nykyiset taulukot tietokannassa sekä niiden otsikot.
Datan käsittely: Tarjolla on ominaisuuksia datan hakemiseen tietystä taulukosta, testidatan kirjoittamiseen taulukkoon tai taulukon ja sen datan poistamiseen pysyvästi tietokannasta.
#### Lisähuomautukset
Tallenna muutokset pikaisesti: Muista tallentaa kaikki muutokset tai data ennen sivun päivittämistä tai yhteyden sulkemista, jotta vältät datan menetyksen.
Virheet ja vianmääritys: Käyttöliittymä näyttää virheviestejä väärästä syötteestä tai epäonnistuneista toimenpiteistä, ohjaten sinua korjaamaan ongelmat.
    """)

else:
    st.markdown("""
Note: Code all the text from here and pass it to ChatGPT or to any other chat-based LLM and ask it to guide you 
through step by step. 

#### Table of contents
0. General guide
1. Setting up database access

## 0. General guides
- If you choose to use your own database, make sure that the user has read and write rights to that database.
- To find out pricing information about OpenAI's API models, visit this page: https://openai.com/pricing
""")

    with st.expander("**1 Setting up database access**"):
        st.markdown("""
    ## 1. Setting up database access
    #### Initial Login
First Step: Upon accessing this page, ensure you're logged in. You need to log in from the Home-page to proceed further. If not logged in, an error message will prompt you to do so.
Setting Up Database Credentials
Database Options: You're given three methods for logging results:

Backend: Use a specified backend database if you have access. Local systems might not require a password, but otherwise, you'll need to input one.
User's Own Database: If you choose to use your own MySQL database, you'll be prompted to enter your DB host, username, password, and the database's name. This option is noted as untested and will inform you of success or failure in connection.
CSV File: Opt for logging data into a .csv file if you prefer not to use a database. Be mindful that data could be lost if not saved within the session, especially if the page is refreshed without manual saving.
Initializing Connection: After selecting your preferred method and entering any required information, click "Initialize connection" to set up. A success message will confirm the credentials are saved or report any errors in connection.

#### Session ID Setup
By default, a session ID is generated for you, but you can modify it according to specific requirements (max 100 characters, allowed characters include A-Ö, a-ö, _, -, 0-9). This is crucial for tracking your session's data uniquely.
#### Managing Data and Tables
Creating or Setting Tables: You must either create new tables for logging results or set existing ones. Ensure they meet the specified requirements. An interface is provided to either choose an existing table or input a new one, alongside specifying its purpose.
Testing, Refreshing, and Closing Connection: Buttons are available to test the database connection, refresh it, or close it entirely. These are useful for troubleshooting or resetting your setup.
Viewing Current Tables: An expander allows you to see current tables in the database along with their headers.
Data Manipulation: Features are available to fetch data from a specific table, write test data to a table, or remove a table and its data permanently from the database.
#### Additional Notes
Save Changes Promptly: Remember to save any changes or data before refreshing the page or closing the connection to prevent loss of data.
Errors and Troubleshooting: The interface will display error messages for incorrect inputs or failed operations, guiding you to rectify issues.
    """)
