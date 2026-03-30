import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_CLOSENESS_POINTS = 2.0
ACOUSTIC_PREFERENCE_POINTS = 1.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamps a float to an inclusive [minimum, maximum] range."""
    return max(minimum, min(maximum, value))


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song and returns both a numeric score and human-readable reasons."""
    score = 0.0
    reasons: List[str] = []

    user_genre = str(user_prefs.get("genre", "")).strip().lower()
    song_genre = str(song.get("genre", "")).strip().lower()
    if user_genre and song_genre == user_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS:.1f})")

    user_mood = str(user_prefs.get("mood", "")).strip().lower()
    song_mood = str(song.get("mood", "")).strip().lower()
    if user_mood and song_mood == user_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS:.1f})")

    target_energy = float(user_prefs.get("energy", 0.5))
    song_energy = float(song.get("energy", 0.0))
    energy_similarity = _clamp(1.0 - abs(song_energy - target_energy), 0.0, 1.0)
    energy_points = ENERGY_CLOSENESS_POINTS * energy_similarity
    score += energy_points
    reasons.append(f"energy close (+{energy_points:.2f})")

    if "likes_acoustic" in user_prefs:
        likes_acoustic = bool(user_prefs.get("likes_acoustic"))
        acousticness = float(song.get("acousticness", 0.0))
        acoustic_fit = acousticness if likes_acoustic else (1.0 - acousticness)
        acoustic_points = ACOUSTIC_PREFERENCE_POINTS * _clamp(acoustic_fit, 0.0, 1.0)
        score += acoustic_points
        reasons.append(f"acoustic fit (+{acoustic_points:.2f})")

    return score, reasons

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Ranks songs for one user and returns the top-k Song objects."""
        scored = []
        for song in self.songs:
            user_prefs = {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
            }
            song_dict = {
                "id": song.id,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "acousticness": song.acousticness,
            }
            total_score, _ = score_song(user_prefs, song_dict)
            energy_distance = abs(song.energy - user.target_energy)
            scored.append((song, total_score, energy_distance))

        ranked = sorted(scored, key=lambda item: (-item[1], item[2], item[0].id))
        return [item[0] for item in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Builds a short explanation string for why a song was recommended."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dict = {
            "id": song.id,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from CSV and converts numeric fields to int/float for scoring."""
    songs: List[Dict] = []
    with open(csv_path, mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, ranks by score, and returns top-k recommendations."""
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))

    target_energy = float(user_prefs.get("energy", 0.5))
    ranked = sorted(
        scored,
        key=lambda item: (
            -item[1],
            abs(float(item[0].get("energy", 0.0)) - target_energy),
            int(item[0].get("id", 0)),
        ),
    )
    return ranked[:k]
