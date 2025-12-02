from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from utils import get_config_value
import chromadb
import httpx
from typing import List


CHROMA_HOST_IP = get_config_value("CHROMA_HOST_IP")
CHROMA_HOST_PORT = get_config_value("CHROMA_HOST_PORT")
OPENAI_API_KEY = get_config_value("OPENAI_API_KEY")
CHROMA_COLLECTION_NAME = "halo_knowledge_base"
HALO_BASE_URL = get_config_value("HALO_BASE_URL")
HALO_CLIENT_ID = get_config_value("HALO_CLIENT_ID")
HALO_CLIENT_SECRET = get_config_value("HALO_CLIENT_SECRET")


def get_kb_token():
    url = f"{HALO_BASE_URL}/auth/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": HALO_CLIENT_ID,
        "client_secret": HALO_CLIENT_SECRET,
        "scope": "read:kb",
    }

    try:
        with httpx.Client() as client:
            resp = client.post(
                url,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            # print(resp.json()["access_token"])
            token_data = resp.json()
            return token_data["access_token"]
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (TOKEN) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("=========================\n")
        raise


def get_knowledge_base_article(article_id: int, token):
    # TODO: Implement this function to fetch knowledge base articles
    url = f"{HALO_BASE_URL}/api/KBArticle/{article_id}"
    try:
        with httpx.Client() as client:
            resp = client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (KB) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("===========================\n")
        raise


def get_knowledge_base_contents(token):
    url = f"{HALO_BASE_URL}/api/KBArticle"
    try:
        with httpx.Client() as client:
            resp = client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            response = resp.json()
            return [a["id"] for a in response["articles"]]
    except httpx.HTTPStatusError as e:
        print("\n=== HTTP ERROR (KB) ===")
        print(f"URL: {e.request.url}")
        print(f"Status: {e.response.status_code}")
        print(f"Body: {e.response.text}")
        print("===========================\n")
        raise


def convert_to_langchain_doc(article):
    art_id = article.get("id")
    title = article.get("name", "Untitled")
    desc = article.get("description", "") or ""
    tags = article.get("tag_string", "") or ""
    resolution = article.get("resolution", "") or ""

    content = (
        f"Title: {title}\nDescription: {desc.strip()}\nResolution: {resolution.strip()}"
    )

    metadata = {
        "source": "HaloPSA",
        "kb_article_id": art_id,
        "title": title,
        "tags": tags,
        "date_modified": article.get("date_modified"),
    }

    return Document(page_content=content, metadata=metadata)


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        add_start_index=True,
    )

    split_docs = text_splitter.split_documents(documents)
    return split_docs


def run_ingestion():
    token = get_kb_token()
    kb_contents = get_knowledge_base_contents(token)

    all_documents: List[Document] = []
    for article_id in kb_contents:
        try:
            article_data = get_knowledge_base_article(article_id, token)
            doc = convert_to_langchain_doc(article_data)
            all_documents.append(doc)
        except Exception as e:
            print(f"Error exporting article: {e}")
            continue

    if not all_documents:
        print("No documents were successfully prepared. Exiting.")
        return

    split_docs = split_documents(all_documents)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    print(f"Connecting to remote ChromaDB at {CHROMA_HOST_IP}:{CHROMA_HOST_PORT}...")
    db = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        client=chromadb.HttpClient(host=CHROMA_HOST_IP, port=CHROMA_HOST_PORT),
    )

    print(f"Successfully vectorized and stored {len(split_docs)} chunks.")

    return db


if __name__ == "__main__":
    run_ingestion()
