"""Abstract base class for all agents."""
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, db: Session, agent_name: str):
        self.db = db
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agents.{agent_name}")
    
    @abstractmethod
    async def execute(self, period_date):
        """Execute agent's primary task."""
        pass
    
    def log_info(self, message: str):
        """Log info level message."""
        self.logger.info(f"[{self.agent_name}] {message}")
    
    def log_error(self, message: str, exception: Exception = None):
        """Log error level message."""
        if exception:
            self.logger.error(f"[{self.agent_name}] {message}", exc_info=exception)
        else:
            self.logger.error(f"[{self.agent_name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning level message."""
        self.logger.warning(f"[{self.agent_name}] {message}")
