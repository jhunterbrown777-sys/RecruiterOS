from typing import List

from models.job import Job
from services.base_provider import BaseJobProvider


class ManualProvider(BaseJobProvider):
    provider_name = "Manual Test Provider"

    def search_jobs(self, query: str, location: str = "Remote") -> List[Job]:
        return [
            Job(
                title="IT Support Specialist",
                company="DemoTech Solutions",
                location=location,
                description="""
We are hiring an IT Support Specialist to provide Tier 1 support for Windows laptops,
Microsoft 365, VPN connectivity, printers, hardware troubleshooting, onboarding,
offboarding, and basic networking issues.

Requirements include strong customer service, Windows troubleshooting, DNS, DHCP,
TCP/IP, VPN concepts, documentation, and basic Active Directory knowledge.
""",
                url="https://example.com/jobs/it-support-specialist",
                source=self.provider_name,
                work_arrangement="Remote",
                employment_type="Full-time",
                salary="$60,000 - $75,000",
                remote=True,
            ),
            Job(
                title="SEO Specialist",
                company="GrowthStack Media",
                location=location,
                description="""
We are seeking an SEO Specialist to manage website optimization, Google Analytics,
keyword research, content recommendations, technical SEO audits, and reporting.

Experience with Google Ads, Google Analytics, SEO, website management, and client
communication is preferred.
""",
                url="https://example.com/jobs/seo-specialist",
                source=self.provider_name,
                work_arrangement="Remote",
                employment_type="Full-time",
                salary="$55,000 - $70,000",
                remote=True,
            ),
        ]