from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.models import BusinessRecord, IngestedDocument


class DocumentExtractor(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool: ...

    @abstractmethod
    def extract(self, file_path: Path, document: IngestedDocument) -> list[BusinessRecord]: ...
