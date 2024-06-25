import json
import pandas as pd
import os
from datetime import datetime
import fitz
import re
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from neo4j_connector import Neo4jConnector
from kg_llm_handler import OpenAILLMService, Text2Token, LLMInfo
from llm_queries import GraphConstQuery
from dumb_secrets import Neo4jSecrets, DummyKeys
from json_extender import extend_json_relationships

class Memory:
    texts = []
    relationship_data = {}

def read_pdf_text_to_memory(memory, filename, clean_not_raw=True):
    """
    Reads all text from a PDF file using the fitz library and returns it as a single string.

    Args:
        memory: An object with an attribute `texts` to save the extracted text.
        filename (str): The path to the PDF file.
        clean_not_raw (bool): If True, the text is cleaned before storing.

    Raises:
        FileNotFoundError: If the PDF file cannot be found.
        ValueError: If the filename is not a string or memory does not have a proper 'texts' attribute.
        Exception: For other issues such as read errors or processing errors.
    """
    if not isinstance(filename, str):
        raise ValueError("Filename must be a string.")
    if not hasattr(memory, 'texts') or not isinstance(memory.texts, list):
        raise ValueError("Memory object must have a 'texts' attribute that is a list.")

    try:
        document = fitz.open(filename)
    except Exception as e:
        raise FileNotFoundError(f"Unable to open the file: {filename}. Error: {str(e)}")

    texts = []
    try:
        for page in document:
            texts.append(page.get_text())
    except Exception as e:
        document.close()
        raise Exception(f"Error reading pages from the PDF file: {str(e)}")
    finally:
        document.close()

    text = ' '.join(texts)
    if clean_not_raw:
        text = clean_text(text)

    memory.texts.append(text)

def clean_text(text, remove_hyphenations=True, additional_modifications=None):
    """
    Cleans the given text by removing hyphenations and applying additional modifications if specified.

    Args:
        text (str): The text to be cleaned.
        remove_hyphenations (bool): If True, removes hyphenations like "-\n" from the text.
        additional_modifications (function): An optional function that takes a string and returns a modified string.

    Returns:
        str: The cleaned text.

    Raises:
        TypeError: If text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    text = text.replace("-\n", "") if remove_hyphenations else text

    lines = text.splitlines()
    cleaned_lines = []
    previous_line_blank = False
    for line in lines:
        current_line_blank = not line.strip()

        if current_line_blank and previous_line_blank:
            continue

        cleaned_lines.append(line)
        previous_line_blank = current_line_blank

    cleaned_text = '\n'.join(cleaned_lines)
    if additional_modifications and callable(additional_modifications):
        cleaned_text = additional_modifications(cleaned_text)

    return cleaned_text


def text_chunker(text, chunk_max_length=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_max_length, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return chunks


def ents_to_table(json_data):
    rows = []

    for relation in json_data['relationships']:
        from_node_text = relation['from_node']['text']
        to_node_text = relation['to_node']['text']
        relation_type = relation['type']
        rows.append({
            'from_node': from_node_text,
            'relationship': relation_type,
            'to_node': to_node_text})

    df = pd.DataFrame(rows, columns=['from_node', 'relationship', 'to_node'])
    return df.to_csv(index=False)


def cost_info_to_file(data, name, filename='cost_info.txt'):
    # Extracting data from the given dictionary
    tokens_in = data['tokens'][0]
    tokens_out = data['tokens'][1]
    cost = data['money']
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Creating the row to add in CSV format
    new_row = f"{current_datetime},{name},{tokens_in},{tokens_out},{cost}\n"

    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Writing to file
    with open(filename, 'a' if file_exists else 'w') as file:
        if not file_exists:
            # Write headers if the file is being created for the first time
            file.write("datetime,filename,tokens_in,tokens_out,cost\n")
        # Append the new data
        file.write(new_row)


def prune_messages(messages):
    # Determine the indices to keep
    keep_indices = set()
    seen_user = seen_assistant = False

    for i in reversed(range(len(messages))):
        role = messages[i]['role']
        if role == 'system':
            keep_indices.add(i)
        elif role == 'user' and not seen_user:
            keep_indices.add(i)
            seen_user = True
        elif role == 'assistant' and not seen_assistant:
            keep_indices.add(i)
            seen_assistant = True

    new_messages = [messages[i] for i in sorted(keep_indices)]

    return new_messages


def llm_extract_info_to_memory(memory, llm, text_list):
    if not isinstance(text_list, list):
        raise TypeError("text_list must be a list type.")
    system_prompt = GraphConstQuery().system
    system_tok = Text2Token().num_of_tokens_in_text(system_prompt)

    cost = {'tokens': [0, 0], 'money': 0}
    messages = [{"role": "system", "content": system_prompt}]
    for ind, one in enumerate(text_list):
        print(f"Extraction: {ind+1}/{len(text_list)}")
        if ind < 1:
            user_prompt = f"# THIS IS THE TEXT:\n{one}"
            messages.append({"role": "user", "content": user_prompt})
        else:
            user_prompt = f"# ADDITIONAL INSTRUCTIONS:\nTake entities from previous answers into account but you don't have to answer them. Just answer the new ones.\n" \
                          f"# THIS IS THE TEXT:\n{one}"
            messages.append({"role": "user", "content": user_prompt})
        try:
            answer, prompt_tok, ans_tok = llm.query_llm_multi_messages(messages=messages)
            messages.append({"role": "assistant", "content": answer})
            answer = json.loads(answer)
            if ind == 0:
                memory.relationship_data = answer
            else:
                extend_json_relationships(memory.relationship_data, answer)
            cost['tokens'][0] += prompt_tok
            cost['tokens'][1] += ans_tok
            cost['money'] += round(LLMInfo().estimate_cost(model=llm.model, prompt=prompt_tok, output=ans_tok), 2)
            for mes in messages:
                print(mes)
        except Exception as err:
            if "TOKEN LIMIT ERROR" in err:
                if ind == 0:
                    raise Exception(f"Error message: {err}")
                elif ind == 1:
                    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
                else:
                    messages = prune_messages(messages)
                print("WARNING: Deleted old messages from context because of token limits error and trying again.")
                try:
                    answer, prompt_tok, ans_tok = llm.query_llm_multi_messages(messages=messages)
                    messages.append({"role": "assistant", "content": answer})
                    answer = json.loads(answer)

                    extend_json_relationships(memory.relationship_data, answer)
                    cost['tokens'][0] += prompt_tok
                    cost['tokens'][1] += ans_tok
                    cost['money'] += round(LLMInfo().estimate_cost(model=llm.model, prompt=prompt_tok, output=ans_tok), 2)
                except Exception as err:
                    raise Exception(f"Error message: {err}")
            else:
                raise Exception(f"Error message: {err}")

    return cost


def construct_graphs(files: list = None, chunk_text=True, clear_db_before_fulfill=True):
    memory = Memory()
    model = 'gpt-4-0125-preview'  # 'gpt-3.5-turbo-0125'
    llm = OpenAILLMService(api_key=DummyKeys.OPENAI_API_KEY, model=model)

    if not files:
        raise Exception("List of files is required!")

    db_keys = [Neo4jSecrets().first_instance, Neo4jSecrets().second_instance]

    print("Extraction starting")
    for ind, file in enumerate(files):
        read_pdf_text_to_memory(memory=memory, filename=file)

        if chunk_text:
            text_list = text_chunker(memory.texts[ind])
        else:
            text_list = [memory.texts[ind]]
        cost = llm_extract_info_to_memory(memory, llm, text_list)
        name = os.path.basename(file)

        with open(f"safe_save_json_{name}.txt", 'w', encoding='utf-8') as file:
            json.dump(memory.relationship_data, file, ensure_ascii=False, indent=4)

        cost_info_to_file(data=cost, name=name)

        if len(memory.relationship_data['relationships']) == 0:
            raise ValueError("Extraction failed for some reason")

        print("starting graph operation")
        graph = Neo4jConnector(db_keys[ind]["NEO4J_URI"], db_keys[ind]["NEO4J_USERNAME"], db_keys[ind]["NEO4J_PASSWORD"])
        if clear_db_before_fulfill:
            graph.clear_database()
        graph.process_json(memory.relationship_data)

        graph.close()
        print(f"Whole process ready for {ind+1}. file")


def langchain_query_graphs():
    from langchain.chains import GraphCypherQAChain
    from langchain_community.graphs import Neo4jGraph
    from langchain_openai import ChatOpenAI

    load_dotenv(r'path')

    os.environ["OPENAI_API_KEY"]

    db_keys = [Neo4jSecrets().first_instance, Neo4jSecrets().second_instance]
    answers = []

    for ind, db in enumerate(db_keys):
        graph = Neo4jGraph(url=db_keys[ind]["NEO4J_URI"], username=db_keys[ind]["NEO4J_USERNAME"], password=db_keys[ind]["NEO4J_PASSWORD"])
        graph.refresh_schema()
        chain = GraphCypherQAChain.from_llm(
            graph=graph,
            cypher_llm=ChatOpenAI(temperature=0, model="gpt-4-0125-preview", openai_api_key=DummyKeys.OPENAI_API_KEY),
            qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
            verbose=True, return_intermediate_steps=True)
        ans = chain.run("What is said about contract details?")
        answers.append(ans)

    system = "You are a construction industry assistant that helps to find conflicts from documents. Return your answer in JSON format so that each conflict is clearly separated."
    user = f"Investigate these two answers that contains information from documents. Try to find if there is conflicst between the documents.\nDocument 1:\n{answers[0]}\n\nDocument 2:\n{answers[1]}"
    final_ans = OpenAILLMService(api_key=DummyKeys.OPENAI_API_KEY, model="gpt-3.5-turbo-16k", temperature=0).query_llm(system=system, prompt=user)
    print("final ans: ", final_ans)


if __name__ == "__main__":
    construct_graphs()
    #langchain_query_graphs()

