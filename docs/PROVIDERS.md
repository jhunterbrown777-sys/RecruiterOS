# RecruiterOS Providers

Providers discover jobs and normalize them into the canonical Job model.

## Provider Interface

Every provider must implement:

```python
search_jobs(query: str, location: str = "Remote") -> list[Job]