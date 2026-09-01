"""
Scraper para Computrabajo (Latinoamerica)
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseScraper, JobOffer
import time
import random


class ComputrabajoScraper(BaseScraper):
    def __init__(self, country_domain: str = "mx"):
        super().__init__("Computrabajo")
        # Dominio segun pais: mx, co, ar, pe, cl, ve, etc.
        self.base_url = f"https://{country_domain}.computrabajo.com/trabajo-de"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def search(self, keywords: str, location: str = "", remote_only: bool = False) -> List[JobOffer]:
        jobs = []
        # Computrabajo usa URLs con guiones para keywords
        keyword_slug = keywords.replace(" ", "-").lower()
        url = f"{self.base_url}-{keyword_slug}"

        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_cards = soup.find_all("article", class_="box_offer")
            for card in job_cards[:10]:
                try:
                    title_el = card.find("h2")
                    link_el = card.find("a", class_="js-o-link")
                    company_el = card.find("p", class_="fs16 fc_base")
                    location_el = card.find("p", class_="fs13 fc_aux")
                    salary_el = card.find("b", class_="semibold")

                    if not title_el:
                        continue

                    href = link_el.get("href", "") if link_el else ""
                    full_url = f"https://mx.computrabajo.com{href}" if href.startswith("/") else href

                    job = JobOffer(
                        title=title_el.get_text(strip=True),
                        company=company_el.get_text(strip=True) if company_el else "N/A",
                        location=location_el.get_text(strip=True) if location_el else location,
                        url=full_url,
                        source=self.name,
                        salary=salary_el.get_text(strip=True) if salary_el else "",
                    )
                    jobs.append(job)
                except Exception:
                    continue
        except Exception as e:
            print(f"[Computrabajo] Error en busqueda: {e}")

        return jobs
