from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import SessionDB
from app.models import Task
from app.schema import TaskBase, TaskPublic

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/')
async def get_all_tasks(session: SessionDB) -> list[TaskPublic]:
    stmt = select(Task)
    tasks = session.scalars(stmt).all()
    return tasks


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_task(session: SessionDB, task: TaskBase) -> TaskPublic:
    try:
        t = Task(**task.model_dump())
        session.add(t)
        session.commit()
        return t
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get('/{id}')
async def get_one_task(session: SessionDB, id: int) -> TaskPublic:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put('/{id}')
async def update_task(session: SessionDB, id: int, task_in: TaskBase) -> TaskPublic:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_in.model_dump().items():
        setattr(task, key, value)
    
    session.commit()
    return task


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(session: SessionDB, id: int) -> None:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit() 
    return