# -*- coding: utf-8 -*-
import os
from langchain_huggingface import HuggingFaceEmbeddings
import os
# You might need to setup your grok api key
# os.environ["GROQ_API_KEY"]  = ""
from langchain_groq import ChatGroq
from rag_utils import rag_utils as rag
#%% Init the rag.RAG object
base_path = './Data' #You might need to edit it
path_csv = os.path.join(base_path, 'raw_investopedia.csv')
db_name = os.path.splitext(os.path.basename(path_csv))[0] + '_db'
PERSIST_DIRECTORY = os.path.join(base_path, db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers

# Either path_csv or PERSIST_directory should be not none
# if the database already exists, the csv_path is not used
RAG = rag.RAG(path_csv, PERSIST_DIRECTORY, llama3,
             finlang_embed, csv_separator = '\t') 

#%% Example
# q = "What can you tell me about the 403(b) ?"
q = "What can you tell me about bankruptcy ?"
q = "What can you tell me about financial statements ?"
q = "What can you tell me about strategie to reduce taxations ?"
q = "Should I sell or buy bad performing stocks ?"
print(RAG.retrieve_answer(q,
                      print_context = False))