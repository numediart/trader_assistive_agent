# -*- coding: utf-8 -*-
from langchain_core.output_parsers import StrOutputParser

#%%
base_prompt = '''"Write a prompt to query a Question Answering system about trading in order to inform the trader in the following context: '''
init_prompts = {
    'FOMO':'''The trader is experiencing fear of missing out or FOMO. Generate a prompt to query the database
    in order to provide them with relevant information about FOMO and trading so that they can adjust their behavior and decisions to perform the best.''',
    'Anger':'''The trader is experiencing anger. Generate a prompt to query the database
    in order to provide them with relevant information about anger and trading so that they can adjust their behavior and decisions to perform the best. '''
    }

#%%
class Recommender:
    def __init__(self, LLM, QA_system):
        self.QA = QA_system
        self.LLM = LLM
        self.llm_out_parser = StrOutputParser()
        return None
    
    def get_recommendation(self, string):
        inital_prompt = base_prompt + string
        raw_query_prompt = self.LLM.invoke(inital_prompt)
        parsed_raw_query_prompt = self.llm_out_parser.invoke(raw_query_prompt)
        query_prompt = self.llm_out_parser.invoke(parsed_raw_query_prompt)
        try:
            idx = query_prompt.index('Prompt')
            query_prompt = query_prompt[idx+6:]
        except ValueError:
            pass
        out = self.QA.retrieve_answer(query_prompt)
        return out
    
