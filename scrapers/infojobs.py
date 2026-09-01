"""
Scraper para InfoJobs (Espana/Latinoamerica)
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from .base import BaseScraper, JobOffer
import time
import random


class InfoJobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("InfoJobs")
        self.base_url = "https://www.infojobs.net/jobsearch/search-results/list.xhtml"
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
            "keyword": keywords,
            "provinceIds": "",
            "sortBy": "PUBLICATION_DATE",
            "sinceDate": "ONE_DAY",
        }
        if remote_only:
            params["teleworkingIds"] = "1"

        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_cards = soup.find_all("li", class_="ij-OfferList-item")
            for card in job_cards[:10]:
                try:
                    title_el = card.find("a", class_="ij-OfferList-itemTitle")
                    company_el = card.find("span", class_="ij-OfferList-itemCompany")
                    location_el = card.find("span", class_="ij-OfferList-itemLocation")
                    salary_el = card.find("span", class_="ij-OfferList-itemSalary")

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    full_url = f"https://www.infojobs.net{href}" if href.startswith("/") else href

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
            print(f"[InfoJobs] Error en busqueda: {e}")

        return jobs
