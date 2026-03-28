from datetime import datetime
import os
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, get_datetime_utc
from app.database import SessionDefault
from app.schema import TaskBase, TaskPublic, TaskUpdate


if os.getenv("OPENAI_API_KEY"):
    model = 'openai:gpt-5.2'
elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
    # model = 'google-gla:gemini-2.5-flash-lite'
    model = 'google-gla:gemini-3.1-flash-lite-preview'
else:
    raise Exception("Environment variable for models not found")


@dataclass
class MyDeps:
    session: Session


agent = Agent(
    model=model,
    deps_type=MyDeps,
    instructions="Eres un asistente que ayuda con la creacion y listado de tareas.",
)

@agent.tool
async def list_task(ctx: RunContext[MyDeps]):
    """Utiliza esta herramienta para obtener todas las tareas, y luego retornalas.
    
    Solo devuelve el id y titulo de la tarea.
    """
    result = ctx.deps.session.scalars(select(Task)).all()
    tasks = [ f"id: {t.id} - title: {t.title}" for t in result]
    response = "\n".join(tasks)
    return response


@agent.tool
async def list_task_all_info(ctx: RunContext[MyDeps]) -> list[TaskPublic]:
    """Utiliza esta herramienta para obtener todas las tareas con toda la informacion."""
    result = ctx.deps.session.scalars(select(Task)).all()
    tasks = []
    for t in result:
        tasks.append(TaskPublic.model_validate(t, from_attributes=True))
    return tasks


@agent.tool
async def create_task(ctx: RunContext[MyDeps], task: TaskBase):
    """Utiliza esta herramienta para crear tareas que solicite el usuario.
    
    Si retorno la tarea, significa que la Tarea  fue creada exitosamente.
    """
    print(task)
    try:
        t = Task(**task.model_dump())
        ctx.deps.session.add(t)
        ctx.deps.session.commit()
        print(t.id)
    except Exception as e:
        print(e)
        return "ERROR: Something went wrong while creating the task."
    
    return ("Tarea creada exitosamente.\n Datos de la tarea\n"
            f"id:{t.id} - title: {t.title}"
    )

@agent.tool
async def get_one_task(ctx: RunContext[MyDeps], id: int):
    """Utiliza esta herramienta para obtener una tarea por un id en especifico"""
    try:
        t = ctx.deps.session.get(Task, id)
        if not t:
            return "Task not found."
        
        task = TaskPublic.model_validate(t, from_attributes=True)
    except Exception as e:
        print(e)
        return "ERROR: Something went wrong"
    return task

@agent.tool
async def update_task(ctx: RunContext[MyDeps], id: int, task_in: TaskUpdate):
    """Utiliza esta herramienta para actualizar las tareas del usuario."""
    task = ctx.deps.session.get(Task, id)
    if not task:
        return "Task not found"
    
    task_dict = task_in.model_dump(exclude_unset=True)
    for key, value in task_dict.items():
        setattr(task, key, value)

    ctx.deps.session.commit()
    
    task_updated = TaskPublic.model_validate(task, from_attributes=True)
    return task_updated

@agent.tool
async def delete_task(ctx: RunContext[MyDeps], id: int):
    """Utiliza esta herramienta para eliminar tareas del usuario."""
    task = ctx.deps.session.get(Task, id)
    if not task:
        return "Task not found"
    try: 
        ctx.deps.session.delete(task)
        ctx.deps.session.commit()
    except Exception as e:
        return "ERROR: Something went wrong while delete task"
    
    return "Tarea eliminada exitosamente."

@agent.tool_plain
async def get_date_current() -> datetime:
    """Utiliza esta herramienta para obtener la fecha actual.
    
    Puedes utilizar esta herramienta, cuando el usuario solicite algo relacionado con fechas relativas al dia actual.
    
    La fecha retornada es la UTC.
    """
    return get_datetime_utc()
    

with SessionDefault() as session:
    deps = MyDeps(session=session)    
    app = agent.to_web(deps=deps)
