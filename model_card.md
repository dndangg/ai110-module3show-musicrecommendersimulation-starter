# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**MoodMatch 1.0** — A lightweight recommender that matches songs to user mood, energy, and genre preferences.

---

## 2. Intended Use  

This recommender generates song suggestions based on a user's mood, genre preference, and desired energy level. It assumes users know what mood and genre they want, and that high energy and matching genre = good recommendation.

**Intended for**: Students learning about recommendation scoring, testing edge cases, understanding how weight choices affect rankings.

**NOT intended for**: Production environments, real users seeking discovery, or systems serving communities with underrepresented genres (this dataset is heavily biased toward lofi/pop).

---

## 3. How the Model Works  

The system scores each song by matching it to the user's four preferences:

**1. Genre Match (+2 points):** If the song's genre exactly matches what the user wants → big boost. A pop-lover seeking pop gets +2 immediately; a pop-lover who gets rock gets 0.

**2. Mood Match (+1 point):** If the song's mood matches (e.g., "chill" or "happy") → smaller boost. This adds nuance but is weaker than genre/energy.

**3. Energy Fit (0–2 points):** How close the song's energy is to the user's target. If a user wants energy 0.9 and the song is 0.88, they get close to 2 points. If the song is 0.3 (very different), they get close to 0.

**4. Acoustic Preference (0–1 point):** If the user likes acoustic music, acoustic songs score higher. If they prefer electric, electric songs score higher.

All scores add up. The song with the highest total score ranks first.

**Real example**: A user seeking *Chill Lofi* would score "Library Rain" like this:
- Genre match: lofi = lofi → +2.0
- Mood match: chill = chill → +1.0
- Energy fit: user wants 0.3, song is 0.28 → +1.9
- Acoustic fit: user likes acoustic, song is 0.86 acoustic → +0.86
- **Total: 5.76** → ranked #1

This same scoring formula runs on all 10 songs, and the top 5 are shown to the user.

---

## 4. Data  

**Dataset size:** 10 songs from a hypothetical streaming catalog.

**Genres represented:**
- **Lofi** (3 songs): 30% of dataset — heavily over-represented
- **Pop** (2 songs): 20%
- **Rock, Jazz, Ambient, Synthwave, Indie Pop** (1 each): 10% each

**Moods represented:**
- **Chill** (3 songs): 30%
- **Happy** (2 songs): 20%
- **Intense** (2 songs): 20%
- **Relaxed, Moody, Focused** (1 each): 10% each

**Energy range:** Very low (0.28–0.42) to very high (0.75–0.93). There's a **critical gap** in the middle (0.5–0.7) with zero songs—users targeting mid-range energy get polarized results.

**What's missing:** Only 10 songs means zero classical, metal, country, folk, or hip-hop. Moods like "nostalgic," "angry," or "romantic" don't exist. This small dataset drives major biases in recommendations.

---

## 5. Strengths  

**Clear genre preferences work well:** If a user explicitly wants "I want lofi," the recommender quickly delivers. Lofi seekers consistently get Library Rain and Midnight Coding, which feel right for that mood.

**Energy-based discovery is fast and consistent:** Users seeking high-energy workout music get Gym Hero and Storm Runner within the top 3 across all high-energy profiles. Energy matching is mathematically clean and predictable.

**Mood adds meaningful signal:** A feature-removal experiment showed that when mood matching was disabled, rankings reshuffled. Midnight Coding dropped from #2 to #3 for Chill Lofi users, proving mood is a real differentiator, not noise.

**Transparent scoring makes debugging easy:** Each recommendation shows a breakdown ("genre match +2.0; mood match +1.0; energy close +1.8") so users understand *why* a song ranked where it did. This transparency helps catch biases and design flaws.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly.

**Lofi Genre Over-representation**: Lofi music comprises 30% (3/10) of the dataset while other genres appear only once or twice. Combined with the +2.0 genre match weight, lofi songs systematically appear in top-5 recommendations for any user seeking "chill" or "calm" moods. This creates a filter bubble where lofi lovers see familiar songs repeatedly, while other genres (jazz, ambient, rock) are starved of visibility.

**Energy Cliff Polarization**: The dataset has a gap in energy values—mid-low songs cluster at 0.40–0.42, while high-energy songs jump to 0.75–0.93. Users targeting energy near 0.5 experience a cliff where no nearby songs exist, forcing the recommender to either heavily penalize energy distance or accept large mismatches. This polarizes recommendations into two groups, reducing personalization for middle-ground users.

**Genre and Energy Dominance**: Together, genre (+2.0) and energy closeness (+2.0) account for up to 4.0 out of ~6.76 maximum points (~59%). Mood (+1.0) represents only 15%, making conflicting moods easily overridden by strong genre/energy matches. A user seeking "sad energy-0.9 pop" still gets upbeat pop songs because genre+energy outweigh mood intent.

**Small Dataset Bias**: With only 10 songs, the recommender lacks diversity. Gym Hero (pop, high-energy, non-acoustic) appears in 4 out of 6 tested profiles' top-5 lists, showing the system converges on similar recommendations rather than discovering varied options.  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected.

**Profiles Tested**: Six diverse user profiles spanning normal use cases and adversarial edges:
- *High-Energy Pop*: genre=pop, mood=happy, energy=0.9 (energy-forward user)
- *Chill Lofi*: genre=lofi, mood=chill, energy=0.3 (mood-focused user)
- *Deep Intense Rock*: genre=rock, mood=intense, energy=0.85 (rare-genre user)
- *Conflicting Sad + High Energy*: Testing if mood and energy can conflict (they can)
- *Out-of-Range Energy (-10.5)*: Testing clamping behavior (energy scores collapse to 0.0)
- *Non-Numeric Energy*: Testing error handling (raises ValueError as expected)

**Unexpected Finding**: *Gym Hero* appeared in the top-5 recommendations for 4 out of 6 profiles, despite only matching on genre/energy. This suggests the system over-prioritizes these two features at the expense of mood and acoustic diversity. For the Conflicting profile, Gym Hero ranked #2 even though neither mood (intense vs. sad) nor acoustic preference (likes_acoustic=True, but Gym Hero is 0.05 acoustic) matched.

**Feature Importance Experiment**: I disabled mood matching and re-ran the recommender. Result: Chill Lofi rankings reshuffled—Midnight Coding dropped from #2 to #3 as the +1.0 mood bonus disappeared. This proved mood matching is valuable but insufficient to compete with genre+energy (4.0 points). The mood feature adds nuance but cannot override strong genre/energy signals.

**Intuition Check**: Results felt right for clear profiles (High-Energy Pop got upbeat songs; Chill Lofi got low-energy acoustic tracks) but unintuitive for edge cases. The Conflicting Sad + High Energy profile still returned happy pop songs, showing the system prioritizes energy compatibility over mood alignment—a design choice that works for energy-first listeners but fails for mood-first listeners.

---

## 8. Future Work  

**1. Expand the dataset:** 10 songs is too small. Gym Hero appeared in 4 out of 6 test profiles' top-5 lists despite being a poor match for some (e.g., conflicting moods). With 100+ songs, the system would find better alternatives and reduce fake convergence.

**2. Rebalance feature weights:** Mood (+1.0) gets overwhelmed by genre + energy (4.0 combined, 59% of max score). Raise mood to +1.5 so users seeking "sad music" get sad songs instead of being forced to accept upbeat alternatives.

**3. Add a diversity penalty:** Prevent the same artist from appearing twice in the top-5 results. Neon Echo and Max Pulse currently dominate the rankings. A diversity penalty would force the system to "spread out" recommendations across different artists.

**4. Learn from user feedback:** If a user rates a recommendation "bad," adjust their implicit weights for that feature long-term. E.g., a user who rejects songs due to acoustic mismatch → boost acoustic weight for that user going forward.

---

## 9. Personal Reflection  

**Biggest learning:** I was shocked to discover how quickly bias hides inside "simple" math. Two feature weights (genre +2.0, energy +2.0) account for 59% of the maximum score, while mood is only 15%. The system consistently ranked the same 3–4 songs (Gym Hero, Library Rain, Sunrise City) across almost every profile. I thought I had a balanced recommender until I did the math, but then the bias was obvious.

Copilot's profile suggestions (conflicting moods, out-of-range energy values, non-numeric inputs)  exposed edge cases I would have missed. I tested "Sad mood + 0.9 energy" and discovered that energy overrides mood. That was design flaw I didn't know existed. Second, I had to fact-check an AI prediction: it claimed removing mood would have minimal impact, but my experiment showed Midnight Coding dropped from #2 to #3 when mood was disabled. The data contradicted the prediction, which made me trust experiments and testing over intuition.

**What surprised me:** Even though this recommender uses only four numbers and basic math, the results felt intelligent and reasonable. Top songs seemed like good matches. This made me realize that simple algorithms don't need complexity to feel smart, but they do need fairness. It over-recommends lofi and pop because the dataset is biased.

**If I extended this:** I'd implement learning from what similar users liked. I'd also triple the dataset
