import time
import streamlit as st
import json
import pandas
from src.premade_prompts import PremadeSystemPrompts, PremadeUserPrompts


st.set_page_config(page_title="LLM query", page_icon="🤖", layout='wide')
st.title("Test number 1: LLM conversation")
this_is ='test_1'

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()

if 'test_ready' not in st.session_state or not st.session_state['test_ready']:
    st.warning("You haven't set up all test settings. Database connection, file(s), and LLM connection must be set before starting tests.")
    st.stop()

if 'files_dict' not in st.session_state or len(st.session_state['files_dict']) == 0:
    st.warning("No files detected in memory. Upload one or two files for analysing in 'Doc and text handling'-page.")
    st.stop()

if 'last_llm_ans_saved' not in st.session_state:
    st.session_state['last_llm_ans_saved'] = False

with st.expander(label="**SYSTEM** Prompt management"):
    st.markdown("##### Here you can either select the system prompt from templates OR write/paste your own.")

    system_prompt_options = PremadeSystemPrompts.prompt_options  # Fetch prompt options dictionary {prompt's_name: prompt's_text}
    user_prompt_options = PremadeUserPrompts.prompt_templates  # To be implemented in future

    selected_prompt = st.selectbox("Choose the prompt from these options:", options=list(system_prompt_options.keys()),placeholder="Chooce one...", index=None)

    if 'system_prompt' in st.session_state and st.session_state["system_prompt"]:
        st.write(f"**Previously selected prompt:** {list(st.session_state['system_prompt'].keys())[0]}")

    if selected_prompt:
        cont = st.container(border=True)
        if selected_prompt == "Create_your_own_prompt":
            with cont:
                default_prompt = st.session_state.get("custom_prompt", "")
                st.info("REMEMBER to always instruct the model to return the answer in a JSON format!")
                value = default_prompt if default_prompt != "" else system_prompt_options[selected_prompt]
                user_written_prompt = st.text_area(label="Write or paste your prompt here:", value=value, height=300)
                if st.button("USE YOUR PROMPT", type='primary'):
                    st.session_state["system_prompt"] = {selected_prompt: user_written_prompt}
                    st.session_state["custom_prompt"] = user_written_prompt
                    st.markdown("✅ Selected prompt saved successfully!")
                if default_prompt:
                    st.subheader(f"The prompt you wrote previously:", divider='grey')
                    st.write(st.session_state.get("custom_prompt", ""))
        else:
            with cont:
                if st.button("USE THIS PROMPT", type='primary'):
                    st.session_state["system_prompt"] = {selected_prompt: system_prompt_options[selected_prompt]}
                    st.markdown("✅ Selected prompt saved successfully!")
                st.subheader(f"Prompt's name: {selected_prompt}", divider='grey')
                st.text(system_prompt_options[selected_prompt])


if 'system_prompt' not in st.session_state:
    st.warning("No prompt detected in memory. Choose prompt from above!")
    st.stop()
if len(st.session_state['system_prompt'].values()) == 1:
    sys_prompt = list(st.session_state['system_prompt'].values())[0]
else:
    st.error("Zero or more than one system prompt detected and that is not allowed. Fix the situation from 'Prompt handling'-page or refresh session and start from beginning.")
    st.stop()

st.info("Now you can query the LLM from below to get first results")

butcol1, butcol2, butcol3, butcol4 = st.columns((0.2,0.2,0.2, 0.2))
with butcol1:
    query_but = st.button("Get LLM's answer", key='queryllm')
with butcol2:
    save_but = st.button("Save results", key='saveans')
with butcol3:
    del_but = st.button("Delete last answer", key='delbut')
with butcol4:
    download_but = st.button("Download results", key='loadbut')


if query_but:
    with st.status("Querying LLM...", expanded=False) as status:
        try:
            answer, tokens = st.session_state["LLM_service"].query_llm(prompt=st.session_state['user_prompt'],system=sys_prompt)
            st.session_state['last_llm_ans'] = {'content': answer, 'tokens': tokens}
            st.write("Querying was successful!")
            status.update(label="Answer ready!", state='complete')
            st.session_state['last_llm_ans_saved'] = False
        except Exception as qerr:
            st.error(f"Got this error while querying LLM: {qerr}")
            status.update(label="Got error!", state='error', expanded=True)
if save_but:
    if 'last_llm_ans' in st.session_state and st.session_state['last_llm_ans']['content'] != "":
        if st.session_state['last_llm_ans_saved'] == False:
            data = [st.session_state['session_id'],
                    list(st.session_state['files_dict'].keys())[0],
                    "n/a" if len(list(st.session_state['files_dict'].keys())) < 2 else list(st.session_state['files_dict'].keys())[1],
                    list(st.session_state['system_prompt'].values())[0],
                    "LLM_only",
                    st.session_state["model_attributes"]['model'],
                    st.session_state['last_llm_ans']['tokens'],
                    st.session_state['last_llm_ans']['content']]
            if len(data) != len(st.session_state['all_table_headers'][this_is]):
                st.error("Error in saving. Data and table columns do not match!")
                time.sleep(3)
                st.rerun()
            try:
                if 't1_results_dict' not in st.session_state:
                    st.session_state['t1_results_dict'] = {list(st.session_state['all_table_headers'][this_is].keys())[ind]: [data[ind]] for ind in range(len(data))}
                else:
                    for ind, key in enumerate(list(st.session_state['t1_results_dict'].keys())):
                        st.session_state['t1_results_dict'][key].append(data[ind])
                st.session_state['last_llm_ans_saved'] = True
            except Exception as se:
                st.error(f"Got this error while saving results: {se}")
            if st.session_state['DB_sel'] != '.csv':
                try:
                    st.session_state['DB_connection'].log(table_name=st.session_state['DB_log_tables'][this_is], data=data)
                    st.session_state['last_llm_ans_saved'] = True
                    st.write("✅ Answer saved successfully.")
                except Exception as se:
                    st.error(f"Got this error while logging results: {se}")
        else:
            st.write("Current answer already saved!")
    else:
        st.warning("Nothing to save at the moment.")
if del_but:
    if 'last_llm_ans' in st.session_state and st.session_state['last_llm_ans']['content'] != "":
        st.session_state['last_llm_ans'] = {'content': "", 'tokens': 0}
        st.session_state['last_llm_ans_saved'] = False
if download_but:
    if 't1_results_dict' in st.session_state:
        df = pandas.DataFrame(st.session_state['t1_results_dict'])
        st.download_button(label="Download data as CSV", data=df.to_csv(index=False).encode('utf-8'),file_name=f"{this_is}_results.csv", mime='text/csv', type='primary')
else:
        st.warning("No results saved yet!")

st.divider()
st.write("Remember to save the answer")
if 'last_llm_ans' in st.session_state and st.session_state['last_llm_ans']['content'] != "":
    with st.container(border=True, height=600):
        st.write("##### LLM's answer")
        text_display = st.session_state['last_llm_ans']['content']
        try:
            json_text = json.loads(text_display)
            st.info(f"**INFO** The answer is in correct format (JSON). Tokens used: {st.session_state['last_llm_ans']['tokens']} pcs. LLM found {len(list(json_text.values())[0])} conflicts.")
            st.json(json_text)
        except ValueError as e:
            st.info(f"The answer is not in correct format (JSON). Tokens used: {st.session_state['last_llm_ans']['tokens']} pcs.")
            st.write(text_display)
else:
    st.info("Nothing to show at the moment. Please query LLM first.")
