# 🗺️ German Translation Game - Feature Roadmap

This document outlines planned features and game modes for future implementation.

---

## ✅ Implemented Games

- [x] **German → English Translation** - Type English translation of German sentences
- [x] **English → German Translation** - Type German translation of English sentences
- [x] **Word Selection (EN → DE)** - Build German translation by selecting words in order
- [x] **Article Selection** - Choose correct German article (der/die/das) with case variations
- [x] **Fill-in-the-Blank** - Complete German sentences with missing words
- [x] **Error Detection** - Find and correct errors in German sentences
- [x] **Verb Conjugation Challenge** - Conjugate German verbs with different pronouns and tenses
- [x] **Speed Translation Race** - Timed translation game with points, combos, and time bonuses
- [x] **Conversation Builder** - Multi-turn conversation scenarios with contextual responses

---

## 📋 Planned Games

### High Priority (Educational Value + Ease of Implementation)

#### 1. **Verb Conjugation Challenge**
**Status:** ✅ Implemented
**Difficulty:** Easy (1-2 hours)
**Description:**
- Show infinitive verb + pronoun + tense
- User types correct conjugated form
- Example: "gehen + ich + Präteritum" → "ging"
- AI validates and explains conjugation rules

**Why:** Reinforces verb patterns already available in CSV data

**Implementation Notes:**
- Reuse existing `VerbLoader` for verb data
- Simple text input validation
- Progressive hints: tense pattern, similar verbs, first letter

---

#### 2. **Synonym/Antonym Matching**
**Status:** Not Started
**Difficulty:** Easy-Medium (2-3 hours)
**Description:**
- Show German word + context sentence
- User selects synonym or antonym from multiple choice options
- AI generates plausible distractors
- Alternate between synonym/antonym rounds

**Why:** Expands vocabulary beyond simple translation

**Implementation Notes:**
- Need new Pydantic model: `SynonymExercise`
- Multiple choice UI (4 options recommended)
- Track separate stats for synonyms vs antonyms

---

#### 3. **Sentence Completion**
**Status:** Not Started
**Difficulty:** Medium (2-4 hours)
**Description:**
- AI shows partial German sentence
- Multiple completion options (only one grammatically correct)
- Tests grammar + vocabulary + context understanding
- Provides explanation for incorrect options

**Why:** Real-world usage patterns, tests comprehension

**Implementation Notes:**
- Similar to article selection UI
- Need model: `SentenceCompletionExercise`
- 3-4 completion options with detailed explanations

---

### Medium Priority (More Complex Implementation)

#### 4. **Sentence Reordering Game**
**Status:** Not Started
**Difficulty:** Medium-Hard (4-6 hours)
**Description:**
- AI generates German sentence, splits it into chunks (2-4 words each)
- User drags/clicks chunks to rebuild correct word order
- Focus on German word order rules (V2 position, subordinate clauses)
- Different difficulty levels test different constructions

**Why:** German word order is tricky, visual/interactive learning

**Implementation Notes:**
- Requires drag-and-drop or click-to-reorder UI in Streamlit
- Need model: `SentenceReorderExercise`
- Chunk size based on difficulty
- Validate complete sentence order

---

#### 5. **Category Sorting**
**Status:** Not Started
**Difficulty:** Medium (3-4 hours)
**Description:**
- Mix of German words from different categories
- Categories: Food, Animals, Verbs, Adjectives, Tools, Places, etc.
- User sorts them into correct categories
- Optional: Timer-based for extra challenge

**Why:** Builds semantic connections, vocabulary organization

**Implementation Notes:**
- Multiple selection lists or drag-drop interface
- Need model: `CategorySortingExercise`
- Load additional noun/adjective data from CSV
- Track accuracy per category

---

#### 6. **Conversation Builder**
**Status:** ✅ Implemented
**Difficulty:** Hard (6-8 hours)
**Description:**
- AI presents realistic scenario (restaurant, shopping, travel)
- User selects appropriate German responses from options
- Builds a multi-turn conversation (5-7 exchanges)
- Context matters: earlier choices affect later options

**Why:** Practical communication skills, real-world application

**Implementation Notes:**
- Stateful conversation tracking
- Need model: `ConversationExercise` with multiple turns
- Context-aware option generation
- Story branching logic

---

### Low Priority (Nice to Have)

#### 7. **Speed Translation Race**
**Status:** ✅ Implemented
**Difficulty:** Medium (3-4 hours)
**Description:**
- Short words/phrases appear rapidly (every 5-10 seconds)
- User types translation quickly
- Scoring based on speed + accuracy
- Difficulty increases: more complex phrases, less time

**Why:** Builds fluency and automatic recall

**Implementation Notes:**
- Timer logic with Streamlit
- Real-time countdown display
- Combo multipliers for consecutive correct answers
- Leaderboard (local session)

---

#### 8. **German Wordle Clone**
**Status:** Not Started
**Difficulty:** Medium (4-5 hours)
**Description:**
- Guess German word of the day (4-6 letters)
- Color feedback for correct letters/positions
- 6 attempts maximum
- Category hints (noun/verb/adjective)
- Daily word generation

**Why:** Popular game format, daily engagement habit

**Implementation Notes:**
- Date-based word generation (seed random)
- Color-coded feedback UI
- German keyboard helper (ä, ö, ü, ß)
- Statistics tracking (win rate, streak)

---

## 🔊 Advanced Features (Future Expansion)

### Audio/Speech Integration

#### 9. **Pronunciation Practice**
**Status:** Not Started
**Difficulty:** Very Hard (10+ hours)
**Description:**
- Display German sentence
- User speaks the sentence
- AI validates pronunciation
- Highlights problematic sounds

**Why:** Complete language learning experience

**Requirements:**
- Speech-to-text integration (Web Speech API or external service)
- Pronunciation scoring algorithm
- Audio playback of correct pronunciation
- Microphone permissions

---

#### 10. **Listening Comprehension**
**Status:** Not Started
**Difficulty:** Hard (6-8 hours)
**Description:**
- Play German audio (text-to-speech)
- User types what they heard
- Multiple difficulty levels (speed, clarity)
- Support for different accents

**Why:** Trains listening skills, real-world comprehension

**Requirements:**
- Text-to-speech service (Google TTS, Azure, etc.)
- Audio player UI in Streamlit
- Playback speed controls
- Option to replay

---

## 🎨 UI/UX Improvements

### Planned Enhancements

- [ ] **Game Statistics Dashboard** - Visualize progress across all games
- [ ] **Achievement System** - Badges for milestones (100 correct, 90% accuracy, etc.)
- [ ] **Custom Difficulty Presets** - Save favorite settings per game
- [ ] **Dark Mode** - Toggle for reduced eye strain
- [ ] **Keyboard Shortcuts** - Quick navigation and answer submission
- [ ] **Mobile Optimization** - Better responsive design for phones/tablets
- [ ] **Streak Tracker** - Daily practice streak counter
- [ ] **Study Mode** - Review incorrect answers from past sessions

---

## 📊 Data & Content Expansion

### Planned Improvements

- [ ] **Extended Vocabulary CSV** - More nouns, adjectives, adverbs
- [ ] **Phrase Database** - Common German phrases and idioms
- [ ] **Thematic Lessons** - Vocabulary grouped by topic (travel, food, work)
- [ ] **Grammar Rules Reference** - In-app grammar explanations
- [ ] **Progress Export** - Download stats as CSV/PDF
- [ ] **Difficulty Auto-Adjustment** - AI adapts difficulty based on performance

---

## 🛠️ Technical Improvements

### Planned Enhancements

- [ ] **Database Integration** - Store user progress persistently (SQLite/PostgreSQL)
- [ ] **User Accounts** - Login system for multi-device progress
- [ ] **API Rate Limiting** - Better handling of AI provider limits
- [ ] **Caching Layer** - Cache AI-generated exercises for faster loading
- [ ] **Offline Mode** - Pre-generated exercises for offline practice
- [ ] **A/B Testing** - Experiment with different game mechanics
- [ ] **Analytics Dashboard** - Track user behavior and game effectiveness

---

## 📅 Estimated Timeline

### Q1 2025
- [x] Core translation games
- [x] Word selection game
- [x] Article selection game
- [x] Fill-in-the-blank game
- [x] Error detection game

### Q2 2025 (Planned)
- [ ] Verb conjugation challenge
- [ ] Synonym/antonym matching
- [ ] Sentence completion
- [ ] UI improvements & statistics dashboard

### Q3 2025 (Planned)
- [ ] Sentence reordering
- [ ] Category sorting
- [ ] Conversation builder
- [ ] Database integration

### Q4 2025 (Aspirational)
- [ ] Speed translation race
- [ ] German Wordle clone
- [ ] Audio/speech features
- [ ] Mobile app version

---

## 🤝 Contributing

Ideas for new games? Found a bug? Want to contribute?

1. Open an issue describing your idea
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

All contributions welcome!

---

## 📝 Notes

- Priority is based on educational value + implementation complexity
- Timeline is flexible and depends on user feedback
- Feature requests can be added via GitHub issues

---

*Last updated: 2025-10-27*
