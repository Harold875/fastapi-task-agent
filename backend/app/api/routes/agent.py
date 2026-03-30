from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.task_agent import MyDeps, agent
from app.api.deps import SessionDB


router = APIRouter(tags=["agents"])


class InputAgent(BaseModel):
    prompt: str
    delete_chat_history: bool = False 

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "lista las tareas.",
                    "delete_chat_history": False
                },
                {
                    "prompt": "lista las tareas."
                },
                {
                    "prompt": "What is the capital of France?",
                    "delete_chat_history": True
                },
            ]
        }
    }


class OutputAgent(BaseModel):
    message: str



chat_history = None


@router.post("/chat")
async def chat_task_agent(
    input: InputAgent,
    session: SessionDB
) -> OutputAgent:
    global chat_history
    deps = MyDeps(session=session)
    
    prompt = input.prompt
    result = await agent.run(
        prompt, 
        message_history=chat_history,
        deps=deps
    )
    
    # save chat history in memory
    chat_history = result.all_messages()
    
    if input.delete_chat_history:
        # delete chat history
        chat_history = None
    
    return {"message": result.output}
