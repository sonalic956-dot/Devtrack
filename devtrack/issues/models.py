from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = int(id)
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name or not str(self.name).strip():
            raise ValueError("Name cannot be empty")
        if "@" not in str(self.email):
            raise ValueError("Invalid email")


class Issue(BaseEntity):
    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = int(id)
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = int(reporter_id) if reporter_id is not None else None
        self.created_at = created_at or str(datetime.now())

    def validate(self):
        if not self.title or not str(self.title).strip():
            raise ValueError("Title cannot be empty")
        
        allowed_statuses = ["open", "in_progress", "resolved", "closed"]
        if self.status not in allowed_statuses:
            raise ValueError(f"Invalid status. Must be one of {allowed_statuses}")

        allowed_priorities = ["low", "medium", "high", "critical"]
        if self.priority not in allowed_priorities:
            raise ValueError(f"Invalid priority. Must be one of {allowed_priorities}")

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    def __init__(self, id, title, description, reporter_id, status="open", created_at=None):
        super().__init__(id, title, description, status, priority="critical", reporter_id=reporter_id, created_at=created_at)

    def describe(self):
        return f"[URGENT] {self.title} - needs immediate attention"


class LowPriorityIssue(Issue):
    def __init__(self, id, title, description, reporter_id, status="open", created_at=None):
        super().__init__(id, title, description, status, priority="low", reporter_id=reporter_id, created_at=created_at)

    def describe(self):
        return f"{self.title} - low priority, handle when free"
