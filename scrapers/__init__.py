"""
Modulo __init__ de scrapers - exporta todos los scrapers disponibles
"""
from .linkedin import LinkedInScraper
from .indeed import IndeedScraper
from .infojobs import InfoJobsScraper
from .computrabajo import ComputrabajoScraper
from .getonboard import GetOnBoardScraper
from .base import JobOffer, BaseScraper

__all__ = [
    "LinkedInScraper",
    "IndeedScraper",
    "InfoJobsScraper",
    "ComputrabajoScraper",
    "GetOnBoardScraper",
    "JobOffer",
    "BaseScraper",
]
