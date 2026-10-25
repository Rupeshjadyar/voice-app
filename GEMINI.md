# 🔒 CRITICAL SYSTEM RULE: VOICE ARCHITECTURE & PRESERVATION (INVIOLABLE)

> **ATTENTION ALL AI ASSISTANTS & DEVELOPERS:**
> This rule is PERMANENT and NON-NEGOTIABLE. Under NO circumstances should any AI or developer alter, degrade, overwrite, or revert the Core Top 10 Voice Architecture established in this codebase.

---

## 📌 Rule 1: Zero Robotic Distortion on Top 10 Voices (5 Female, 5 Male)
- In `VOICE_TYPE_MODIFIERS` (`app.py`), the top 10 core voices (`female-1` to `female-5` and `male-1` to `male-5`) MUST ALWAYS maintain:
  ```python
  'rate_mult': 1.00,  # Exactly 1.00x - NO artificial speed changes
  'pitch_add': 0,     # Exactly 0Hz - NO artificial pitch shifting
  ```
- **Reason:** These 10 voices are the flagship natural voices of the platform. Any artificial pitch/rate shift introduces robotic/metallic distortion ("chipmunk effect") which destroys user retention.

---

## 📌 Rule 2: Zero Voice Collision (All 104 Languages MUST Have 5 Unique Females & 5 Unique Males)
- In EVERY single language supported by the platform (all 104 languages in `COMPLETE_VOICE_CATALOG`):
  - `female-1`, `female-2`, `female-3`, `female-4`, `female-5` MUST ALWAYS resolve to **5 completely different, unique neural voice models**.
  - `male-1`, `male-2`, `male-3`, `male-4`, `male-5` MUST ALWAYS resolve to **5 completely different, unique neural voice models**.
- **NEVER** map multiple female slots or male slots to the same underlying voice model for the same language (e.g. Swara mapped to female-1, 2, 3, 4 is STRICTLY FORBIDDEN).

---

## 📌 Rule 3: Native-First & Flagship Multilingual Architecture
- For languages with native neural models (e.g. `hi-IN-SwaraNeural`, `hi-IN-MadhurNeural`, `mr-IN-AarohiNeural`, `mr-IN-ManoharNeural`):
  - Native models MUST be assigned to slots 1 and 2.
  - The remaining slots (3, 4, 5) MUST be filled with distinct flagship Multilingual neural models:
    - **Females:** `en-US-AvaMultilingualNeural`, `en-US-EmmaMultilingualNeural`, `fr-FR-VivienneMultilingualNeural`, `de-DE-SeraphinaMultilingualNeural`, `pt-BR-ThalitaMultilingualNeural`
    - **Males:** `en-US-AndrewMultilingualNeural`, `en-US-BrianMultilingualNeural`, `en-AU-WilliamMultilingualNeural`, `de-DE-FlorianMultilingualNeural`, `fr-FR-RemyMultilingualNeural`
- This ensures that every language in the world has 5 distinct, high-quality, authentic personas.

---

## 📌 Rule 4: Character & Emotion Voices Preservation
- All 112+ subsequent character and style voices (`kid-*`, `teen-*`, `young-*`, `mid-*`, `senior-*`, `anime-girl`, `radio`, `whisper`, `storyteller`, etc.) MUST remain intact.
- When generating character voices in non-English languages (e.g. Hindi), the base voice must inherit the language's native model (e.g. Swara/Madhur for Hindi) rather than English models, ensuring genuine native accent with the character's pitch/rate modifiers applied on top.

---

## 📌 Rule 5: Mandatory Automated Verification Test
- Before completing ANY task or modifying voice logic in `app.py`, you MUST execute:
  ```powershell
  python test_voice_rules.py
  ```
- All 104 languages MUST pass with **100% SUCCESS (0 collisions, 0 duplicates)**. If any language fails or shows duplicates, the change is invalid and must be corrected immediately.
