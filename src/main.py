"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profile_set = {
        "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
        "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
        "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.85, "likes_acoustic": False},
        "Edge: Conflicting Sad + High Energy": {
            "genre": "pop",
            "mood": "sad",
            "energy": 0.9,
            "likes_acoustic": True,
        },
        "Edge: Out-of-Range Energy": {
            "genre": "pop",
            "mood": "happy",
            "energy": -10.5,
            "likes_acoustic": False,
        },
        "Edge: Non-Numeric Energy (expected error)": {
            "genre": "pop",
            "mood": "happy",
            "energy": "high",
            "likes_acoustic": False,
        },
    }

    for profile_name, user_prefs in profile_set.items():
        print(f"\n=== {profile_name} ===")
        print(f"Preferences: {user_prefs}")

        try:
            recommendations = recommend_songs(user_prefs, songs, k=5)
        except (TypeError, ValueError) as exc:
            print(f"Recommendation failed: {exc}")
            continue

        print("Top recommendations:\n")
        for index, rec in enumerate(recommendations, start=1):
            song, score, explanation = rec
            print(f"{index}. {song['title']} by {song['artist']}")
            print(f"   Score: {score:.2f}")
            print(f"   Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
