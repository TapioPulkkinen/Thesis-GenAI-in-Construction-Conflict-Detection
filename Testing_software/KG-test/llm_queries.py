

class GraphConstQuery:

    system = """
# TASK:
Your task is to extract all the entities and their relationships from the text what user provides. The text is related to construction industry.
Please note that the entities and relationships will be used to construct a knowledge graph. Thus it is important to capture all the important details and connect them together with relationships.
Do not limit yourself to these but entities can be for example: persons, companies, dates, processes, tasks, money, projects, and other details.
To summarize your task: try to find all the important entities BUT do not take into account entities that you cannot join to others with relationships so ALWAYS JOIN EVERYTHING TOGETHER WITH RELATIONSHIPS.
# INSTRUCTIONS:
1. Read through the provided text line by line. It will be related to construction industry.
2. Locate important entities and their relationships. 
3. For each entity, come up with a proper type. I.e. persons or companies or processes and so on.
4. For each relationship, come up with a proper type. I.e. is_part_of or belongs_to or has and so on.
5. Map entities and relationships to a desired JSON answer format.
# ANSWER FORMAT:
Always answer using this JSON format and do not answer anything else:
{"relationships": [
    {"type": "example_relationship",
      "from_node": {
        "type": "type_of_node_1",
        "text": "text_of_node_1"},
      "to_node": {
        "type": "type_of_node_2",
        "text": "text_of_node_2"}},
    {"type": "example_relationship_2",
      "from_node": {
        "type": "type_of_node_1",
        "text": "text_of_node_1"},
      "to_node": {
        "type": "type_of_node_3",
        "text": "text_of_node_3"}},
  ]
}
"""

    query_prompt = """
#TASK:
Your task is to find all the conflicts between the files that you receive. Both files are about the same work, and they are related to the construction industry. One file is a contract for the job, and another file is an offer for that same job. Try to find all things that might conflict between the files, paying attention to details such as what has been offered and what has been agreed upon.
Note that there are not always conflicts in the files. Only report the things you consider as conflicts.

#EXAMPLE CONFLICTS:
These conflicts are examples of what kind of conflicts an offer and a contract might contain. Remember that these are examples, so do not limit yourself to these:
- Differences between offer's and contract's prices, dates, and parties.
- Differences between contact persons or persons’ contact information such as phone number and email address.
- Differences between work mentioned in the contract and the work that was offered.

#ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
{"file_one_info": "Example conflict text 1 in file one",
"file_two_info": "Example conflict text 1 in file two",
"explanation": "Very short explanation for conflict 1"},
{"file_one_info": "Example conflict text 2 in file one",
"file_two_info": "Example conflict text 2 in file two",
"explanation": "Very short explanation for conflict 2"}
]}"""