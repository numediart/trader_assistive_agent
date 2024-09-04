# -*- coding: utf-8 -*-
import os
from langchain_huggingface import HuggingFaceEmbeddings
import os
# You might need to setup your grok api key
# os.environ["GROQ_API_KEY"]
from langchain_groq import ChatGroq

import sys
path_ = "E:/github/multisensor_llm"
if not(path_ in sys.path):
    sys.path.insert(0,path_)
from rag_utils import rag_utils as rag
#%% Init the rag.RAG object
base_path = 'E:/github/multisensor_llm/Data/behavior' #You might need to edit it
path_csv = os.path.join(base_path, 'behaviour_database_v0.csv')
db_name = os.path.splitext(os.path.basename(path_csv))[0] + '_db'
PERSIST_DIRECTORY = os.path.join(base_path, db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
# modèle entraîné sur des blogs financiers
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  

# Either path_csv or PERSIST_directory should be not none
# if the database already exists, the csv_path is not used
RAG = rag.RAG(path_csv, PERSIST_DIRECTORY, llama3,
             finlang_embed, csv_separator = '\t') 
RAG.create_retriever(search_kwargs = {'k':10})
#%% Example with RAG
q = '''Can you give a small overwiev of the Fear of Missing out phenomenon,
why it should be avoided and how to avoid it when trading ? Which kind of routine could a trader
implement to avoid FOMO ?'''
rag_answer = RAG.retrieve_answer(q,
                      print_context = False)
print('\n\n ============ WITH RAG ================== \n\n')
print(rag_answer)

#%% Test without RAG
from langchain_core.output_parsers import StrOutputParser
print('\n\n ============ WITHOUT RAG ================== \n\n')
print(StrOutputParser().invoke(RAG.model.invoke(q)))