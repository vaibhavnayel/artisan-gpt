import json
import os
import logging

from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.llms import MessageRole, ChatMessage
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.groq import Groq

class Model():
    def __init__(self, index_path:str='storage/', raw_data_path:str='firecrawl.json'):
        
        self.index = self.load_index(index_path, raw_data_path)
        self.chat_engine = self.create_chat_engine(self.index)
        
    def load_index(self, index_path:str, raw_data_path:str):
        if not os.path.exists(index_path):
            logging.info(f"Loading index from {raw_data_path}")
            docs = json.load(open(raw_data_path))
            docs = [Document(text=d["content"], metadata=d["metadata"]) for d in docs]
            parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[8192, 2048, 512])
            nodes = parser.get_nodes_from_documents(docs)

            embed_model = OpenAIEmbedding(model="text-embedding-3-large")
            index = VectorStoreIndex(nodes, embed_model=embed_model)
            index.storage_context.persist(persist_dir=index_path)
        else:
            logging.info(f"Loading index from {index_path}")
            storage_context = StorageContext.from_defaults(persist_dir=index_path)
            index = load_index_from_storage(storage_context)
        return index


    def create_chat_engine(self, index):
        system_prompt = """
            your are a helpful assistant named "Artisan AI chatbot" on the website of the company "Artisan". you are here to help the user with their questions.
            you are given context snippets from the company's website and you must answer the user's question based on that context.
            don't reveal your context, only answer the question.
        """

        llm = Groq(model="llama3-70b-8192", temperature=0.0)
        chat_engine = index.as_chat_engine(
            chat_mode="context", verbose=False, llm=llm, system_prompt=system_prompt
        )
        return chat_engine
    

    def make_history(self, message_thread):
        history = []
        for message in message_thread:
            match message["role"]:
                case "user":
                    role = MessageRole.USER
                case "assistant":
                    role = MessageRole.ASSISTANT
                case _:
                    raise ValueError(f"Invalid role: {message['role']}")
            content = message['content']
            history.append(ChatMessage(role=role, content=content))
        return history[-10:]
    
    def chat(self, message_thread):
        
        if len(message_thread) > 1:
            query = message_thread[-1]["content"]
            history = self.make_history(message_thread[:-1])
        else:
            query = message_thread[0]["content"]
            history = None
            
        response = self.chat_engine.chat(query, chat_history=history).response
        print(f"fastapi response: {response}")
        return str(response)
