from database.sqlite_manager import SQLiteManager
from models.document import Document


class DocumentService:
    """Service-layer interface for Document data.

    Wraps SQLiteManager's document persistence methods so callers depend
    on the service layer instead of the persistence layer directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_document(self, document: Document) -> int:
        """Persist a new Document and return its id."""
        return self.db.save_document(document)

    def get_document(self, document_id: int) -> Document | None:
        """Fetch a Document by id, or None if not found."""
        return self.db.get_document(document_id)

    def list_documents(self, candidate_id: int) -> list[Document]:
        """List all Documents belonging to a Candidate, most recently updated first."""
        return self.db.get_documents(candidate_id)

    def update_document(self, document: Document) -> None:
        """Persist changes to an existing Document."""
        self.db.update_document(document)

    def delete_document(self, document_id: int) -> None:
        """Permanently remove a Document."""
        self.db.delete_document(document_id)
