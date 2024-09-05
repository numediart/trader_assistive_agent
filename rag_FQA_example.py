# -*- coding: utf-8 -*-
from langchain_huggingface import HuggingFaceEmbeddings
import os
# You might need to setup your grok api key
import sys
path_ = "E:/github/multisensor_llm"
if not(path_ in sys.path):
    sys.path.insert(0,path_)
# os.environ["GROQ_API_KEY"]
from langchain_groq import ChatGroq
from rag_utils import rag_utils as rag
#%% Init the rag.RAG object
base_path = 'E:/github/multisensor_llm/Data/' #You might need to edit it
dataframe_path = os.path.join(base_path, 'FQA','text.pickle')
db_name =  'FQA_chroma_db'
cache_dir = os.path.join(base_path,'FQA', db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers

# Either path_csv or PERSIST_directory should be not none
# if the database already exists, the csv_path is not used
RAG = rag.RAG(dataframe_path, cache_dir, llama3,
             finlang_embed) 

#%% Example
# q = "What can you tell me about the 403(b) ?"
q = "What can you tell me about bankruptcy ?"
q = "What can you tell me about financial statements ?"
#q = "What can you tell me about strategie to reduce taxations ?"
#q = "Should I sell or buy bad performing stocks ?"
print(RAG.retrieve_answer(q,
                      print_context = False))