"""
Scraper base - clase abstracta para todos los scrapers de empleo
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class JobOffer:
    title: str
    company: str
    location: str
    url: str
    source: str
    description: str = ""
    salary: str = ""
    date_posted: str = ""
    job_id: str = ""

    def __post_init__(self):
        if not self.job_id:
            # Generar ID unico basado en titulo + empresa + fuente
            self.job_id = f"{self.source}_{hash(self.title + self.company)}"

    def to_telegram_message(self) -> str:
        msg = f"*{self.title}*\n"
        msg += f"Empresa: {self.company}\n"
        msg += f"Ubicacion: {self.location}\n"
        if self.salary:
            msg += f"Salario: {self.salary}\n"
        if self.date_posted:
            msg += f"Publicado: {self.date_posted}\n"
        msg += f"Fuente: {self.source}\n"
        msg += f"[Ver oferta]({self.url})"
        return msg


class BaseScraper(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def search(self, keywords: str, location: str = "", remote_only: bool = False) -> List[JobOffer]:
        pass
