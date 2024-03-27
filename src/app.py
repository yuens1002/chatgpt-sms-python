from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import OpenAIEmbeddings
from utils import pdf_qa as pqa
from prompt.chat_prompt_chain import ChatPrompt
from utils.chat_session import GlobalChatHistory, handle_incoming_sms
from utils.SQLite_setup import UserDb

chain = ChatPrompt().chain
global_chat_history = GlobalChatHistory()
db = UserDb()
# v_store = pqa.create_vector_store("data.pdf", "v_store", OpenAIEmbeddings())
app = Flask(__name__)


@app.route("/sms", methods=["POST"])
def sms_chat():
    """get incoming message"""
    inb_msg = request.form["Body"].lower()
    from_phone = request.form["from"]

    output = handle_incoming_sms(db, from_phone, chain, global_chat_history, inb_msg)

    # Start TwiML response
    resp = MessagingResponse()

    # write output to the message property
    resp.message(output)

    # Add a message
    # qa_res = pqa.query_store(v_store, inb_msg)
    # print(qa_res)
    # resp.message(qa_res)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
