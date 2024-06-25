import tiktoken

class TestPromptsAndText():
    t_prompt = """Always follow these instructions when responding to the user's questions:
                 - Return only the questions and answers separated by a colon in this format 'Question: answer'. For example, like this -> What is the name of the project?: Example Project 1.
                 - Do not return anything other than question-answer pairs.
                 - Answer with using finnish as a language.
                 - Always try to find all possible answers from the text."""

    t_questions = """What is the name of the project?,
                     Where is the project located?,
                     When was the meeting held?,
                     How many people were present?,
                     Who were present?,
                     How many individuals from different companies were present?,
                     Who was absent and from which companies?,
                     Which companies had no one present?,
                     When will the project be fully completed?,
                     What work is scheduled to be completed first according to the timeline?,
                     What issues are mentioned under the schedule heading?,
                     What is said about electrical work?,
                     Which model works are completed?,
                     What is the result of the safety measurement?,
                     What remarks were made about safety?,
                     Were there any comments from the supervisors?,
                     What other matters were discussed?,
                     What attachments are included?"""

    t_text = """
    
    """


def token_counter():
    materials = TestPromptsAndText()
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
    num_t = encoding.encode(materials.t_text)
    print(len(num_t))

def printer():
    materials = TestPromptsAndText()
    print(materials.t_questions)

if __name__ == "__main__":
    token_counter()
