import argparse

# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import dotenv_values
import asyncio
import halo_api

CHROMA_PATH = dotenv_values()["CHROMA_PATH"]
OPENAI_API_KEY = dotenv_values()["OPENAI_API_KEY"]


async def query_db(question: str, ticket_id, db: Chroma):
    # Search the DB.
    if ticket_id is None:
        request = f"Primary Question: {question}"
    else:
        ticket_info = await halo_api.get_ticket(ticket_id)
        request = (
            f"Primary Question: {question}. Ticket Subject: {ticket_info['summary']}."
        )
    results = db.similarity_search_with_relevance_scores(request, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    scores = [score for _doc, score in results]
    if len(results) == 0 or results[0][1] < 0.5:
        output = "No relevant articles found."
        return output, sources, scores
    return context_text, sources, scores


async def create_prompt(question: str, ticket_id: int, db: Chroma):
    results, sources, scores = await query_db(question, ticket_id, db)
    formatted_sources = "\n".join(
        f"{i + 1}. {src} (score={score:.3f})"
        for i, (src, score) in enumerate(zip(sources, scores))
    )
    PROMPT = f"""
            You are a support agent bot that answers user questions *only* using the knowledge base context provided.

            If the context does not contain enough information to confidently answer,
            say that you don't know and suggest the user contact a human agent.

            ---------------- CONTEXT START ----------------
            {results}
            ----------------- CONTEXT END -----------------

            Question:
            {question}

            Instructions:
            - Base your answer only on the context above. Do not use outside knowledge.
            - If relevant information is missing from the context, say you don't know.
            - Be clear and concise, and write in a helpful, professional tone.
            - At the end, list the sources you used and their scores.

            After your answer, output:

            Sources:
            <Source 1> <Score 1>
            <Source 2> <Score 2>
            ...

            Available sources and scores:
            {formatted_sources}
            """
    return PROMPT


async def get_response(prompt: str, ticket_id):
    embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    # prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)
    prompt = await create_prompt(prompt, ticket_id, db)
    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
    response_text = model.invoke(prompt).content

    formatted_response = f"{response_text}\n"
    return formatted_response


if __name__ == "__main__":
    asyncio.run(get_response())
