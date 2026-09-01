"""
Scraper para Indeed
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseScraper, JobOffer
import time
import random


class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")
        self.base_url = "https://www.indeed.com/jobs"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        }

    def search(self, keywords: str, location: str = "", remote_only: bool = False) -> List[JobOffer]:
        jobs = []
        params = {
            "q": keywords,
            "l": "Remote" if remote_only else location,
            "fromage": "1",  # Ultimo dia
            "sort": "date",
        }

        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_cards = soup.find_all("div", class_="job_seen_beacon")
            for card in job_cards[:10]:
                try:
                    title_el = card.find("h2", class_="jobTitle")
                    company_el = card.find("span", {"data-testid": "company-name"})
                    location_el = card.find("div", {"data-testid": "text-location"})
                    salary_el = card.find("div", {"data-testid": "attribute_snippet_testid"})
                    link_el = card.find("a", class_="jcs-JobTitle")

                    if not title_el or not link_el:
                        continue

                    href = link_el.get("href", "")
                    full_url = f"https://www.indeed.com{href}" if href.startswith("/") else href

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
            print(f"[Indeed] Error en busqueda: {e}")

        return jobs
