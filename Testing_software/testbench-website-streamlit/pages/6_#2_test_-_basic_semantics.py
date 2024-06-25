import time
import pandas
import streamlit as st
import json
from src.text_handler import TextEmbedder, EmbeddingInfo, SemanticSearch
from src.premade_prompts import PremadeSystemPromptsForSEMANTICS, PremadeSemanticQuestions


def use_embeddings(results, file_name):
    for result in results:
        st.session_state['curr_semantics'][file_name]['sessionID'].append(result[0])
        st.session_state['curr_semantics'][file_name]['file_name'].append(result[1])
        st.session_state['curr_semantics'][file_name]['split_method'].append(result[2])
        st.session_state['curr_semantics'][file_name]['embed_method'].append(result[3])
        st.session_state['curr_semantics'][file_name]['chunk_number'].append(result[4])
        st.session_state['curr_semantics'][file_name]['num_of_chunks'].append(result[5])
        st.session_state['curr_semantics'][file_name]['original_text'].append(result[6])
        st.session_state['curr_semantics'][file_name]['vector'].append(result[7])


st.set_page_config(page_title="Semantic search", page_icon="", layout='wide')
st.title("Test number 2: Semantic search with LLM")

if 'password_correct' not in st.session_state or not st.session_state['password_correct']:
    st.error("Please login first from Home-page in order to proceed further.")
    st.stop()

if 'test_ready' not in st.session_state or not st.session_state['test_ready']:
    st.warning("You haven't set up all test settings. Database connection, file(s), and LLM connection must be set before starting tests.")
    st.stop()

########################################################################################################################
# EMBEDDING MANAGEMENT
########################################################################################################################

if 'curr_semantics' not in st.session_state:
    st.session_state['curr_semantics'] = {file: {'sessionID': [], 'file_name': [], 'split_method': [], 'embed_method': [], 'chunk_number': [], 'num_of_chunks': [], 'original_text': [], 'vector': []} for file in list(st.session_state['files_dict'].keys())}
if 'temp_db_results' not in st.session_state:
    st.session_state['temp_db_results'] = {}
if 'temp_create_results' not in st.session_state:
    st.session_state['temp_create_results'] = {}
if 'temp_good' not in st.session_state:
    st.session_state['temp_good'] = []

this_is = 'test_2'
vector_table = 'semantic_vectors'
max_chunk_size = 10000

with st.container(border=True):
    st.write("##### 1️⃣ Check if embeddings exists in database:")
    st.write("Note that only one set of embeddings can exist for one file in vector table. This will be corrected in future.")
    if st.session_state['DB_sel'] == '.csv':
        st.write("You must create new embeddings because you chose to use .csv.")
    else:

        if st.button("Search for existing embeddings from DB", disabled=st.session_state['DB_sel'] == '.csv'):
            try:
                for file in list(st.session_state['files_dict'].keys()):
                    res = st.session_state['DB_connection'].find_rows_by_value(table_name=st.session_state['DB_log_tables'][vector_table], column_name="file_name", search_value=file)
                    if res:
                        st.session_state['temp_db_results'][file] = res
                    else:
                        st.session_state['temp_db_results'][file] = []
            except Exception as ferr:
                st.error(f"Results not found because this error occurred while querying database: {ferr}")
                st.session_state['temp_db_results'] = {}

            if any(len(value) > 0 for value in list(st.session_state['temp_db_results'].values())):
                st.session_state['temp_good'] = []
                with st.expander("See results:"):
                    for file in list(st.session_state['temp_db_results'].keys()):
                        diff_embs = set([one[0] for one in st.session_state['temp_db_results'][file]])
                        sm = set([one[2] for one in st.session_state['temp_db_results'][file]])
                        em = set([one[3] for one in st.session_state['temp_db_results'][file]])
                        if len(diff_embs) == 0:
                            st.write(f"❌ No embeddings for file: {file}")
                            st.session_state['temp_good'].append(False)
                        elif len(diff_embs) == 1:
                            st.info(f"✅ good. **Embeddings found for file: {file}**. Splitting_method: {sm} Embedding method: {em}")
                            st.session_state['temp_good'].append(True)
                        else:
                            st.warning(f"❌ Found too many embeddings for file: {file}")
                            st.session_state['temp_good'].append(False)
            else:
                st.warning("No matches with current files. You must create new embeddings.")

    if st.button("Use the good embeddings:", type='primary', disabled=True not in st.session_state['temp_good']):
        for ind, file in enumerate(list(st.session_state['temp_db_results'].keys())):
            if st.session_state['temp_good'][ind]:
                use_embeddings(st.session_state['temp_db_results'][file], file_name=file)
        st.session_state['temp_db_results'] = {}
        st.write("✅ Embeddings saved successfully!")
        time.sleep(2)
        st.rerun()


with st.container(border=True):
    st.write("##### 2️⃣ Create embeddings here")
    embcol1, embcol2, embcol3, = st.columns([0.33,0.33,0.33])
    with embcol1:
        split_method = st.selectbox(label="Choose splitting method", options=EmbeddingInfo().get_splitting_methods())
    with embcol2:
        size = st.number_input(label=f"Choose size for chunk (min=10, max={max_chunk_size})", min_value=100, max_value=max_chunk_size, value=1000)
    with embcol3:
        overlap = st.number_input(label=f"Choose overlap size (min=0, max={int(0.2*max_chunk_size)})", min_value=0, max_value=int(0.2*max_chunk_size), value=50)
    seccol1, seccol2 = st.columns([0.4,0.6])
    with seccol1:
        not_for_all = st.radio(label="Create embeddings for all or only for those that don't have yet?", options=["For those that don't have","For all"], horizontal=True) != 'For all'
    with seccol2:
        st.write("Embedding process is slow and might take a couple of minutes depending on selected settings.")
        create_embs = st.button("Create embeddings")
    if create_embs:
        with st.status("Processing first file", state='running') as create_status:
            try:
                text_embedder = TextEmbedder(openai_key=st.session_state['LLM_credentials']['openai_key'], chunk_size=size, chunk_overlap=overlap, split_method=split_method)
                st.session_state['temp_create_results'] = {}
                nth = 1
                for file, text in list(st.session_state['files_dict'].items()):
                    if not_for_all and len(st.session_state['curr_semantics'][file]['file_name']) != 0:
                        nth += 1
                        continue
                    res = text_embedder.embed_text_into_vectors(text=text)
                    if res:
                        mod_res = [(st.session_state['session_id'], file, one[0], one[1], one[2], one[3], one[4], one[5]) for one in res]
                        st.session_state['temp_create_results'][file] = mod_res
                    st.write(f"{nth}. file ready.")
                    nth += 1
                    create_status.update(label=f"Processing {nth}. file")
                st.write("✅ Embeddings created successfully!")
                create_status.update(label="Embedding ready!", state='complete')
            except Exception as merr:
                st.error(f"Got this error: {merr}")
                create_status.update(label="Got error!", state='error', expanded=True)
        if len(st.session_state['temp_create_results']) > 0:
            st.write(f"Number of embedded chunks: {len(st.session_state['temp_create_results'])}")
        else:
            st.write("For some reason, embedding seems to failed")

    if st.button("USE THESE EMBEDDINGS:", type='primary', disabled=len(st.session_state['temp_create_results']) == 0):
        for ind, file in enumerate(list(st.session_state['temp_create_results'].keys())):
            use_embeddings(st.session_state['temp_create_results'][file], file_name=file)
        st.session_state['temp_create_results'] = {}
        time.sleep(2)
        st.rerun()


with st.expander("See embeddings that are in memory:"):
    with st.container(height=500):
        for file in list(st.session_state['curr_semantics'].keys()):
            st.write(f"For file: {file}")
            st.write(st.session_state['curr_semantics'][file])

if any(len(value['file_name']) == 0 for value in list(st.session_state['curr_semantics'].values())):
    st.write("You must set embeddings to proceed further")
    st.stop()
st.write("##### Embedding memory management: ")
butcol1, butcol2, butcol3 = st.columns([0.3,0.3,0.3])
with butcol1:
    save_emb = st.button("Save embeddings into DB", type='primary', key="save_emb")
with butcol2:
    replace_emb = st.button("Replace embeddings for current files", type='primary', key='replace_emb')
with butcol3:
    clear_but = st.button("Clear embeddings from memory", key="clear_emb_memory")
if save_emb:
    try:
        for file in list(st.session_state['curr_semantics'].keys()):
            st.session_state['DB_connection'].log(table_name=st.session_state['DB_log_tables'][vector_table], data=st.session_state['curr_semantics'][file])
        st.write("✅ Embeddings saved successfully!")
    except Exception as serr:
        st.error(f"Saving failed due to this error: {serr}")

if replace_emb:
    try:
        deleted = 0
        for file in list(st.session_state['curr_semantics'].keys()):
            res = st.session_state['DB_connection'].pop_rows_by_value(table_name=st.session_state['DB_log_tables'][vector_table], column_name="file_name",search_value=file)
            if res:
                deleted += 1
        for file in list(st.session_state['curr_semantics'].keys()):
            st.session_state['DB_connection'].log(table_name=st.session_state['DB_log_tables'][vector_table],data=st.session_state['curr_semantics'][file])
        st.write("✅ Embeddings replaced successfully!")
    except Exception as serr:
        st.error(f"Saving failed due to this error: {serr}")
if clear_but:
    st.session_state['curr_semantics'] = {file: {'sessionID': [], 'file_name': [], 'split_method': [], 'embed_method': [], 'chunk_number': [], 'num_of_chunks': [], 'original_text': [], 'vector': []} for file in list(st.session_state['files_dict'].keys())}
    st.write("✅ Embeddings cleared successfully!")
    time.sleep(2)
    st.rerun()

st.divider()
st.subheader("Semantic search management")

########################################################################################################################
# LLM QUERYING MANAGEMENT
########################################################################################################################

if 'last_llm_sem_ans_saved' not in st.session_state:
    st.session_state['last_llm_sem_ans_saved'] = False

with st.expander(label="3️⃣ **SYSTEM** Prompt management"):
    st.markdown("##### Here you can either select the system prompt from templates OR write/paste your own.")

    system_prompt_options = PremadeSystemPromptsForSEMANTICS.prompt_options  # Fetch prompt options dictionary {prompt's_name: prompt's_text}

    selected_prompt = st.selectbox("Choose the prompt from these options:", options=list(system_prompt_options.keys()),placeholder="Chooce one...", index=None)

    if 'sem_system_prompt' in st.session_state and st.session_state["sem_system_prompt"]:
        st.write(f"**Previously selected prompt:** {list(st.session_state['sem_system_prompt'].keys())[0]}")

    if selected_prompt:
        cont = st.container(border=True)
        if selected_prompt == "Create_your_own_prompt":
            with cont:
                default_prompt = st.session_state.get("sem_custom_prompt", "")
                st.info("REMEMBER to always instruct the model to return the answer in a JSON format!")
                value = default_prompt if default_prompt != "" else system_prompt_options[selected_prompt]
                user_prompt = st.text_area(label="Write or paste your prompt here:", value=value, height=300)
                if st.button("USE YOUR PROMPT", type='primary'):
                    st.session_state["sem_system_prompt"] = {selected_prompt: user_prompt}
                    st.session_state["sem_custom_prompt"] = user_prompt
                    st.markdown("✅ Selected prompt saved successfully!")
                if default_prompt:
                    st.subheader(f"The questions you wrote previously:", divider='grey')
                    st.write(st.session_state.get("sem_custom_prompt", ""))
        else:
            with cont:
                if st.button("USE THIS PROMPT", type='primary'):
                    st.session_state["sem_system_prompt"] = {selected_prompt: system_prompt_options[selected_prompt]}
                    st.markdown("✅ Selected prompt saved successfully!")
                st.subheader(f"Prompt's name: {selected_prompt}", divider='grey')
                st.text(system_prompt_options[selected_prompt])

if 'sem_system_prompt' not in st.session_state:
    st.warning("No system prompt detected in memory. Choose prompt from above!")
    st.stop()

with st.expander(label="4️⃣ **SEMANTIC SEARCH** management"):
    st.markdown("##### Here you can modify semantic search's settings and search for content.")
    st.session_state['temp_permission'] = False
    semantic_questions = PremadeSemanticQuestions.question_options  # Fetch prompt options dictionary {prompt's_name: prompt's_text}

    # Iterate through each document in the session state
    for doc_id, sem_dict in st.session_state['curr_semantics'].items():
        st.markdown(f"### Settings for document: {doc_id}")

        selected_questions_key = f"{doc_id}_selected_questions"
        custom_questions_key = f"{doc_id}_custom_questions"
        sem_search_questions_key = f"{doc_id}_sem_search_questions"
        chunk_num_key = f"{doc_id}_chunk_num"

        selected_questions = st.selectbox("Choose the questions from these options:",
                                          options=list(semantic_questions.keys()),
                                          placeholder="Choose one...",
                                          index=None,
                                          key=selected_questions_key)

        if sem_search_questions_key in st.session_state and st.session_state[sem_search_questions_key]:
            st.write(f"**Previously selected questions for {doc_id}:** {list(st.session_state[sem_search_questions_key].keys())[0]}")

        cont = st.container(border=True)
        if selected_questions:
            if selected_questions == "create_your_own_questions":
                with cont:
                    default_prompt = st.session_state.get(custom_questions_key, "")
                    st.info("REMEMBER that the questions must be semantically similar to the material thus Finnish language should be used if the material is in Finnish.")
                    value = default_prompt if default_prompt != "" else semantic_questions[selected_questions]
                    user_prompt = st.text_area(label="Write or paste your questions here:",
                                               value=value,
                                               height=100,
                                               key=f"{doc_id}_user_prompt")
                    if st.button("USE YOUR QUESTIONS", type='primary', key=f"{doc_id}_use_your_questions"):
                        st.session_state[sem_search_questions_key] = {selected_questions: user_prompt}
                        st.session_state[custom_questions_key] = user_prompt
                        st.markdown("✅ Selected questions saved successfully!")
                        st.session_state['temp_permission'] = True
                    if default_prompt:
                        st.subheader(f"The prompt you wrote previously for {doc_id}:", divider='grey')
                        st.write(st.session_state.get(custom_questions_key, ""))
            else:
                with cont:
                    if st.button("USE THESE QUESTIONS", type='primary', key=f"{doc_id}_use_these_questions"):
                        st.session_state[sem_search_questions_key] = {
                            selected_questions: semantic_questions[selected_questions]}
                        st.markdown("✅ Selected questions saved successfully!")
                        st.session_state['temp_permission'] = True
                    st.subheader(f"Question set's name: {selected_questions}", divider='grey')
                    st.text(semantic_questions[selected_questions])

        # Set chunk_num per document
        num_chunks =min(st.session_state['curr_semantics'][doc_id]['num_of_chunks'])
        chunk_num = st.number_input(f"Choose how many chunks to return for document {doc_id} between 1 and {num_chunks}.",
                                    value=min(3, num_chunks),
                                    min_value=1,
                                    max_value=num_chunks ,
                                    key=chunk_num_key)

    if st.button("Fetch content"):
        st.session_state["sem_content"] = {}
        for doc_id, sem_dict in st.session_state['curr_semantics'].items():
            sem_search_questions_key = f"{doc_id}_sem_search_questions"
            chunk_num_key = f"{doc_id}_chunk_num"

            sem_searcher = SemanticSearch(openaikey=st.session_state['LLM_credentials']['openai_key'])

            if sem_search_questions_key in st.session_state:
                context = sem_searcher.search_docs(df=sem_dict,
                                                   user_query=list(st.session_state[sem_search_questions_key].values())[
                                                       0],
                                                   chunk_num=st.session_state[chunk_num_key])
                for key in ['sessionID', 'file_name', 'split_method', 'embed_method', 'chunk_number', 'num_of_chunks',
                            'vector', 'similarities']:
                    context.pop(key, None)
                st.session_state["sem_content"][doc_id] = context


if 'sem_content' not in st.session_state:
    st.warning("No semantic context detected in memory. Fetch content from above!")
    st.stop()
if len(st.session_state['sem_system_prompt'].values()) == 1:
    sys_prompt = list(st.session_state['sem_system_prompt'].values())[0]
else:
    st.error("Zero or more than one system prompt detected and that is not allowed. Fix the situation from 'Prompt handling'-page or refresh session and start from beginning.")
    st.stop()

final_json_structure = {'Information': "THIS JSON CONTAINS THE FILES FOR YOU TO HANDLE", 'Files': []}
for file_name, file_text in st.session_state['sem_content'].items():
    chunks_as_dict = next(iter(file_text.values())) if file_text else {}
    final_json_structure['Files'].append({
        'name_of_the_file': file_name,
        'chunks_of_the_file': chunks_as_dict})
st.session_state['sem_user_prompt'] = json.dumps(final_json_structure, indent=4)

with st.expander("See generated context:"):
    st.write(f"Is correct JSON: {isinstance(st.session_state['sem_user_prompt'], str)}")
    st.json(st.session_state['sem_user_prompt'])

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
            answer, tokens = st.session_state["LLM_service"].query_llm(prompt=st.session_state['sem_user_prompt'],system=sys_prompt)
            st.session_state['last_llm_sem_ans'] = {'content': answer, 'tokens': tokens}
            st.write("Querying was successful!")
            status.update(label="Answer ready!", state='complete')
            st.session_state['last_llm_sem_ans_saved'] = False
        except Exception as qerr:
            st.error(f"Got this error while querying LLM: {qerr}")
            status.update(label="Got error!", state='error', expanded=True)
if save_but:
    if 'last_llm_sem_ans' in st.session_state and st.session_state['last_llm_sem_ans']['content'] != "":
        if st.session_state['last_llm_sem_ans_saved'] == False:
            data = [st.session_state['session_id'],
                    list(st.session_state['files_dict'].keys())[0],
                    "n/a" if len(list(st.session_state['files_dict'].keys())) < 2 else list(st.session_state['files_dict'].keys())[1],
                    list(st.session_state['sem_system_prompt'].values())[0],
                    ", ".join(f"{doc_id}: {list(st.session_state[f'{doc_id}_sem_search_questions'].values())[0]}"
                              for doc_id in st.session_state['curr_semantics']
                              if f"{doc_id}_sem_search_questions" in st.session_state),
                    "Semantic_search_w_LLM",
                    st.session_state['sem_user_prompt'],
                    st.session_state["model_attributes"]['model'],
                    st.session_state['last_llm_sem_ans']['tokens'],
                    st.session_state['last_llm_sem_ans']['content']]
            if len(data) != len(st.session_state['all_table_headers'][this_is]):
                st.error("Error in saving. Data and table columns do not match!")
                time.sleep(3)
                st.rerun()
            try:
                if 't2_results_dict' not in st.session_state:
                    st.session_state['t2_results_dict'] = {list(st.session_state['all_table_headers'][this_is].keys())[ind]: [data[ind]] for ind in range(len(data))}
                else:
                    for ind, key in enumerate(list(st.session_state['t2_results_dict'].keys())):
                        st.session_state['t2_results_dict'][key].append(data[ind])
                st.session_state['last_llm_sem_ans_saved'] = True
            except Exception as se:
                st.error(f"Got this error while saving results: {se}")
            if st.session_state['DB_sel'] != '.csv':
                try:
                    st.session_state['DB_connection'].log(table_name=st.session_state['DB_log_tables'][this_is], data=data)
                    st.session_state['last_llm_sem_ans_saved'] = True
                    st.write("✅ Answer saved successfully.")
                except Exception as se:
                    st.error(f"Got this error while logging results: {se}")
        else:
            st.write("Current answer already saved!")
    else:
        st.warning("Nothing to save at the moment.")
if del_but:
    if 'last_llm_sem_ans' in st.session_state and st.session_state['last_llm_sem_ans']['content'] != "":
        st.session_state['last_llm_sem_ans'] = {'content': "", 'tokens': 0}
        st.session_state['last_llm_sem_ans_saved'] = False
if download_but:
    if 't2_results_dict' in st.session_state:
        df = pandas.DataFrame(st.session_state['t2_results_dict'])
        st.download_button(label="Download data as CSV", data=df.to_csv(index=False).encode('utf-8'), file_name=f"{this_is}_results.csv", mime='text/csv', type='primary' )
    else:
        st.warning("No results saved yet!")

st.divider()
st.write("Remember to save the answer")
if 'last_llm_sem_ans' in st.session_state and st.session_state['last_llm_sem_ans']['content'] != "":
    with st.container(border=True, height=600):
        st.write("##### LLM's answer")
        text_display = st.session_state['last_llm_sem_ans']['content']
        try:
            json_text = json.loads(text_display)
            st.info(f"**INFO** The answer is in correct format (JSON). Tokens used: {st.session_state['last_llm_sem_ans']['tokens']} pcs. LLM found {len(list(json_text.values())[0])} conflicts.")
            st.json(json_text)
        except ValueError as e:
            st.info(f"The answer is not in correct format (JSON). Tokens used: {st.session_state['last_llm_sem_ans']['tokens']} pcs.")
            st.write(text_display)
else:
    st.info("Nothing to show at the moment. Please query LLM first.")