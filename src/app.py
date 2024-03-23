from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import OpenAIEmbeddings
from utils import pdf_qa as pqa


v_store = pqa.create_vector_store("data.pdf", "v_store", OpenAIEmbeddings())
app = Flask(__name__)


@app.route("/sms", methods=["POST"])
def sms_chat():
    """get incoming message"""
    inb_msg = request.form["Body"].lower()
    print(inb_msg)
    # Start our TwiML response
    resp = MessagingResponse()
    # Add a message
    qa_res = pqa.query_store(v_store, inb_msg)
    print(qa_res)
    resp.message(qa_res)

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
