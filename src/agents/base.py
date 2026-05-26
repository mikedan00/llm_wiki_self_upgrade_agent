from src.core.config import Settings
from src.core.hf_client import HFRouterClient
from src.core.storage import Storage
from src.core.schemas import AgentResult

class BaseAgent:
    name = "BaseAgent"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.storage = Storage(settings)
        self.llm = HFRouterClient(settings)

    def run(self, *args, **kwargs) -> AgentResult:
        raise NotImplementedError
