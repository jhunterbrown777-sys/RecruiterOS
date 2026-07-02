from database.sqlite_manager import SQLiteManager
from models.assessment import Assessment
from models.candidate import Candidate
from models.document import Document
from models.opportunity import Opportunity
from models.resume import Resume
from services.assessment_service import AssessmentService
from services.candidate_service import CandidateService
from services.discovery_service import DiscoveryService
from services.document_service import DocumentService
from services.opportunity_service import OpportunityService
from services.resume_service import ResumeService


class AppController:
    def __init__(self):
        self.db = SQLiteManager()
        self.discovery_service = DiscoveryService()
        self.candidate_service = CandidateService()
        self.opportunity_service = OpportunityService()
        self.assessment_service = AssessmentService()
        self.resume_service = ResumeService()
        self.document_service = DocumentService()

    def get_dashboard_stats(self):
        jobs = self.db.get_all_jobs()

        total_jobs = len(jobs)
        new_jobs = len([job for job in jobs if job.status == "NEW"]) if jobs else 0
        applied_jobs = len([job for job in jobs if job.applied]) if jobs else 0

        return {
            "jobs_discovered": total_jobs,
            "qualified_opportunities": new_jobs,
            "applications_sent": applied_jobs,
            "interviews": 0,
            "offers": 0,
            "ready_queue": new_jobs,
            "average_ats": 92,
        }

    def get_recent_jobs(self, limit=8):
        jobs = self.db.get_all_jobs()
        return jobs[:limit]

    def get_top_opportunities(self, limit=5):
        jobs = self.db.get_all_jobs()
        return jobs[:limit]

    def get_activity_feed(self):
        return [
            "Google Jobs provider checked",
            "Greenhouse provider checked",
            "Lever provider checked",
            "Discovery pipeline completed",
            "Waiting for application review",
        ]

    def get_mission_items(self):
        return [
            ("Discover Jobs", True),
            ("Score Opportunities", True),
            ("Company Research", False),
            ("Resume Optimization", False),
            ("Browser Automation", False),
        ]

    def get_candidate(self) -> Candidate:
        return self.candidate_service.get_default_candidate()

    def update_candidate(self, name: str, candidate_profile: str) -> None:
        candidate = self.get_candidate()
        candidate.name = name
        candidate.candidate_profile = candidate_profile
        self.candidate_service.update_candidate(candidate)

    def get_opportunities(self):
        candidate = self.get_candidate()
        return self.opportunity_service.list_opportunities_with_jobs(candidate.id)

    def create_opportunity_for_job(self, job_id: int) -> bool:
        candidate = self.get_candidate()
        opportunity = Opportunity(candidate_id=candidate.id, job_id=job_id)
        return self.opportunity_service.create_opportunity(opportunity) is not None

    def update_opportunity_status(self, opportunity_id: int, new_status: str) -> Opportunity:
        opportunity = self.opportunity_service.get_opportunity(opportunity_id)
        opportunity.status = new_status
        self.opportunity_service.update_opportunity(opportunity)
        return opportunity

    def analyze_opportunity(self, opportunity_id: int) -> Assessment:
        opportunity = self.opportunity_service.get_opportunity(opportunity_id)
        job = self.db.get_job(opportunity.job_id)

        if job is None:
            raise RuntimeError("Cannot analyze: Job details unavailable for this Opportunity.")

        return self.assessment_service.generate_assessment(opportunity, job)

    def get_latest_assessment(self, opportunity_id: int) -> Assessment | None:
        assessments = self.assessment_service.list_assessments(opportunity_id)
        return assessments[0] if assessments else None

    def get_resumes(self):
        candidate = self.get_candidate()
        return self.resume_service.list_resumes(candidate.id)

    def get_resume(self, resume_id: int) -> Resume | None:
        return self.resume_service.get_resume(resume_id)

    def create_resume(self, title: str, content: str) -> Resume:
        candidate = self.get_candidate()
        resume = Resume(candidate_id=candidate.id, title=title, content=content)
        resume.id = self.resume_service.create_resume(resume)
        return resume

    def update_resume_content(self, resume_id: int, content: str) -> Resume:
        resume = self.resume_service.get_resume(resume_id)
        resume.content = content
        self.resume_service.update_resume(resume)
        return resume

    def generate_resume_for_opportunity(self, opportunity_id: int) -> Resume:
        opportunity = self.opportunity_service.get_opportunity(opportunity_id)
        job = self.db.get_job(opportunity.job_id)

        if job is None:
            raise RuntimeError("Cannot generate resume: Job details unavailable for this Opportunity.")

        assessment = self.get_latest_assessment(opportunity_id)

        return self.resume_service.generate_tailored_resume(job, assessment)

    def duplicate_resume(self, resume_id: int) -> Resume:
        original = self.resume_service.get_resume(resume_id)
        new_resume = Resume(
            candidate_id=original.candidate_id,
            title=original.title,
            content=original.content,
            version=original.version + 1,
        )
        new_resume.id = self.resume_service.create_resume(new_resume)
        return new_resume

    def get_documents(self):
        candidate = self.get_candidate()
        return self.document_service.list_documents(candidate.id)

    def get_document(self, document_id: int) -> Document | None:
        return self.document_service.get_document(document_id)

    def create_document(self, title: str, document_type: str, content: str) -> Document:
        candidate = self.get_candidate()
        document = Document(candidate_id=candidate.id, title=title, document_type=document_type, content=content)
        document.id = self.document_service.create_document(document)
        return document

    def update_document_content(self, document_id: int, title: str, document_type: str, content: str) -> Document:
        document = self.document_service.get_document(document_id)
        document.title = title
        document.document_type = document_type
        document.content = content
        self.document_service.update_document(document)
        return document

    def delete_document(self, document_id: int) -> None:
        self.document_service.delete_document(document_id)

    def duplicate_document(self, document_id: int) -> Document:
        original = self.document_service.get_document(document_id)
        new_document = Document(
            candidate_id=original.candidate_id,
            title=original.title,
            document_type=original.document_type,
            content=original.content,
            version=original.version + 1,
        )
        new_document.id = self.document_service.create_document(new_document)
        return new_document

    def run_discovery(self):
        run = self.discovery_service.run_discovery()

        if run.errors:
            raise RuntimeError("; ".join(run.errors))

        return self.get_dashboard_stats()