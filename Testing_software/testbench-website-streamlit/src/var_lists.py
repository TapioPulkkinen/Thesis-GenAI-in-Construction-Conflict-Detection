
class VarListing:
    """This class is just for notes and this doesn't actually do anything"""
    """LLM VARIABLES"""
    llm_credentials = 'LLM_credentials'  # {"openai_key_sel": ownkey_sel,"openai_key": user_openai_key,"openai_endpoint_sel": endpoint_sel,"endpoint_key": user_endpoint_key,"endpoint_versio": user_endpoint_versio}
    model_attributes = 'model_attributes'  # {'model': model, 'temperature': temperature}
    llm_service = 'LLM_service'  # Connection object from llm_handler file
    ### Test 1: Only LMM
    last_answer_from_llm = 'last_llm_ans'  # {content: text as JSON, tokens: tokens as int}
    is_the_last_llm_ans_saved = 'last_llm_ans_saved'  # Boolean
    ### Test 2: Semantic search
    last_semantic_answer_from_llm = 'last_llm_sem_ans'  # {content: text as JSON, tokens: tokens as int}
    is_the_last_sem_llm_ans_saved = 'last_llm_sem_ans_saved'  # Boolean

    """DATABASE VARIABLES"""
    db_initialized = 'DB_initialized'  # boolean
    db_selection = 'DB_sel'  # string. One of from 'Backend', 'User', or '.csv'
    db_connection = 'DB_connection'  # Connection object from data_logger file
    db_result_logging_table = 'DB_log_tables'  # {'test_1': table_1, 'test_2': table_2, 'semantic_vectors': table_x}
    session_id_variable = "session_id"  # user set or this string: test_session_{datetime.date.today()}_at_{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}

    results_logging_table_headers_t1 = 't1_table_headers'  # in actual variables
    results_logging_table_headers_t2 = 't2_table_headers'  # in actual variables
    semantics_table = 't2_semantics_table_headers'  # in actual variables

    """FILES VARIABLES"""
    files_to_analyze = 'files_dict'  # {'file_name': text, 'file_name2':text2}
    semantic_repr_of_files = 'curr_semantics'  # {file_name: {'sessionID': [], 'file_name': [], 'chunk_number': [], 'num_of_chunks': [], 'original_text': [], 'vector': []}}


    """PROMPT VARIABLES"""
    ### Test 1: Only LMM
    user_written_prompt = 'custom_prompt'  # text
    final_system_prompt_to_use_in_analyze = 'system_prompt'  # {selected_prompt_name: selected_prompt}
    final_user_prompt_to_use_in_analyze = 'user_prompt'  # text
    ### Test 2: Semantic search
    sem_user_written_questions = 'sem_custom_questions'  # text
    sem_search_questions = 'sem_search_questions'  # {selected_questions_name: selected_questions}
    sem_user_written_prompt = 'sem_custom_prompt'  # text
    final_sem_system_prompt_to_use_in_analyze = 'sem_system_prompt'  # {selected_prompt_name: selected_prompt}
    semantic_content = 'sem_content'  # {file_name: {context}}
    final_sem_user_prompt_to_use_in_analyze = 'sem_user_prompt'  # text

    """TEST SETUP VARIABLES"""
    test_ready = 'test_ready'  # Boolean. Is all settings ready for testing
    t1_results_in_memory = 't1_results_dict'  # {'header1': [res1, res2, ...], 'header2': [res1, res2, ...], ...}
    t2_results_in_memory = 't2_results_dict'  # {'header1': [res1, res2, ...], 'header2': [res1, res2, ...], ...}

    """LOGIN VARIABLES"""
    user_logged_in_correctly = 'password_correct'  # boolean
    users_name = 'username_value'  # text

class ActualVariables:

    log_tables_init_vals = {'test_1': "", 'test_2': "", 'semantic_vectors': ""}

    t1_db_table_headers = {'sessionID': 'TEXT', 'file_1_name': 'TEXT', 'file_2_name': 'TEXT', 'prompt': 'TEXT',
                           'method': 'TEXT', 'LLM': 'TEXT', 'tokens_used': 'INT', 'answer': 'MEDIUMTEXT'}

    vector_emb_table_headers = {'sessionID': 'TEXT', 'file_name': 'TEXT', 'split_method': 'TEXT', 'embed_method': 'TEXT',
                                'chunk_number': 'INT', 'num_of_chunks': 'INT', 'original_text': 'MEDIUMTEXT', 'vector': 'MEDIUMTEXT'}

    t2_db_table_headers = {'sessionID': 'TEXT', 'file_1_name': 'TEXT', 'file_2_name': 'TEXT', 'prompt': 'TEXT',
                           'sem_search_questions': 'TEXT', 'method': 'TEXT', 'chunks': 'TEXT', 'LLM': 'TEXT',
                           'tokens_used': 'INT', 'answer': 'MEDIUMTEXT'}
