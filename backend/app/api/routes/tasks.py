from datetime import date, timedelta, timezone
from typing import Annotated
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import SessionDB
from app.models import Task, TaskStatus, TaskPriority, get_datetime_utc
from app.schema import TaskBase, TaskPublic, TaskUpdate, TaskSummary
from app.agent.task_agent import MyDeps, agent

router = APIRouter(prefix='/tasks', tags=['tasks'])

date_format = Annotated[date, Query(example="2026-03-27")]

@router.get('/')
async def get_all_tasks(
    session: SessionDB,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    created_at_from: date_format | None = None,
    created_at_to: date_format | None = None,
    due_date_from: date_format | None = None,
    due_date_to: date_format | None = None,
    limit: int = 100
) -> list[TaskPublic]:
    
    stmt = select(Task).limit(limit)
    if status:
        stmt = stmt.where(Task.status == status.name)
    if priority:
        stmt = stmt.where(Task.priority == priority.name)
    
    
    # filter date
    if created_at_from:
        stmt = stmt.where(Task.created_at >= created_at_from)

    if created_at_to:
        stmt = stmt.where(Task.created_at <= created_at_to)
    
    if due_date_from:
        stmt = stmt.where(Task.due_date >= due_date_from)
    
    if due_date_to:
        stmt = stmt.where(Task.due_date <= due_date_to)


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


@router.patch('/{id}')
async def update_task_patch(session: SessionDB, id: int, task_in: TaskUpdate) -> TaskPublic:
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_dict = task_in.model_dump(exclude_unset=True)
    for key, value in task_dict.items():
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


@router.get("/summary/")
async def summary_day(
    session: SessionDB,
) -> TaskSummary:
    stmt = select(Task)
    tasks = session.scalars(stmt).all()

    current_date = get_datetime_utc()
    upcommit_due_date = current_date + timedelta(days=3)
    
    total_tasks = len(tasks)
    dist_by_status = defaultdict(int)
    dist_by_priority = defaultdict(int)
    
    tasks_overdue = 0
    tasks_due_soon = 0
    for task in tasks:
        # distribution by status and priority
        dist_by_status[task.status] += 1
        dist_by_priority[task.priority] += 1
        
        t_due_date = task.due_date.replace(tzinfo=timezone.utc)
        
        # overdue and upcoming tasks
        if t_due_date < current_date:
            tasks_overdue += 1
        elif t_due_date < upcommit_due_date:
            tasks_due_soon += 1
    
    
    response = {
        "total_tasks": total_tasks,
        "distribution_by_status": dist_by_status,
        "distribution_by_priority": dist_by_priority,
        "tasks_overdue": tasks_overdue,
        "tasks_due_soon": tasks_due_soon,
    }
    
    # AI
    deps = MyDeps(session=session)
    try:
        result = await agent.run(
            (
                "Dame una sugerencia de cual tarea deberia hacer"
                "enfocada en la prioridad para este dia.\n\n"
                "Aqui tienes la estadista sobre las tareas:\n"
                f"{response}"
            ),
            deps=deps,
        )
        message_ai = result.output
    except Exception:
        message_ai = "ERROR: Something went wrong with the AI agent."
    
    response["message"] = message_ai
    
    return response
