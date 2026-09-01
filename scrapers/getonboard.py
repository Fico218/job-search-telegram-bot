"""
Scraper para GetOnBoard (Latinoamerica - tech jobs)
Usa la API publica de GetOnBoard
"""
import requests
from typing import List
from .base import BaseScraper, JobOffer
import time


class GetOnBoardScraper(BaseScraper):
    def __init__(self):
        super().__init__("GetOnBoard")
        self.api_url = "https://www.getonbrd.com/api/v0/search/jobs"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "JobBot/1.0",
        }

    def search(self, keywords: str, location: str = "", remote_only: bool = False) -> List[JobOffer]:
        jobs = []
        params = {
            "query": keywords,
            "per_page": 10,
        }
        if remote_only:
            params["remote"] = "true"

        try:
            time.sleep(1)
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            offers = data.get("data", [])
            for offer in offers[:10]:
                try:
                    attrs = offer.get("attributes", {})
                    company = attrs.get("company", {})
                    company_name = company.get("name", "N/A") if isinstance(company, dict) else "N/A"
                    locations = attrs.get("locations", [])
                    loc_str = ", ".join(locations) if locations else ("Remote" if attrs.get("remote") else location)

                    job = JobOffer(
                        title=attrs.get("title", "Sin titulo"),
                        company=company_name,
                        location=loc_str,
                        url=f"https://www.getonbrd.com/jobs/{offer.get('id', '')}",
                        source=self.name,
                        salary=attrs.get("salary", ""),
                        description=attrs.get("description", "")[:200],
                        job_id=f"getonboard_{offer.get('id', '')}",
                    )
                    jobs.append(job)
                except Exception:
                    continue
        except Exception as e:
            print(f"[GetOnBoard] Error en busqueda: {e}")

        return jobs
