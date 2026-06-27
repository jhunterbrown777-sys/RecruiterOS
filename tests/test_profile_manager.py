from profiles.profile_manager import ProfileManager


def main():
    manager = ProfileManager()
    profiles = manager.available_profiles()

    print(f"Available profiles: {profiles}")

    assert "hunter" in profiles

    profile = manager.load("hunter")

    print(f"Loaded profile: {profile.name}")
    print(f"Profile directory: {profile.profile_dir}")

    assert profile.name == "hunter"
    assert profile.candidate_profile
    assert profile.master_resume
    assert profile.preferences
    assert profile.technical_skills


if __name__ == "__main__":
    main()