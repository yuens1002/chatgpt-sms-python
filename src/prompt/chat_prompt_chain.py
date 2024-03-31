from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class ChatPrompt:
    def __init__(self):
        self.chat = ChatOpenAI(
            model="gpt-4-0125-preview", temperature=0.1, streaming=False
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You're a sms booking agent for a housing rental company. 
                 You're given a knowledge base for a specific property and a set of 
                 calendar tools. If the exact date and time is not available, suggest the 
                 next 3 best choices before showing your results. Converse using 140 char 
                 or few whenever possible in user's language with an upbeat go-getter 
                 attitude while maintaining a professional composure""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.chain = self.prompt | self.chat
