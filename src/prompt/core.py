from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from utils import pdf_qa as pqa
from langchain_openai import OpenAIEmbeddings

load_dotenv()


def get_chat_response(name, user_input, characteristics):

    chat_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a housing agent for {company_name} who has been given a {knowledge_base} for a property. you have the ability to converse in the language used by the user and you should have an {characteristic} attitude.",
            ),
            ("human", "{user_input}"),
        ]
    )

    v_store = pqa.create_vector_store("data.pdf", "v_store", OpenAIEmbeddings())
    context = v_store.similarity_search(query=user_input, k=3)

    messages = chat_template.format_messages(
        company_name=name,
        user_input=user_input,
        knowledge_base=context,
        characteristics=characteristics,
    )

    chat = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)

    return chat.invoke(messages)


msg = get_chat_response(
    name="sunny & tina",
    user_input="what are a few landmarks close to the property?",
    characteristics="cheerful",
)
print(msg)
