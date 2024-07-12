"""
LLM node.
Process the message according to roles specified
Deploy on GPU servers.
"""


import threading
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from llama import Llama  # Follow the llama repo to build this dependency.
from pydantic import BaseModel
from contextlib import asynccontextmanager

from prompts import prompts



# Global state to maintain the conversation
conversation = []
last_request_time = datetime.now()
shutdown_timer = None
shutdown_delay = 300  # 300 seconds (5 minutes auto-shutdown, if no request come to this node)
processing = False  # Status flag


class DialogMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: DialogMessage
    functionality: Optional[str] = 'analysis'
    continue_conversation: Optional[bool] = False
    temperature: Optional[float] = 0.2
    top_p: Optional[float] = 0.7
    max_seq_len: Optional[int] = 512
    max_batch_size: Optional[int] = 4
    max_gen_len: Optional[int] = None


class ResetRequest(BaseModel):
    ckpt_dir: str
    tokenizer_path: str


# Initialize the LLama model (Singleton)
generator = None


def reset_shutdown_timer():
    global shutdown_timer
    if shutdown_timer:
        shutdown_timer.cancel()
    shutdown_timer = threading.Timer(shutdown_delay, shutdown_server)
    shutdown_timer.start()


def shutdown_server():
    import os
    os.system('/usr/bin/shutdown now')


@asynccontextmanager
async def lifespan(app: FastAPI):
    global generator
    try:
        generator = Llama.build(ckpt_dir='/root/original/',
                                tokenizer_path='/root/original/tokenizer.model',
                                max_seq_len=8192, max_batch_size=4, )
    except Exception as e:
        print(e)

    yield

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def update_last_request_time(request: Request, call_next):
    global last_request_time
    # if not requesting the status, update the time
    if request.url.path != "/status":
        last_request_time = datetime.now()
        reset_shutdown_timer()
    response = await call_next(request)
    return response

@app.post("/chat")
def chat(request: ChatRequest):
    global conversation, generator, processing

    if generator is None:
        try:
            generator = Llama.build(ckpt_dir='/root/original/',
                                    tokenizer_path='/root/original/tokenizer.model',
                                    max_seq_len=8192, max_batch_size=4, )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Auto init failed: " + str(e))

    if processing:
        raise HTTPException(status_code=503, detail="Server is busy")

    processing = True

    try:
        prompt = prompts.get(request.functionality, None)
        if prompt is not None:
            conversation = [{
                "role": "system",
                "content": prompt
            }]
        else:
            raise HTTPException(status_code=500, detail="No such role, update prompts.py")

        if generator is None:
            raise HTTPException(status_code=500, detail="Model not initialized")

        try:
            # Add the new user message to the conversation
            conversation.append(request.message.dict())

            # Generate the response
            dialogs = [conversation]
            results = generator.chat_completion(dialogs, max_gen_len=request.max_gen_len,
                                                temperature=request.temperature,
                                                top_p=request.top_p, )
            # Get the assistant's response and add it to the conversation
            assistant_response = {"role": "assistant", "content": results[0]['generation']['content']}
            if request.continue_conversation:
                conversation.append(assistant_response)
            else:
                conversation = []  # reset the conversation for next task

            return {"functionality": request.functionality, "response": assistant_response}

        except Exception as e:
            # Process the CUDA out of memory on the orchestra side.
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        processing = False


@app.post("/reset")
def reset_dialog():
    global conversation
    conversation = []
    return {"message": "Conversation reset successfully"}


@app.get("/status")
def get_status():
    global processing
    return {"status": "busy" if processing else "available"}


if __name__ == "__main__":
    reset_shutdown_timer()  # Start the shutdown timer initially
    uvicorn.run(app, host="0.0.0.0", port=6006)
