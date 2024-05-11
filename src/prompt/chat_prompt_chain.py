from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from utils import pdf_qa as pqa
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()


class ChatPrompt:
    def __init__(self):
        self.v_store = pqa.create_vector_store(
            "data.pdf", "v_store", OpenAIEmbeddings()
        )
        self.retriever = self.v_store.as_retriever(k=4)
        self.chat = ChatOpenAI(
            model="gpt-4-0125-preview", temperature=0.1, streaming=False
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You're a sms booking agent for a housing rental company. 
                    You're given a knowledge base (see context below) for a specific property and a set of 
                    calendar tools for related property showing tasks. Say "I don't know" if the context given 
                    is irrelevant to the user question. When scheduling, if the exact date and time is not available, 
                    suggest the next 3 best choices before showing your results. Converse using fewer than 140 
                    characters whenever possible in user's language with an upbeat go-getter attitude while 
                    maintaining a professional composure.
                 
                    <context>{context}</context>
                    """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.query_transform_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
                ),
            ]
        )

        self.chain = self.prompt | self.chat
        self.document_chain = create_stuff_documents_chain(self.chat, self.prompt)
        self.query_transformation_chain = self.query_transform_prompt | self.chat
        self.conversational_retrieval_chain = RunnablePassthrough.assign(
            context=self._query_transforming_retriever_chain(),
        ).assign(
            answer=self.document_chain,
        )

    def _query_transforming_retriever_chain(self, k=4):
        return RunnableBranch(
            (
                lambda x: len(x.get("messages", [])) == 1,
                # If only one message, then we just pass that message's content to retriever
                (lambda x: x["messages"][-1].content) | self.retriever,
            ),
            # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
            self.query_transform_prompt
            | self.chat
            | StrOutputParser()
            | self.retriever,
        ).with_config(run_name="chat_retriever_chain")
