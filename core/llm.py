from langchain_openai import ChatOpenAI

def get_llm(temperature):
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature
    )
