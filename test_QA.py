# -*- coding: utf-8 -*-
import pandas
import os
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)
from tqdm import tqdm
import torch
import numpy as np
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
# You might need to setup your grok api key
# os.environ["GROQ_API_KEY"]  = ""
s2s_path = "E:/github/multisensor_llm/"
import sys
if not(s2s_path in sys.path):
    sys.path.insert(0,s2s_path)
from rag_utils import rag_utils as rag

#%%
data_path = os.path.join(s2s_path, "./QA_benchmark/Data/Financial-QA-10k.csv")
# https://www.kaggle.com/datasets/visalakshiiyer/question-answering-financial-data
df = pandas.read_csv(data_path, sep = ',')

#%%
model_name="microsoft/Phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, trust_remote_code=True
).to('cuda')

pipe = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, device='cuda',  
)
#%%
template = '''' .Answer succinctly the following question: '''
q = df['question'][0]
kwargs = {
    "min_new_tokens": 20,
    "max_new_tokens": 120,
}
    
#%% Test direct answer with Phi-3-mini-4k-instruct
rng = np.random.default_rng()
all_answers = []
selected_questions_idx = []
with torch.no_grad():
    for jq in tqdm(range(df['question'].shape[0])):
        q = df['question'][jq]
        c = df['context'][jq]
        r = rng.uniform(0,1)
        if r < 0.005:
            prompt = c+template+q
            raw = pipe(prompt, **kwargs)
            start = len(prompt)
            a = raw[0]['generated_text'][start:]
            all_answers.append(a.replace('\n', ' '))
            print(a.replace('\n', ' '))
            selected_questions_idx.append(jq)
            
            
#%%
resu_df = pandas.DataFrame(data = {'questions idx':selected_questions_idx,
                                   'answers':all_answers}
                           )

resu_path = os.path.join(s2s_path, './QA_benchmark/Data/')
rmodel_name = model_name.replace('/', '_').replace('-','_')
resu_df.to_csv(os.path.join(resu_path, f'direct_{rmodel_name}.csv'))
#%% Test answer with llama3 (ChatGroq) + rag 
base_path = './Data' #You might need to edit it
path_csv = os.path.join(base_path, 'raw_investopedia.csv')
db_name = os.path.splitext(os.path.basename(path_csv))[0] + '_db'
PERSIST_DIRECTORY = os.path.join(base_path, db_name)
# Example with ChatGroq
llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers

# Either path_csv or PERSIST_directory should be not none
# if the database already exists, the csv_path is not used
RAG = rag.RAG(path_csv, PERSIST_DIRECTORY, llama3,
             finlang_embed, csv_separator = '\t') 

#%%
all_answers = []
for jq in tqdm(range(df['question'].shape[0])):
    if jq in selected_questions_idx:
        q = df['question'][jq]
        c = df['context'][jq]
        prompt = c+template+q
        a = RAG.retrieve_answer(prompt, )
        all_answers.append(a)

#%%
resu_df = pandas.DataFrame(data = {'questions idx':selected_questions_idx[:len(all_answers)],
                                   'answers':all_answers}
                           )

resu_path = os.path.join(s2s_path, './QA_benchmark/Data/')
resu_df.to_csv(os.path.join(resu_path, 'rag_llama3.csv'))