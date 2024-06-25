import platform
import time
import datetime
import streamlit as st
import re
from src.data_logger import CSVLogger, MySQLLogger
from src.var_lists import ActualVariables as ActVar

st.set_page_config(page_title="Manage db connection", page_icon="🗄️", layout='wide')
st.header("Database and test initialization page", divider=True)

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()

if 'DB_initialized' not in st.session_state:
    st.session_state['DB_initialized'] = False
if 'DB_log_tables' not in st.session_state:
    st.session_state['DB_log_tables'] = ActVar.log_tables_init_vals

st.session_state['all_table_headers'] = {'test_1': ActVar.t1_db_table_headers,
                                         'test_2': ActVar.t2_db_table_headers,
                                         'semantic_vectors': ActVar.vector_emb_table_headers}

st.write("**You must:** 1️⃣ First set up the method for database and if you don't use .csv 2️⃣ secondly map/create tables for results. (optional) 3️⃣ Set a sessionID if you don't want to use automatic one.")


with st.container(border=True):
    st.markdown("#### Database credentials setup :key:")
    db_options = ['Backend', 'User', '.csv']
    db_options_captions = ["Use Tapio's DB if you have access to it", "Use your own MySQL DB", "Don't use DB but use .csv instead"]
    user_db_host, user_db_database, user_db_user, user_db_pass = "", "", "", ""
    col1, col2 = st.columns(2)
    with col1:
        db_sel = st.radio("Choose method for logging results", options=db_options, captions=db_options_captions)
    with col2:
        if db_sel == db_options[0]:
            try:
                if platform.uname().node == st.secrets['LOCAL_LAPTOP']:
                    st.write("Password not needed while running in local system")
                    got_pass_try = st.secrets['BACKEND_DB_PASS']
                else:
                    got_pass_try = st.text_input(label="Type password here to access backend storage", type='password')
            except KeyError as e:
                st.error(f"Backend database not available at the moment due to this error:\n{e}")
        elif db_sel == db_options[1]:
            st.warning("This approach hasn't been tested yet. You will be prompted result whatever the connection is successful or not.")
            user_db_host = st.text_input(label="Type your DB host:", placeholder="localhost")
            user_db_user = st.text_input(label="Type your DB username:", placeholder="testUser")
            user_db_pass = st.text_input(label="Type your DB password:", placeholder="xyz123")
            user_db_database = st.text_input(label="Type your database's name:", placeholder="mysql_database")
        elif db_sel == db_options[2]:
            st.warning("Without use of DB, all the data will be lost if not saved within the session! I.e. if you "
                       "update page without manually saving results, those results will be lost.", icon="⚠️")

    if st.button(label="Initialize connection", key="db_settings_set", type='primary'):
        if db_sel == db_options[0]:  # Backend
            if got_pass_try not in st.secrets:
                st.error("INCORRECT PASSWORD. Try again")
            else:
                try:
                    st.session_state['DB_connection'] = MySQLLogger(host=st.secrets[got_pass_try]['MYSQL_HOST'],user=st.secrets[got_pass_try]['MYSQL_USER'],password=st.secrets[got_pass_try]['MYSQL_PASSWORD'],database=st.secrets[got_pass_try]['MYSQL_DATABASE'])
                    st.session_state['DB_sel'] = db_sel
                    st.session_state['DB_initialized'] = True
                    st.write("✅ DB credentials saved successfully!")
                except Exception as ex:
                    st.error(f"Database connection failed due to this error:\n{ex}")
        elif db_sel == db_options[1]:  # user's database
            db_config = {"db_sel": db_sel,
                         "user_db_url": user_db_host,
                         "user_db_user": user_db_user,
                         "user_db_pass": user_db_pass}
            if user_db_host == "" or user_db_database == "" or user_db_user == "" or user_db_pass == "":
                st.error("You must fulfill all the asked variables to be able to create a connection!")
            else:
                try:
                    st.session_state['DB_connection'] = MySQLLogger(host=user_db_host,user=user_db_user,password=user_db_pass,database=user_db_database)
                    st.session_state['DB_sel'] = db_sel
                    st.session_state['DB_initialized'] = True
                    st.write("✅ DB credentials saved successfully!")
                except Exception as ex:
                    st.error(f"Database connection failed due to this error:\n{ex}")
        else:  # .csv option
            st.session_state['DB_sel'] = db_sel
            st.session_state['DB_initialized'] = True
            st.write("✅ DB credentials saved successfully! ❗Remember to save data files before refreshing this session!")



if not st.session_state['DB_initialized']:
    st.write("Database connection not initialized.")
    st.stop()

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = f"test_session_{datetime.date.today()}_at_{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}"

if st.session_state['DB_sel'] == '.csv':
    st.write("Chosen logging method is .csv. You can save the .csv files from each testing page.")
    st.stop()

if any(value == "" for value in st.session_state['DB_log_tables'].values()):
    st.warning("""Result logging tables has not been set! Create new tables from below or set a existing tables for result logging.""", icon='❗')
else:
    st.info(f"Current tables for logging results: {st.session_state['DB_log_tables']}")

testcol1, testcol2, testcol3, testcol4 = st.columns((0.2, 0.2, 0.2, 0.4))
with testcol1:
    test_con_but = st.button("Test connection")
with testcol2:
    refresh_but = st.button("Refresh connection")
with testcol3:
    close_con_but = st.button("Close connection")
with testcol4:
    if test_con_but:
        try:
            if st.session_state['DB_connection'].connection_available():
                st.write("✅ DB is available.")
            else:
                st.write("❌ DB is not available! Initialize connection again.")
        except Exception as e:
            st.error(f"❌ DB is not available and you should initialize connection again. This error occurred: {e}")
    if refresh_but:
        try:
            if st.session_state['DB_connection'].connection_available():
                st.session_state['DB_connection'].update_tables_and_headers_vars()
                st.write("🔃 Refreshing connection...")
                time.sleep(2)
                st.rerun()
            else:
                st.write("❌ DB is not available! Initialize connection again.")
        except Exception as e:
            st.error(f"❌ DB is not available and you should initialize connection again. This error occurred: {e}")
    if close_con_but:
        st.session_state['DB_connection'].close_connection()
        st.session_state.pop('DB_connection')
        st.session_state['DB_initialized'] = False
        st.session_state['DB_log_tables'] = ActVar.log_tables_init_vals
        st.warning("Connection closed")
        time.sleep(2)
        st.rerun()


with st.expander("**See current tables in database:**"):  # Show tables
    st.write("##### Current tables and their headers in the connected database:")
    headers_dict = st.session_state['DB_connection'].get_tables_and_headers()
    st.table({"Table name": list(headers_dict.keys()), "Table's headers": [", ".join(heads) for heads in headers_dict.values()]})


with st.container(border=True):  # Create or set a table
    st.write("#### Create or define results logging tables")
    st.write(f"At least these tables must be initialized: {', '.join(list(st.session_state['DB_log_tables'].keys()))}")
    with st.expander("See info about table requirements:"):
        st.table({"For what:": list(st.session_state['all_table_headers'].keys()), "With headers (header_name: data_type):": list(st.session_state['all_table_headers'].values())})
    if len(st.session_state['DB_connection'].get_tables_and_headers()) == 0:
        st.write("No tables in database. You must create them.")
        options = ['New table']
    else:
        options = ['New table', 'Existing table']

    for one in list(st.session_state['DB_log_tables'].keys()):
        setcol1, setcol2 = st.columns([0.3,0.7])
        with setcol1:
            new_or_old = st.radio(label=f"Choose method for **{one}**-table:", options=options, horizontal=True, key='radio_sel_'+one)
        with setcol2:
            if new_or_old == 'New table':
                st.text_input(label=f"Type a name for the **{one}**-table:", placeholder=f"Table_for_{one}", key='name_text_'+one)
            else:
                st.write("Please make sure that the table has exactly the same headers than required.")
                db_table_name = st.selectbox(label=f"Select what table to use as **{one}**-table:", options=list(st.session_state['DB_connection'].get_tables_and_headers().keys()), key='table_select_'+one)
                if st.session_state['DB_connection'].get_tables_and_headers()[db_table_name] != list(st.session_state['all_table_headers'][one].keys()):
                    st.warning("Cannot use this table because of invalid headers! See the headers above.")
    if st.button("Use these", type='primary'):
        errors = []
        for second in list(st.session_state['DB_log_tables'].keys()):
            try:
                if st.session_state['radio_sel_'+second] == 'New table':
                    name = st.session_state['name_text_'+second]
                    st.session_state['DB_connection'].ensure_table_exists(table_name=name, headers=st.session_state['all_table_headers'][second])
                    st.session_state['DB_log_tables'][second] = name
                else:
                    st.session_state['DB_log_tables'][second] = st.session_state['table_select_'+second]
            except Exception as err:
                errors.append(f"Error while logging {second}-table: {err}")
                continue
        if len(errors) == 0:
            st.write("✅ All result logging tables set successfully.")
        else:
            text_errors = '\n\n'.join(errors)
            st.error(f"Got these errors:\n\n {text_errors}")


with st.container(border=True):  # Modify session id
    st.write("##### Modify session ID:")
    st.write(f"Current session id: {st.session_state['session_id']}")
    st.write(f"Requirements for session id: max length is 100 char and allowed characters are A-Ö, a-ö, _, -, 0-9")
    modified_id = st.text_input(label="Type your session ID here:", placeholder="session_X...", key="sessionidmodifier", max_chars=100)
    modified_id = modified_id.replace(" ", "_")
    modified_id = re.sub('[^a-zA-Z0-9ÄäÖö_-]+', '', modified_id)
    if st.button("Use this session id", type='primary'):
        st.session_state['session_id'] = modified_id
        st.rerun()


with st.container(border=True):  # Fetch all data from one table
    st.write("##### Fetch data from specific table:")
    table_to_query = st.selectbox(label="Select table:", options=list(st.session_state['DB_connection'].get_tables_and_headers().keys()))
    if st.button(f"Fetch data", type='primary'):
        try:
            data = st.session_state['DB_connection'].read_from(table_name=table_to_query)
            st.write(data)
        except Exception as fe:
            st.error(f"Got this error while trying to fetch data: {fe}")


with st.container(border=True):  # write data to one table for a test
    st.write("##### Write data to specific table (as a test):")
    data_to_table = st.selectbox(label="Select table where to add data:",options=list(st.session_state['DB_connection'].get_tables_and_headers().keys()))
    to_edit_cols = st.session_state['DB_connection'].get_tables_and_headers()[data_to_table]

    row = st.data_editor(data={col: "" for col in to_edit_cols})
    if st.button("Send data to db", type='primary'):
        try:
            st.session_state['DB_connection'].log(table_name=data_to_table, data=row)
            st.write("✅ Data wrote successfully.")
            time.sleep(2)
            st.rerun()
        except Exception as ie:
            st.error(f"Got this error while trying to log data into database: {ie}")



with st.container(border=True):  # Remove one table from db
    st.write("##### Remove specific table from database")
    to_remove = st.selectbox(label="Select what table to remove:", options=list(st.session_state['DB_connection'].get_tables_and_headers().keys()))
    if st.button("Remove table and its data permanently.", type='primary'):
        st.session_state['DB_connection'].remove_table(table_name=to_remove)
        st.write("✅ Table removed successfully.")
        time.sleep(2)
        st.rerun()
