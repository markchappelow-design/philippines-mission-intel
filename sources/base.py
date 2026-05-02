from __future__ import annotations

from abc import ABC, abstractmethod

from sources.source_models import SourcePayload


class SourceAdapterError(Exception):
    pass


class SourceFetchError(SourceAdapterError):
    pass


class SourceParseError(SourceAdapterError):
    pass


class BaseSourceAdapter(ABC):
    @abstractmethod
    def fetch(self) -> SourcePayload:
        raise NotImplementedError