####################################################
            #Retrieval Code#
####################################################
# __import__('pysqlite3')
import sys
from langchain.schema import Document
import tiktoken
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

tokenizer = tiktoken.get_encoding('cl100k_base')

# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

# This text splitter is used to create the parent documents
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)
# This text splitter is used to create the child documents
# It should create documents smaller than the parent
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)

vectorstore = Chroma(
    collection_name="solarpdfparent",
    embedding_function=OpenAIEmbeddings()
)
# The storage layer for the parent documents
store = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore, 
    docstore=store, 
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

with open(r"main.md", 'r', encoding='utf-8') as f:
    markdown_text = f.read()

doc = Document(page_content=markdown_text)

retriever.add_documents([doc])


#############################################################################################

