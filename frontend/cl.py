import chainlit as cl
import requests

@cl.on_message
async def on_message(message: cl.Message):
    # Get all the messages in the conversation in the OpenAI format
    message_thread = cl.chat_context.to_openai()
    
    response = requests.post("https://chat.whitedune-3fe30ea7.eastus.azurecontainerapps.io/chat", json=message_thread).json()
    print(response)
    
    await cl.Message(response).send()