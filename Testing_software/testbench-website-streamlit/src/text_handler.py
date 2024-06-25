import ast
import numpy as np
import pandas as pd
from src.llm_handler import OpenAILLMService, LLMInfo, Text2Token
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


class EmbeddingInfo:

    def __init__(self):
        self.allowed_splitting_methods = ['RecursiveCharacterTextSplitter', 'CharacterTextSplitter']
        self.allowed_embedding_methods = ['OpenAIEmbeddings']

    def get_splitting_methods(self):
        return self.allowed_splitting_methods

    def get_embedding_methods(self):
        return self.allowed_embedding_methods


class TextEmbedder:
    """Gets text and returns it chunked with its vector representations"""

    def __init__(self, openai_key, chunk_size=1000, chunk_overlap=50, split_method='RecursiveCharacterTextSplitter', emb_method='OpenAIEmbeddings'):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.split_method = split_method
        self.emb_method = emb_method
        self.openAI_key = openai_key


    def split_text(self, text):
        if self.split_method == 'RecursiveCharacterTextSplitter':
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap,
                                                           length_function=len, is_separator_regex=False)
        else:
            text_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=self.chunk_size,
                                                  chunk_overlap=self.chunk_overlap, length_function=len, is_separator_regex=False,)

        chunks = text_splitter.split_text(text)
        return chunks

    def vectorize_text(self, text):
        pass


    def langchain_embeddings(self, chunk):
        try:
            embeddings_model = OpenAIEmbeddings(openai_api_key=self.openAI_key)
            embeddings = embeddings_model.embed_query(chunk)
            return embeddings
        except Exception as error:
            raise Exception(f"This error occurred: {error}")

    def embed_text_into_vectors(self, text):
        chunks = self.split_text(text)
        total = len(chunks)
        to_return = []  # (split_method, emb_method, chunk_num, total_num, org_text, vector)
        for ind, chunk in enumerate(chunks, start=1):
            to_return.append((self.split_method, self.emb_method, ind, total, chunk, str(self.langchain_embeddings(chunk))))
        return to_return


class SemanticSearch:

    def __init__(self, text_embedder=None, openaikey=None, chunk_num=3):
        if not text_embedder and not openaikey:
            raise ValueError("Either TextEmbedder object or OpenAI API key must be provided!")
        self.text_embedder = text_embedder
        self.openAIkey = openaikey
        self.chunk_num = chunk_num

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get_embedding(self, text):
        if not self.text_embedder:
            self.text_embedder = TextEmbedder(openai_key=self.openAIkey)
        return self.text_embedder.langchain_embeddings(chunk=text)

    def search_docs(self, df: pd.DataFrame or dict, user_query: str, chunk_num=None):
        if not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception:
                raise TypeError("Vectors must be in df or in correctly formatted dict containing column 'vector'!")
        if 'vector' not in df.columns:
            raise TypeError("Dataframe must contain column 'vector'!")

        if not chunk_num:
            chunk_num = self.chunk_num

        embedding = self.get_embedding(user_query)

        df['vector'] = df['vector'].apply(lambda x: [float(num) for num in ast.literal_eval(x)])

        df["similarities"] = df.vector.apply(lambda x: self.cosine_similarity(x, embedding))

        res = df.sort_values("similarities", ascending=False).head(chunk_num).to_dict()

        return res


