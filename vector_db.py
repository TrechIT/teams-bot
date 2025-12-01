from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import dotenv_values
import utils
import halo_api

config = dotenv_values()
CHROMA_PATH = config["CHROMA_PATH"]
DATA_PATH = config["DATA_PATH"]
OPENAI_API_KEY = config["OPENAI_API_KEY"]


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="**/*.txt")
    documents = loader.load()
    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        add_start_index=True,
    )

    split_docs = text_splitter.split_documents(documents)
    return split_docs


def create_vector_store():
    # if config.path.exists(CHROMA_PATH):
    # shutil.rmtree(CHROMA_PATH)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = Chroma.from_documents(
        split_documents(load_documents()), embeddings, persist_directory=CHROMA_PATH
    )

    db.persist()


if __name__ == "__main__":
    load_documents()
    split_documents(load_documents())
    create_vector_store()
