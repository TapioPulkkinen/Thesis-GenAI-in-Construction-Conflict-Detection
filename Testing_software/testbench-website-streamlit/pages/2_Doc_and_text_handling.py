import streamlit as st
from src.file_handler import FileReader


st.set_page_config(page_title="Document loader", page_icon="📁", layout='wide')

st.header("Document loader page", divider=True)

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()

files_dict_max_size = 2
if 'files_dict' not in st.session_state:
    st.session_state['files_dict'] = {}

with st.container(border=True):
    st.write("❗Please **load only 1 or 2 two files**. Also the files must not have exactly the same name.❗")

    uploaded_files = st.file_uploader(label="Choose max 2 files to load for analysis", accept_multiple_files=True,
                                      type=['txt', 'pdf', 'doc', 'docx'])

    if len(uploaded_files) > 2:
        st.error("More than 2 files loaded which isn't allowed. Remove extra files by clicking ✖️-sign to the right of the file's name.", icon="🚨")
    elif len(uploaded_files) == 2 and uploaded_files[0].name == uploaded_files[1].name:
        st.error("Two files loaded with equal names and that isn't allowed. Remove other file by clicking ✖️-sign to the right of the file's name.", icon="🚨")
    elif uploaded_files:
        if st.button("Use file(s)", type='primary'):
            for ind, file in enumerate(uploaded_files):
                text = FileReader().read_file(file)
                # st.session_state['files_dict'][file.name.replace("_", " ")] = text
                key = file.name
                if len(st.session_state['files_dict']) < files_dict_max_size or key in st.session_state['files_dict']:
                    # If there's room or the item is an update, add/replace directly
                    st.session_state['files_dict'][key] = text
                else:
                    # If the dictionary is full and the item is new, remove the oldest and add the new item
                    # Assuming the first key in the iteration order is the oldest
                    oldest_key = next(iter(st.session_state['files_dict']))
                    del st.session_state['files_dict'][oldest_key]
                    st.session_state['files_dict'][key] = text
            st.markdown("✅ Files saved successfully!")


# TEXT MODIFICATION?
st.subheader("Here you can see contents from the saved file(s):")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        try:
            name = list(st.session_state['files_dict'].keys())[0]
            text = list(st.session_state['files_dict'].values())[0]
        except IndexError or KeyError as e:
            name = "Empty"
            text = "Nothing to show here. Load files from above"
        st.subheader(f"File one: _{name.replace('_', ' ')}_")
        with st.container(border=True):
            subcol11, subcol12 = st.columns(2)
            if subcol11.button("Remove this file", key="removefirstfile"):
                try:
                    st.session_state['files_dict'].pop(name)
                    st.rerun()
                except KeyError:
                    st.warning("Nothing to remove!")
            subcol12.write("More functionalities will be added")
        with st.container(border=True, height=500):
            st.subheader(body="Text from the file:", anchor=False, divider='grey')
            st.text(text)

with col2:
    with st.container(border=True):
        try:
            name2 = list(st.session_state['files_dict'].keys())[1]
            text2 = list(st.session_state['files_dict'].values())[1]
        except IndexError or KeyError as e:
            name2 = "Empty"
            text2 = "Nothing to show here. Load files from above"
        st.subheader(f"File two: _{name2.replace('_', ' ')}_")
        with st.container(border=True):
            subcol21, subcol22 = st.columns(2)
            if subcol21.button("Remove this file", key="removesecondfile"):
                try:
                    st.session_state['files_dict'].pop(name2)
                    st.rerun()
                except KeyError:
                    st.warning("Nothing to remove!")
            subcol22.write("More functionalities will be added")
        with st.container(border=True, height=500):
            st.subheader(body="Text from the file:", anchor=False, divider='grey')
            st.text(text2)