from abc import ABC, abstractmethod
from typing import Any

class LLMProviderPort(ABC):
  @abstractmethod
  def get_llm(
    model_id: str
  ) -> Any:
    pass

  @abstractmethod
  def validate_credentials():
    pass

  @abstractmethod
  def cleanup():
    pass