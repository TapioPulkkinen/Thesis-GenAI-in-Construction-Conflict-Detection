class PremadeSystemPrompts:
    prompt_options = {
        '1_file_simple_problems_prompt':
            """ # TASK: 
Your task involves analyzing a single document related to the construction industry. This analysis consists of two primary steps, and your responses should be formatted in JSON for easy data extraction later.
## Step 1: Document Identification
Begin by carefully reading the document to identify its type, which could be a contract, a plan, guidelines, technical specifications, a report, or any other type of construction-related document. Once you have determined the type of document, provide a brief summary of your identification process in the following JSON format:
{"document_type": "[type]",
"identification_summary": "Brief explanation of how you identified this type."}
## Step 2: Problem Detection
After identifying the type of document, examine it for any potential issues. Look for problems such as inconsistencies or ambiguities, non-compliance with legal standards or industry best practices, unrealistic timelines or budget estimations, and omissions of critical information like safety protocols.
For each problem identified, describe the issue in detail, including its location in the document (with section or paragraph references if possible) and why it represents a potential problem. Format your findings in JSON.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"problems": [
    {"location": "Location/Description of the issue",
      "description": "Explanation of why it is a problem"},
    {"location": "Another Location/Description of the issue",
      "description": "Explanation of why it is a problem"}
    // Add more problems as needed
]}
# EXAMPLE:
Example of a problem to guide your analysis, formatted in JSON:
{"problems": [
    {"location": "Section 3.2 specifies a concrete grade not suitable for the environmental conditions described in Section 1.5",
      "description": "Using the specified concrete grade could compromise the structure's durability and safety."}
]}
# SUMMARY:
Please conduct a comprehensive analysis of the document, starting with identifying its type and followed by a detailed examination to uncover any potential problems, using the JSON formats provided above.""",
        '2_files_simple_conflict_prompt':
            """# TASK:
Please compare the following two construction industry documents to identify any conflicts between them. Conflicts may arise from differences in dates for the same task, discrepancies in material specifications, contradictions in project responsibilities, or any other variances that could impact the project's timeline, quality, or cost.
To perform this analysis, examine each document thoroughly and list any conflicts you find. For each conflict, clearly indicate the information from file one, the corresponding information from file two, and provide an explanation of why it represents a conflict. Format your findings in JSON.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
{"file_one_info": "Information from file one",
"file_two_info": "Corresponding information from file two",
"explanation": "Explanation why it is a conflict"},
{"file_one_info": "Another information from file one",
"file_two_info": "Corresponding information from file two",
"explanation": "Explanation why it is a conflict"}
// Add more conflicts as needed
]}
# EXAMPLE:
Example of potential conflicts to look for:
-	Different start or completion dates for the same task.
-	Variations in the quantity or type of materials specified.
-	Discrepancies in the roles or responsibilities assigned to team members.
-	Contradictory safety standards or procedures.
Here are some specific examples to illustrate how you should format your findings in JSON:
{"conflicts": [
{"file_one_info": "Excavation starts on 20.4.2024",
"file_two_info": "Excavation starts on 27.4.2024",
"explanation": "The dates for the same task are different, leading to potential scheduling conflicts."},
{"file_one_info": "Concrete grade C30/37",
"file_two_info": "Concrete grade C25/30",
"explanation": "Different concrete grades specified could affect the structure's integrity."},
{"file_one_info": "Safety inspection by project manager weekly",
"file_two_info": "Safety inspection by safety officer daily",
"explanation": "Different inspection frequencies and responsibilities could lead to oversight in safety protocols."}
]}
# SUMMARY:
Analyze the documents with these examples in mind and list any conflicts you identify using the JSON format provided. Ensure your analysis is thorough and consider all aspects of the construction documents.""",

        '2_files_simple_contract_conflicts_prompt':
            """# TASK:
Your task is to compare the specific clauses and provisions of a contract document against the standards and recommendations outlined in a general contract guide. The objective is to identify any elements within the contract that are either illegal or not recommended according to the guide. This analysis is crucial for ensuring that the contract adheres to legal standards and best practices in the industry.
When analyzing the contract, focus on key areas such as legal compliance of the terms and conditions, conformity with recommended practices for fairness, clarity, and risk management, identification of clauses that may pose legal risks or are against regulatory guidelines, and assessment of any terms that deviate significantly from industry standards or best practices as outlined in the guide.
For each conflict you find, list the specific clause or provision from the contract, the corresponding recommendation or legal requirement from the guide, and provide an explanation of why it represents a conflict or a potential issue. Format your findings in JSON.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{" conflicts ": [
{"contract_clause": "Specific clause or provision from the contract",
"guide_recommendation": "Corresponding recommendation or legal requirement from the guide",
"explanation": "Explanation why it is a conflict or potential issue"},
{"contract_clause": "Another specific clause or provision from the contract",
"guide_recommendation": "Corresponding recommendation or legal requirement from the guide",
"explanation": "Explanation why it is a conflict or potential issue"}
// Add more discrepancies as needed
]}
# EXAMPLE:
Examples of potential conflicts to look for include contract terms that allow for unilateral modifications without notice, late payment penalties that are excessively high, and contracts that lack a clear dispute resolution mechanism.
Here are some specific examples to illustrate how you should format your findings in JSON:
{" conflicts ": [
{"contract_clause": "Contract terms allow for unilateral modifications without notice",
"guide_recommendation": "Guide recommends mutual agreement for any contract modifications",
"explanation": "Unilateral modification clauses could be seen as unfair or exploitative."},
{"contract_clause": "Late payment penalties specified in the contract are excessively high",
"guide_recommendation": "Legal guidelines recommend or limit penalty charges to a certain percentage",
"explanation": "Excessive penalties could be considered punitive and not enforceable."},
{"contract_clause": "The contract lacks a clear dispute resolution mechanism",
"guide_recommendation": "The guide advises including a step-by-step dispute resolution process",
"explanation": "Absence of a clear mechanism can lead to legal complications and is not recommended."}
]}
# SUMMARY:
Please analyze the contract with these considerations in mind and list any discrepancies, illegalities, or non-recommended practices you identify, using the JSON format provided. Ensure your analysis is comprehensive, covering all aspects of the contract against the guide.""",

        '2_files_simple_general_conflict_prompt':
            """# Task: 
Your task involves a two-step analysis of two documents provided to you. The first step is to determine the type of each document. The second step is to compare these documents to identify any conflicts or discrepancies between them, focusing on areas that could lead to misunderstandings, legal issues, or execution problems in relation to their content and implications.
## Step 1: Document Identification
Start by examining the content of each document to identify its type. Common types of documents you might encounter include contracts, plans, guidelines, technical specifications, and reports. Do not answer anything regarding this step. Once you have identified the type of each document, move to second step. 
## Step 2: Conflict Detection
After identifying the types of documents, proceed to compare them to find any conflicts. Focus on discrepancies that could impact their implementation or compliance, such as conflicting dates, diverging specifications, contradictory obligations, or any other aspect where the documents do not align.
For each conflict you find, list the conflicting information from both documents and provide an explanation of why it represents a conflict. Report your findings in the JSON format.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
{" file_one_info ": "Example conflict text 1 in file one",
" file_two_info ": "Example conflict text 1 in file two",
"explanation": "Very short explanation for conflict 1"},
{" file_one_info ": "Example conflict text 2 in file one",
" file_two_info ": "Example conflict text 2 in file two",
"explanation": "Very short explanation for conflict 2"}
]}
# EXAMPLE:
Examples to guide your analysis:
- For a contract and a plan, look for discrepancies in project timelines, specifications, responsibilities, and deliverables.
- Between guidelines and technical specifications, identify areas where the specifications may not meet the standards set out in the guidelines.
- When comparing contracts, focus on terms that might contradict each other in areas such as payment terms, deliverables, and obligations.
# SUMMARY:
Please conduct a thorough analysis of the documents, starting with the identification of their types and followed by a detailed comparison to identify any conflicts, using the formats provided above. MOST IMPORTANTLY do not return anything else than what was asked.""",

        "Create_your_own_prompt":
            """# TASK: 
{write your prompt here}
{You can keep or modify the JSON return guide below}
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
    {" file_one_info ": "Example conflict text 1 in file one",
      " file_two_info ": "Example conflict text 1 in file two",
      "explanation": "Very short explanation for conflict 1"},
    {" file_one_info ": "Example conflict text 2 in file one",
      " file_two_info ": "Example conflict text 2 in file two",
      "explanation": "Very short explanation for conflict 2"}
  ]} """,
        "offer_request_vs_offer":
        """#TASK:
Your task is to identify any discrepancies between the offer request and the actual offer for a construction job. You will receive two documents: one is an offer request outlining desired terms and conditions, and the other is the actual offer made in response to the request. Examine each document carefully to detect any conflicts in terms such as pricing, dates, parties involved, and scope of work.
Note that conflicts may not always be present. Only report discrepancies that you consider genuine conflicts.

EXAMPLE CONFLICTS:
These examples illustrate potential conflicts between an offer request and an actual offer. Use these as a guide but remain open to identifying other types of conflicts:
- Variations in prices, dates, or parties mentioned in the offer request compared to the actual offer.
- Discrepancies in contact information for the relevant parties, including phone numbers and email addresses.
- Differences in the scope of work as outlined in the offer request versus what is detailed in the actual offer.

ANSWER FORMAT:
Please format your responses in the following JSON structure. Include only conflict-related information:

{
  "conflicts": [
    {
      "file_one_info": "Example conflict text 1 from the offer request",
      "file_two_info": "Example conflict text 1 from the actual offer",
      "explanation": "Brief explanation of the identified conflict"
    },
    {
      "file_one_info": "Example conflict text 2 from the offer request",
      "file_two_info": "Example conflict text 2 from the actual offer",
      "explanation": "Brief explanation of the identified conflict"
    }
  ]
}""",
    "meeting_minute_vs_meeting_minute":
    """#TASK:
Your task is to identify any discrepancies between two meeting minutes documents. You will review documents from two different meetings regarding the same project to detect conflicts in terms such as decisions made, action items assigned, timelines agreed upon, and participant roles. Carefully examine each document to find any inconsistencies or contradictions.

#EXAMPLE CONFLICTS:
These examples illustrate potential conflicts between the minutes of two different meetings. Use these as a guide but be open to identifying other types of conflicts:
- Differences in decisions reported in the first meeting compared to those reported in the subsequent meeting.
- Conflicts in action items assigned to individuals or teams.
- Variations in agreed-upon timelines or deadlines.
- Discrepancies in the roles or responsibilities assigned to participants.

#ANSWER FORMAT:
Please format your responses in the following JSON structure. Include only conflict-related information:
{
  "conflicts": [
    {
      "file_one_info": "Example conflict text 1 from the first meeting minutes",
      "file_two_info": "Example conflict text 1 from the second meeting minutes",
      "explanation": "Brief explanation of the identified conflict"
    },
    {
      "file_one_info": "Example conflict text 2 from the first meeting minutes",
      "file_two_info": "Example conflict text 2 from the second meeting minutes",
      "explanation": "Brief explanation of the identified conflict"
    }
  ] 
}""",

    }


class PremadeUserPrompts:
    prompt_templates = {"basic_files_as_attachment: "
                        """  """}


class PremadeSystemPromptsForSEMANTICS:
    prompt_options = {"2_files_general_conflicts_prompt":
                          """# Task:
Your task involves a two-step analysis of task-relevant chunks of text from two documents provided to you in JSON format. The first step is to determine the type of each document based on the content chunks provided. The second step is to compare these document chunks to identify any conflicts or discrepancies between them, focusing on areas that could lead to misunderstandings, legal issues, or execution problems in relation to their content and implications.
## Step 1: Document Identification
You will receive relevant chunks of text from each document in JSON format. Start by examining the content of these chunks to identify the type of the document they belong to. Common types of documents you might encounter include contracts, plans, guidelines, technical specifications, and reports. Do not answer anything regarding this step. Once you have identified the type of each document based on the provided chunks, move to the second step.
## Step 2: Conflict Detection
After identifying the types of documents from the chunks provided, proceed to compare these chunks to find any conflicts. Focus on discrepancies that could impact their implementation or compliance, such as conflicting dates, diverging specifications, contradictory obligations, or any other aspect where the documents do not align based on the content chunks.
For each conflict you find, list the conflicting information from both documents' chunks and provide an explanation of why it represents a conflict. Report your findings in the JSON format.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
{" file_one_info ": "Example conflict text 1 in file one's chunk",
" file_two_info ": "Example conflict text 1 in file two's chunk",
"explanation": "Very short explanation for conflict 1"},
{" file_one_info ": "Example conflict text 2 in file one's chunk",
" file_two_info ": "Example conflict text 2 in file two's chunk",
"explanation": "Very short explanation for conflict 2"}
]}
# EXAMPLE:
Examples to guide your analysis:
For a contract and a plan, look for discrepancies in project timelines, specifications, responsibilities, and deliverables based on the chunks provided.
Between guidelines and technical specifications, identify areas where the specifications in the provided chunks may not meet the standards set out in the guidelines.
When comparing contracts, focus on terms that might contradict each other in areas such as payment terms, deliverables, and obligations based on the content chunks.
# SUMMARY:
Please conduct a thorough analysis of the document chunks provided to you, starting with the identification of their types and followed by a detailed comparison to identify any conflicts, using the formats provided above. MOST IMPORTANTLY do not return anything else than what was asked.""",
                      '2_files_simple_contract_conflicts_prompt':
"""# TASK:
Your task is to compare specific clauses and provisions from segments of a contract document against the standards and recommendations outlined in a general contract guide. These segments are provided as semantically relevant chunks rather than the entire document. The objective is to identify any elements within these contract chunks that are either illegal or not recommended according to the guide. This analysis is crucial for ensuring that the segments of the contract adhere to legal standards and best practices in the industry.
When analyzing the contract chunks, focus on key areas such as legal compliance of the terms and conditions, conformity with recommended practices for fairness, clarity, and risk management, identification of clauses that may pose legal risks or are against regulatory guidelines, and assessment of any terms that deviate significantly from industry standards or best practices as outlined in the guide.
For each conflict you find within the chunks, list the specific clause or provision from the contract, the corresponding recommendation or legal requirement from the guide, and provide an explanation of why it represents a conflict or a potential issue. Format your findings in JSON.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{" conflicts ": [
{"contract_clause": "Specific clause or provision from the contract chunk",
"guide_recommendation": "Corresponding recommendation or legal requirement from the guide",
"explanation": "Explanation why it is a conflict or potential issue"},
{"contract_clause": "Another specific clause or provision from the contract chunk",
"guide_recommendation": "Corresponding recommendation or legal requirement from the guide",
"explanation": "Explanation why it is a conflict or potential issue"}
// Add more discrepancies as needed
]}
# EXAMPLE:
Examples of potential conflicts to look for include contract terms that allow for unilateral modifications without notice, late payment penalties that are excessively high, and contracts that lack a clear dispute resolution mechanism.
## Here are some specific examples to illustrate how you should format your findings in JSON:
{" conflicts ": [
{"contract_clause": "Contract terms allow for unilateral modifications without notice",
"guide_recommendation": "Guide recommends mutual agreement for any contract modifications",
"explanation": "Unilateral modification clauses could be seen as unfair or exploitative."},
{"contract_clause": "Late payment penalties specified in the contract are excessively high",
"guide_recommendation": "Legal guidelines recommend or limit penalty charges to a certain percentage",
"explanation": "Excessive penalties could be considered punitive and not enforceable."},
{"contract_clause": "The contract lacks a clear dispute resolution mechanism",
"guide_recommendation": "The guide advises including a step-by-step dispute resolution process",
"explanation": "Absence of a clear mechanism can lead to legal complications and is not recommended."}
]}
# SUMMARY:
Please analyze the provided contract chunks with these considerations in mind and list any discrepancies, illegalities, or non-recommended practices you identify, using the JSON format provided. Ensure your analysis is comprehensive, covering all aspects of the contract chunks against the guide.
""",
                      '2_files_simple_conflict_prompt':
"""# TASK:
Please compare sets of text chunks from two construction industry documents to identify any conflicts between them. Conflicts may arise from differences in dates for the same task, discrepancies in material specifications, contradictions in project responsibilities, or any other variances that could impact the project's timeline, quality, or cost. These segments are provided as semantically relevant chunks rather than the entire documents.
To perform this analysis, examine the sets of text chunks from each document thoroughly and list any conflicts you find. For each conflict, clearly indicate the information from document one, the corresponding information from document two, and provide an explanation of why it represents a conflict. Format your findings in JSON.
# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
{" document_one_info": "Information from segment one",
" document_two_info": "Corresponding information from segment two",
"explanation": "Explanation why it is a conflict"},
{" document_one_info": "Another information from segment one",
" document_two_info": "Corresponding information from segment two",
"explanation": "Explanation why it is a conflict"}
// Add more conflicts as needed
]}
# EXAMPLE:
Example of potential conflicts to look for:
-	Different start or completion dates for the same task.
-	Variations in the quantity or type of materials specified.
-	Discrepancies in the roles or responsibilities assigned to team members.
-	Contradictory safety standards or procedures.
Here are some specific examples to illustrate how you should format your findings in JSON:
{"conflicts": [
{"segment_one_info": "Excavation starts on 20.4.2024",
"segment_two_info": "Excavation starts on 27.4.2024",
"explanation": "The dates for the same task are different, leading to potential scheduling conflicts."},
{"segment_one_info": "Concrete grade C30/37",
"segment_two_info": "Concrete grade C25/30",
"explanation": "Different concrete grades specified could affect the structure's integrity."},
{"segment_one_info": "Safety inspection by project manager weekly",
"segment_two_info": "Safety inspection by safety officer daily",
"explanation": "Different inspection frequencies and responsibilities could lead to oversight in safety protocols."}
]}
# SUMMARY:
Analyze the segments from the documents with these examples in mind and list any conflicts you identify using the JSON format provided. Ensure your analysis is thorough and consider all aspects of the construction document segments. 
""",
                      "Create_your_own_prompt":
                          """# TASK: 
{Write your prompt here. You can keep or modify the JSON return guide below.}

# ANSWER FORMAT:
Return your answers in the following JSON format and do not answer anything else:
{"conflicts": [
  {"file_one_info": "Example conflict text 1 in file one",
    "file_two_info": "Example conflict text 1 in file two",
    "explanation": "Very short explanation for conflict 1"},
  {"file_one_info": "Example conflict text 2 in file one",
    "file_two_info": "Example conflict text 2 in file two",
    "explanation": "Very short explanation for conflict 2"}
]} """,
}


class PremadeSemanticQuestions:

    question_options = {"about_agreements":
            """Millaisia sopimuksia yritykset ovat tehneet?""",
                        "about_working":
            """Miten työt ovat edenneet?""",
                        "multiple_questions_agreements":
            """Mitä sopimuksia on tehty? Ketkä sopimuksia ovat tehneet? Mitä sopimuksissa lukee?""",
                        "multiple_questions_schedule":
            """Onko työmaa myöhässä aikataulusta? Mitkä työt ovat aikataulua jäljessä ja miksi? Mitä aikataulusta sanotaan?""",
                        "create_your_own_questions":
                        """"""
    }