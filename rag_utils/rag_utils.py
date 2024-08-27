from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
import os
import pandas as pd
# os.environ["GROQ_API_KEY"] 
from langchain_groq import ChatGroq
from types import SimpleNamespace
from tqdm import tqdm

def load_csv_to_documents(path_csv, separator='\t'):
    try:
        df = pd.read_csv(path_csv, encoding="utf-8", sep=separator) #encoding="windows-1252"
    except Exception as e:
        print(f"Error reading the CSV file: {path_csv}")
        print(f"Exception: {e}")
        return []
    
    documents = []
    print('Total number of documents : ', df.shape[0])
    for index, row in tqdm(df.iterrows()):
        try:
            document = SimpleNamespace(
                page_content=f"{row['Method Name']}: {row['Definition']}",
                metadata={'method_name': row['Method Name']}
            )
            documents.append(document)
        except Exception as e:
            document = SimpleNamespace(
                page_content=f"{row[0]}",
                metadata={}
            )
            documents.append(document)
    return documents

def load_chromadb(cache_dir, embedding_function, csv_dir = None, separator='\t'):
    if os.path.exists(cache_dir):
        #print("Loading Chroma database")
        db = Chroma(persist_directory=cache_dir, embedding_function=embedding_function)
    else:
        if csv_dir is None:
            raise FileNotFoundError('Did not find a cached database and no csv path provided.')
        print("No cached database found. Creating Chroma database.")
        documents = load_csv_to_documents(csv_dir)
        db = Chroma.from_documents(documents=documents, 
                                   embedding=embedding_function, 
                                   persist_directory=cache_dir)
        db.persist()
    return db
        
        
def retrieve_answer(question, retriever, model, print_context = False):
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    if print_context:
        print(retriever.invoke(question))
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, 
         "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain.invoke(question)


if __name__ == "__main__":
    PATH_CSV = 'Data/Financial_and_Technical_Analysis_Methods_t.csv'
    db_name = os.path.splitext(os.path.basename(PATH_CSV))[0] + '_db.pkl'
    PERSIST_DIRECTORY = os.path.join('Data', db_name)
    llama3 = ChatGroq(model="llama3-8b-8192")
    finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers
    
    db = load_chromadb(PERSIST_DIRECTORY, finlang_embed)
    retriever = db.as_retriever()
    print(retrieve_answer("List five methods that are based on average calculation.",
                          retriever,
                          llama3))


