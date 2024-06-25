import tiktoken
from openai import OpenAI

default_system = "You are a helpful assistant. Try to answer very shortly and be precise. Return your answer in JSON format."


class LLMInfo:
    allowed_models = ['gpt-3.5-turbo-0125', 'gpt-4-0125-preview', 'gpt-4', 'gpt-4-32k']
    providers = {'gpt-3.5-turbo-0125': 'OpenAI', 'gpt-4-0125-preview': 'OpenAI', 'gpt-4': 'OpenAI', 'gpt-4-32k': 'OpenAI'}
    token_limits = {'gpt-3.5-turbo-0125': 16000, 'gpt-4-0125-preview': 128000, 'gpt-4': 8000, 'gpt-4-32k': 32000}
    pricing_per_1k_tokens = {'gpt-3.5-turbo-0125': [0.0005, 0.0015], 'gpt-4-0125-preview': [0.01, 0.03], 'gpt-4': [0.03, 0.06], 'gpt-4-32k': [0.06, 0.12]}
    supports_json_response = ['gpt-3.5-turbo-0125', 'gpt-4-0125-preview']

    def __init__(self, model=None):
        self.model = model

    def is_allowed_model(self, model):
        return True if model in LLMInfo.allowed_models else False

    def get_info_dict(self):
        table_rows = []
        for model in LLMInfo.allowed_models:
            row = {
                "Available models": model,
                "Model provider": LLMInfo.providers.get(model, 'Unknown'),
                "Token limit (pcs)": LLMInfo.token_limits.get(model, None),
                "Pricing input ($/k-tokens)": LLMInfo.pricing_per_1k_tokens.get(model, None)[0] if type(LLMInfo.pricing_per_1k_tokens.get(model, None)) == list else None,
                "Pricing output ($/k-tokens)": LLMInfo.pricing_per_1k_tokens.get(model, None)[1] if type(LLMInfo.pricing_per_1k_tokens.get(model, None)) == list else None,
                "Supports JSON": model in LLMInfo.supports_json_response
            }
            table_rows.append(row)
        return table_rows

    def get_pricing(self, model=None):
        """

        :param model:
        :return:
        """
        if not model:
            return LLMInfo.pricing_per_1k_tokens
        elif model in LLMInfo.pricing_per_1k_tokens:
            return LLMInfo.pricing_per_1k_tokens[model]
        else:
            raise KeyError(f"Model {model} doesn't belong to allowed models. Allowed models are: {LLMInfo.allowed_models}.")

    def get_token_limits(self, model=None):
        """

        :param model:
        :return:
        """
        if not model:
            return LLMInfo.token_limits
        elif model in LLMInfo.token_limits:
            return LLMInfo.token_limits[model]
        else:
            raise KeyError(f"Model {model} doesn't belong to allowed models. Allowed models are: {LLMInfo.allowed_models}.")

    def estimate_cost(self, model, prompt: str or int, output=None) -> float:
        """

        :param model:
        :param prompt:
        :param output:
        :return:
        """
        if model not in LLMInfo.allowed_models:
            raise KeyError(
                f"Model {model} doesn't belong to allowed models. Allowed models are: {LLMInfo.allowed_models}.")
        if type(prompt) == str:
            input_tokens = Text2Token().num_of_tokens_in_text(text=prompt)
        elif type(prompt) == int:
            input_tokens = prompt
        else:
            raise TypeError(f"Prompt not in allowed format. Either text or int is allowed!")
        if output:
            if type(output) == str:
                output_tokens = Text2Token().num_of_tokens_in_text(text=output)
            elif type(output) == int:
                output_tokens = output
            else:
                raise TypeError(f"Output not in allowed format. Either text or int is allowed!")
            return (input_tokens / 1000) * self.get_pricing(model)[0] + (output_tokens / 1000) * self.get_pricing(model)[1]
        else:
            return (input_tokens / 1000) * self.get_pricing(model)[0]


class OpenAILLMService:

    def __init__(self, api_key, model='gpt-3.5-turbo-0125', temperature=0):
        self.api_key = api_key
        self.model = model
        self.model_temp = temperature
        self.token_lim = LLMInfo().get_token_limits(model) if LLMInfo().is_allowed_model(model) else 8000
        self.client = OpenAI(api_key=self.api_key)

    def set_new_model(self, model):
        self.model = model
        self.token_lim = LLMInfo().get_token_limits(model) if LLMInfo().is_allowed_model(model) else 8000

    def set_temperature(self, temperature):
        self.model_temp = temperature

    @staticmethod
    def validate_messages(messages):
        if not isinstance(messages, list):
            return False
        if len(messages) < 2:
            return False

        for message in messages:
            if not isinstance(message, dict):
                return False
            if 'role' not in message or not isinstance(message['role'], str):
                return False
            if 'content' not in message or not isinstance(message['content'], str):
                return False

        return True

    def query_llm_multi_messages(self, messages):
        """
        Query LLM so that messages are in list. This enables LLM to have "memory". Same token limits apply.
        :param messages:
        :return: content as string, prompt_tokens and ans_tokens as int
        """
        if not self.validate_messages(messages):
            raise ValueError("Messages that are fed to LLM must be in list of dicts and each dict must have 'role' and 'content' keys!")

        message_size = Text2Token().num_of_tokens_in_messages(messages=messages)
        if message_size + 1000 > self.token_lim:
            raise Exception(f"TOKEN LIMIT ERROR! Selected model's limit is {self.token_lim} tokens! "
                            f"Messages has in total {message_size} tokens and 1000 has been reserved for the answer.")

        if self.model in LLMInfo.supports_json_response:
            response = self.client.chat.completions.create(model=self.model,
                                                           temperature=self.model_temp,
                                                           response_format={"type": "json_object"},
                                                           messages=messages)
        else:
            response = self.client.chat.completions.create(model=self.model,
                                                           temperature=self.model_temp,
                                                           messages=messages)
        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        prompt_tokens = response.usage.prompt_tokens
        ans_tokens = response.usage.completion_tokens
        return content, prompt_tokens, ans_tokens


    def query_llm(self, prompt, system=default_system):
        """

        :param prompt:
        :param system:
        :return: content as string and total_tokens as int
        """
        prompt_size = Text2Token().num_of_tokens_in_text(prompt)
        system_size = Text2Token().num_of_tokens_in_text(system)
        if prompt_size + system_size + 500 > self.token_lim:
            raise Exception(f"Too many tokens in the prompt! Selected model's limit is {self.token_lim} tokens! Prompt "
                            f"and system message has in total {prompt_size+system_size} tokens and 500 has been "
                            f"reserved for the answer.")
        if self.model in LLMInfo.supports_json_response:
            response = self.client.chat.completions.create(model=self.model,
                                                       temperature=self.model_temp,
                                                       response_format={"type": "json_object"},
                                                       messages=[{"role": "system", "content": system},
                                                          {"role": "user", "content": prompt}])
        else:
            response = self.client.chat.completions.create(model=self.model,
                                                           temperature=self.model_temp,
                                                           messages=[{"role": "system", "content": system},
                                                                     {"role": "user", "content": prompt}])
        content = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        prompt_tokens = response.usage.prompt_tokens
        ans_tokens = response.usage.completion_tokens
        return content, prompt_tokens, ans_tokens


class Text2Token:

    def __init__(self, llm_model: str = "gpt-3.5-turbo-16k"):
        """
        Initializes an instance of the Text2Token class with an optional language model name.
        :param llm_model: The name of the language model to use for tokenization (default is "gpt-3.5-turbo-16k").
        """
        try:
            self.encoder = tiktoken.encoding_for_model(llm_model)
            self.model = llm_model
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            self.encoder = tiktoken.get_encoding("cl100k_base")
            self.model = "cl100k_base"

    def _encode_text(self, text):
        return self.encoder.encode(text)

    def _decode_tokens(self, tokens):
        return self.encoder.decode(tokens)

    def num_of_tokens_in_text(self, text: str) -> int:
        """
        Calculates the number of tokens in the input text.
        :param text: The input text for which to calculate the number of tokens.
        :return: The number of tokens in the text as an integer.
        """
        if not isinstance(text, str):
            raise TypeError(f"Invalid type for text! {type(text)} is not acceptable!")
        return len(self._encode_text(text))

    def encode_text_to_tokens(self, text: str) -> list[int]:
        """
        Encodes the input text into tokens and returns a list of token IDs.
        :param text: The input text to encode.
        :return: A list of token IDs representing the encoded text.
        """
        if not isinstance(text, str):
            raise TypeError(f"Invalid type for text! {type(text)} is not acceptable!")
        return self._encode_text(text)

    def decode_tokens_to_text(self, tokens: list) -> str:
        """
        Decodes a list of token IDs back into text and returns the decoded text.
        :param tokens: A list of token IDs to decode.
        :return: The decoded text as a string.
        """
        if not isinstance(tokens, list) or not all(isinstance(token, int) for token in tokens):
            raise TypeError(f"Invalid type for tokens! {type(tokens)} is not acceptable!")
        return self._decode_tokens(tokens)

    def num_of_tokens_in_messages(self, messages, model=None):
        """Return the number of tokens used by a list of messages.
        :param model:
        :param list: The list of dicts that contains messages.
        :return: A list of token IDs representing the encoded text.
        """
        if not model:
            model = self.model

        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-16k",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            'gpt-3.5-turbo-0125',
            'gpt-4-0125-preview',
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_of_tokens_in_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_of_tokens_in_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}.""")

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self._encode_text(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
