import streamlit as st
import platform
import time
from src.llm_handler import LLMInfo, OpenAILLMService, Text2Token

st.set_page_config(page_title="LLM set-up", page_icon="🤖", layout='wide')
st.title('Setup LLM access :clipboard:')

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()

if 'DB_initialized' not in st.session_state or 'DB_sel' not in st.session_state or not st.session_state['DB_initialized']:
    st.warning("Database not initialized or .csv not chosen for logging method. Fix settings in 'Database manager'-page.")
    st.stop()

if st.session_state['DB_sel'] != '.csv':
    if 'DB_log_tables' not in st.session_state or any(value == "" for value in st.session_state['DB_log_tables'].values()):
        st.warning("Logging tables not set for result logging. Fix settings in 'Database manager'-page.")
        st.stop()

if 'files_dict' not in st.session_state or len(st.session_state['files_dict']) == 0:
    st.warning("No files detected in memory. Upload one or two files for analysing in 'Doc and text handling'-page.")
    st.stop()

st.write("**1️⃣ First set up API access keys and 2️⃣ then choose LLM model from below**")

llm_api_options = ['Backend', 'User']
llm_api_options_captions = ["Use Tapio's key if you have access to it", "Provide your own key"]
llm_endpoint_options = ["OpenAI", "Azure (in future)"]
ownkey_sel, endpoint_sel, user_openai_key, user_endpoint_key, user_endpoint_versio = llm_api_options[0], llm_endpoint_options[0], "", "", ""

with st.container(border=True):
    st.header("OpenAI's API credentials setup :key:")

    col1, col2 = st.columns(2)
    with col1:
        ownkey_sel = st.radio("Choose source for OPENAI API key", options=llm_api_options,captions=llm_api_options_captions)
        endpoint_sel = st.radio("Choose your API endpoint. Defaults to OpenAI when backend's key is used.", options=llm_endpoint_options,
            disabled=False if ownkey_sel == llm_api_options[1] else True, index=0 if ownkey_sel == llm_api_options[1] else 0)

    with col2:
        if ownkey_sel == llm_api_options[0]:
            try:
                if platform.uname().node == st.secrets['LOCAL_LAPTOP']:
                    st.write("Password not needed while running in local system")
                    llm_pass_try = st.secrets['BACKEND_LLM_PASS']
                else:
                    llm_pass_try = st.text_input(label="Type password here to access backend storage", type='password')
            except KeyError as e:
                st.error(f"Backend database not available at the moment due to this error:\n{e}")

        if ownkey_sel == llm_api_options[1]:
            user_openai_key = st.text_input(label="Type your OpenAI API key here:", placeholder="sk-...", type='password')

        if endpoint_sel == llm_endpoint_options[1] and ownkey_sel == llm_api_options[1]:
            st.info("Will be implemented later.")
            #user_endpoint_key = st.text_input(label="Type your Azure OpenAI endpoint key here:")
            #user_endpoint_versio = st.text_input(label="Type your Azure OpenAI API version here:")

    if st.button(label="Use these settings", key="llm_settings_set", type='primary'):
        if ownkey_sel == 'Backend':
            if llm_pass_try not in st.secrets:
                st.error("INCORRECT PASSWORD. Try again")
            else:
                try:
                    backapikey = st.secrets[llm_pass_try]['OPENAI_API_KEY']
                    st.session_state['LLM_credentials'] = {"openai_key_sel": "Backend",
                                                           "openai_key": backapikey,
                                                           "openai_endpoint_sel": 'OpenAI',
                                                           "endpoint_key": "",
                                                           "endpoint_versio": ""}
                    st.write("✅ Settings saved successfully!")
                    time.sleep(2)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Backend LLM not available currently due to this error:\n{ex}")
        else:
            endpoint_sel = llm_endpoint_options[0] if ownkey_sel == llm_api_options[0] else endpoint_sel
            st.session_state['LLM_credentials'] = {"openai_key_sel": ownkey_sel,
                                               "openai_key": user_openai_key,
                                               "openai_endpoint_sel": endpoint_sel,
                                               "endpoint_key": user_endpoint_key,
                                               "endpoint_versio": user_endpoint_versio}

            valid_llm_settings = True
            if ownkey_sel == llm_api_options[1]:
                if endpoint_sel == llm_endpoint_options[0] and user_openai_key == "":
                    valid_llm_settings = False
                    warning_message = "You chose to use your own API key but left it unset thus preventing LLM connection to work!"
                elif endpoint_sel == llm_endpoint_options[1] and (
                        user_openai_key == "" or user_endpoint_key == "" or user_endpoint_versio == ""):
                    valid_llm_settings = False
                    warning_message = "You chose to use your own API key and Azure endpoint but didn't set required variables thus preventing LLM connection to work!"

            if valid_llm_settings:
                st.write("✅ Settings saved saved successfully!")
            else:
                st.warning(warning_message, icon="⚠️")
            time.sleep(2)
            st.rerun()


final_json_structure = {'Information': "THIS JSON CONTAINS THE FILES FOR YOU TO HANDLE", 'Files': []}
for file_name, file_text in st.session_state['files_dict'].items():
    final_json_structure['Files'].append({
        'name_of_the_file': file_name,
        'text_of_the_file': file_text})

st.session_state['user_prompt'] = str(final_json_structure)
est_file_tokens = Text2Token().num_of_tokens_in_text(st.session_state['user_prompt'])

if est_file_tokens + 1000 < min(list(LLMInfo.token_limits.values())):
    st.info(f"The files you uploaded will consume {est_file_tokens} tokens, system message consumes about 500 tokens, "
            f"and LLM's answer takes about 500 tokens. This can be handled by all of the available models.")
else:
    st.warning(f"**Note the token limits!** The files you uploaded will consume **{est_file_tokens}** tokens. System "
               f"message consumes about 500 tokens. Remember to leave at least 500 tokens for LLM's answer. Thus chosen "
               f"model's token limit should be at least **{est_file_tokens+1000}** tokens.", icon='❗')

with st.expander("See standard user message:"):
    with st.container(height=300):
        st.json(st.session_state['user_prompt'])

with st.expander("See information about available models:"):
    st.table(data=LLMInfo().get_info_dict())

cont1 = st.container(border=True)
with cont1:
    st.header(f"Select model and initialize connection 🤖")
    st.markdown(f"⚠️ Only the newest models ({', '.join(LLMInfo.supports_json_response)}) support the JSON response format, and these models are recommended for reducing errors in the format of answers.")

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox("Select model to use:", options=LLMInfo.allowed_models)
        st.info(f"""**Selected models token limit is: {LLMInfo.token_limits[model]}**  
                    Estimated cost of reading the files once with selected model is {round(LLMInfo().estimate_cost(model=model, prompt=est_file_tokens, output=500), 3)} $.""")
    with col2:
        temperature = st.number_input("Choose temperature for the model between 0 and 2 with two decimals.",
                                      min_value=0.00, max_value=2.00, value=0.50, )
        st.info("Guide: lower value gives stricter and more precise answers. Recommended value is between 0 and 1.")

    if 'LLM_credentials' not in st.session_state or st.session_state['LLM_credentials'].get('openai_key', '') == '':
        st.warning(f"⚠️ Please set LLM credentials first!")
    elif est_file_tokens > LLMInfo.token_limits[model]:
        st.warning(f"⚠️ Note the token limits!")
    else:
        if st.button("Use these setting and initialize LLM", type='primary'):
            st.session_state["model_attributes"] = {'model': model, 'temperature': temperature}
            try:
                st.session_state["LLM_service"] = OpenAILLMService(api_key=st.session_state['LLM_credentials']['openai_key'],
                            model=st.session_state["model_attributes"]['model'],
                            temperature=st.session_state["model_attributes"]['temperature'])
                st.write("✅ Connection initialized successfully! Still it is recommended to test the connection.")
                st.session_state['test_ready'] = True
            except Exception as llme:
                st.error(f"Initialization failed due to this error: {llme}")


if 'LLM_service' in st.session_state and st.session_state["LLM_service"] is not None:
    test_user_message = "Kerro vitsi joka liittyy rakennusalaan"
    test_system_message = "Olet stand-up koomikko ja käytät Anthony Jeselnikin mukaista tyyliä. Mutta koira olla poliittisesti korrekti. Palauta vastauksesi JSON muodossa."

    st.write(f"You selected {st.session_state['model_attributes']['model']} as model with temperature of {st.session_state['model_attributes']['temperature']} ")

    tcol1, tcol2 = st.columns((0.2, 0.8))
    with tcol1:
        test_conn_but = st.button("Test LLM connection")
        st.markdown(f"Test costs about {round(LLMInfo().estimate_cost(model=st.session_state['model_attributes']['model'], prompt=test_user_message+test_system_message, output=100), 4)} $.")
        close_conn_but = st.button("Close LLM connection")

    with tcol2:
        if test_conn_but:
            try:
                answer, tokens = st.session_state["LLM_service"].query_llm(prompt=test_user_message, system=test_system_message)
                st.write(answer)

                st.write(f"✅ Connection works! Spend {tokens} tokens.")
            except Exception as llmce:
                st.error(f"Quering LLM failed due to this error: {llmce}")
        if close_conn_but:
            st.session_state["LLM_service"] = None
            st.write("Connection closed!")
            time.sleep(2)
            st.rerun()

