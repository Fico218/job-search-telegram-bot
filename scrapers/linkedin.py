"""
Scraper para LinkedIn Jobs
Usa la API publica de busqueda de LinkedIn (no requiere login para resultados basicos)
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseScraper, JobOffer
import time
import random


class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn")
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def search(self, keywords: str, location: str = "", remote_only: bool = False) -> List[JobOffer]:
        jobs = []
        params = {
            "keywords": keywords,
            "location": location,
            "f_TPR": "r3600",  # Ultimas 24 horas
            "start": 0,
        }
        if remote_only:
            params["f_WT"] = "2"  # Filtro remoto

        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_cards = soup.find_all("div", class_="base-card")
            for card in job_cards[:10]:
                try:
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el = card.find("span", class_="job-search-card__location")
                    link_el = card.find("a", class_="base-card__full-link")
                    date_el = card.find("time")

                    if not title_el or not link_el:
                        continue

                    job = JobOffer(
                        title=title_el.get_text(strip=True),
                        company=company_el.get_text(strip=True) if company_el else "N/A",
                        location=location_el.get_text(strip=True) if location_el else location,
                        url=link_el["href"].split("?")[0],
                        source=self.name,
                        date_posted=date_el.get("datetime", "") if date_el else "",
                    )
                    jobs.append(job)
                except Exception:
                    continue
        except Exception as e:
            print(f"[LinkedIn] Error en busqueda: {e}")

        return jobs
