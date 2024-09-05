# -*- coding: utf-8 -*-
import os
from langchain_huggingface import HuggingFaceEmbeddings
# You might need to setup your grok api key
os.environ["GROQ_API_KEY"] = "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"
from langchain_groq import ChatGroq

import sys
path_ = "E:/github/multisensor_llm"
if not(path_ in sys.path):
    sys.path.insert(0,path_)
from rag_utils import rag_utils as ragu
from recommend_utils import recommend_utils as recu

#%% Get RAG system for recommendation
base_path = 'E:/github/multisensor_llm/Data/' #You might need to edit it
dataframe_path = os.path.join(base_path, 'Recommendation','text.pickle') 
db_name =  'recommendation_chroma_db' #See example_recommendation_database.py to get an example of how to build a database
cache_dir = os.path.join(base_path,'Recommendation', db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
# modèle entraîné sur des blogs financiers
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  
RAG = ragu.RAG(dataframe_path, cache_dir, llama3,
             finlang_embed) 
RAG.create_retriever({'k':4,})
#%% instantiate recommender object
recommender = recu.Recommender(llama3, RAG)

#%% Get a recommendation
# Sometimes the retrieved documents are not very useful, maybe look into search_kwargs ??
reco = recommender.get_recommendation('FOMO')
print(reco)