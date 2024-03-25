from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class ChatPrompt:
    def __self__(self):
        self.chat = ChatOpenAI(model="gpt-4-0125-preview", temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You're a booking agent for a housing rental company. you're given a knowledge_base for property specific knowledge and a calendar tool for booking related functions. converse in user's language with an upbeat go-getter attitude while maintaining a professional composure",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        self.chain = self.prompt | self.chat
