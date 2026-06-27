from database.sqlite_manager import SQLiteManager


def main():
    db = SQLiteManager()

    jobs = db.get_all_jobs()
    new_jobs = db.get_new_jobs()

    print(f"Total jobs: {len(jobs)}")
    print(f"New jobs: {len(new_jobs)}")

    assert jobs is not None
    assert new_jobs is not None


if __name__ == "__main__":
    main()