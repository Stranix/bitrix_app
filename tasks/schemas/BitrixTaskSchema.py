import datetime
from enum import IntEnum

from pydantic import BaseModel, Field
from typing import Optional, Union


class TaskStage(IntEnum):
    NEW = 2943
    PLANING = 2949
    ASSIGNED = 2947
    IN_PROGRESS = 2939
    SUSPENDED = 2953
    AWAITING = 2951
    NEED_CONTROL = 2955
    COMPLETE = 2941
    PERSONAL = 0


class TaskStatus(IntEnum):
    PERSONAL = 0
    NEW = 1
    CREATED = 2
    AWAITING = 2
    IN_PROGRESS = 3
    SUSPENDED = 6
    COMPLETE = 5


class BitrixTask(BaseModel):
    id: int = Field(alias='ID')
    subject: str = Field(alias='TITLE')
    description: str = Field(alias='DESCRIPTION')
    stage: TaskStage = Field(alias='STAGE_ID')
    status: TaskStatus = Field(alias='REAL_STATUS')

    created_id: int = Field(alias='CREATED_BY')
    responsible_id: int = Field(alias='RESPONSIBLE_ID')
    accomplices: Optional[list[int]] = Field(alias='ACCOMPLICES')

    watchers: Optional[list[int]] = Field(alias='AUDITORS')

    parent_id: Optional[int] = Field(alias='PARENT_ID')
    group_id: Optional[int] = Field(alias='GROUP_ID')

    duration_fact_time: Optional[int] = Field(alias='DURATION_FACT')
    created_date: datetime.datetime = Field(alias='CREATED_DATE')
    closed_by_id: Optional[int] = Field(alias='CLOSED_BY')
    closed_date_time: Union[datetime.datetime, str] = Field(
        alias='CLOSED_DATE'
    )
    last_activity_date: datetime.datetime = Field(alias='ACTIVITY_DATE')
