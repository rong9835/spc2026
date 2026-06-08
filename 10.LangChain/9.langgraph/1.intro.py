from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END, MessagesState


load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')
