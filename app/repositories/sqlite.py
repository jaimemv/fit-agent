import sqlite3
from datetime import date
from pathlib import Path
from threading import Lock

from app.models.domain import (
    BiometricEntry,
    KnowledgeSnippet,
    NutritionLogEntry,
    UserProfile,
    WorkoutLogEntry,
)


class SQLiteRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._lock = Lock()
        self._ensure_parent_dir()
        self._init_schema()
        self._seed_default_knowledge()

    def upsert_profile(self, profile: UserProfile) -> UserProfile:
        payload = profile.model_dump_json()
        with self._locked_conn() as conn:
            conn.execute(
                """
                INSERT INTO profiles (user_id, payload)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload
                """,
                (profile.user_id, payload),
            )
            conn.commit()
        return profile

    def get_profile(self, user_id: str) -> UserProfile | None:
        with self._locked_conn() as conn:
            row = conn.execute(
                "SELECT payload FROM profiles WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return UserProfile.model_validate_json(row["payload"])

    def add_biometric(self, entry: BiometricEntry) -> None:
        self._insert_user_dated_payload(
            table="biometrics",
            user_id=entry.user_id,
            when_date=entry.when.isoformat(),
            payload=entry.model_dump_json(),
        )

    def get_recent_biometrics(self, user_id: str, limit: int = 14) -> list[BiometricEntry]:
        rows = self._select_recent_user_payloads(table="biometrics", user_id=user_id, limit=limit)
        return [BiometricEntry.model_validate_json(row["payload"]) for row in rows]

    def add_workout_log(self, entry: WorkoutLogEntry) -> None:
        self._insert_user_dated_payload(
            table="workouts",
            user_id=entry.user_id,
            when_date=entry.when.isoformat(),
            payload=entry.model_dump_json(),
        )

    def get_recent_workouts(self, user_id: str, limit: int = 50) -> list[WorkoutLogEntry]:
        rows = self._select_recent_user_payloads(table="workouts", user_id=user_id, limit=limit)
        return [WorkoutLogEntry.model_validate_json(row["payload"]) for row in rows]

    def add_nutrition_log(self, entry: NutritionLogEntry) -> None:
        self._insert_user_dated_payload(
            table="nutrition",
            user_id=entry.user_id,
            when_date=entry.when.isoformat(),
            payload=entry.model_dump_json(),
        )

    def get_recent_nutrition(self, user_id: str, limit: int = 30) -> list[NutritionLogEntry]:
        rows = self._select_recent_user_payloads(table="nutrition", user_id=user_id, limit=limit)
        return [NutritionLogEntry.model_validate_json(row["payload"]) for row in rows]

    def search_knowledge(self, query: str, limit: int = 3) -> list[KnowledgeSnippet]:
        q = query.strip().lower()
        with self._locked_conn() as conn:
            rows = conn.execute("SELECT source, topic, note FROM knowledge").fetchall()
        snippets = [KnowledgeSnippet(source=row["source"], topic=row["topic"], note=row["note"]) for row in rows]

        if not q:
            return snippets[:limit]

        ranked: list[tuple[int, KnowledgeSnippet]] = []
        for snippet in snippets:
            score = 0
            topic = snippet.topic.lower()
            note = snippet.note.lower()
            if q in topic:
                score += 2
            if q in note:
                score += 1
            if score:
                ranked.append((score, snippet))

        if not ranked:
            return snippets[:limit]

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [snippet for _, snippet in ranked[:limit]]

    def add_knowledge_snippet(self, snippet: KnowledgeSnippet) -> None:
        with self._locked_conn() as conn:
            conn.execute(
                "INSERT INTO knowledge (source, topic, note) VALUES (?, ?, ?)",
                (snippet.source, snippet.topic, snippet.note),
            )
            conn.commit()

    def seed_demo_data(self, user_id: str) -> None:
        if self.get_recent_biometrics(user_id, limit=1):
            return
        self.add_biometric(
            BiometricEntry(
                user_id=user_id,
                when=date.today(),
                weight_kg=80.0,
                resting_hr=60,
                sleep_hours=7.5,
                stress_1_to_10=4,
                soreness_1_to_10=3,
            )
        )

    def _insert_user_dated_payload(self, *, table: str, user_id: str, when_date: str, payload: str) -> None:
        with self._locked_conn() as conn:
            conn.execute(
                f"INSERT INTO {table} (user_id, when_date, payload) VALUES (?, ?, ?)",
                (user_id, when_date, payload),
            )
            conn.commit()

    def _select_recent_user_payloads(self, *, table: str, user_id: str, limit: int) -> list[sqlite3.Row]:
        with self._locked_conn() as conn:
            return conn.execute(
                f"""
                SELECT payload
                FROM {table}
                WHERE user_id = ?
                ORDER BY when_date DESC, id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

    def _ensure_parent_dir(self) -> None:
        db_file = Path(self._db_path)
        if db_file.parent != Path("."):
            db_file.parent.mkdir(parents=True, exist_ok=True)

    def _init_schema(self) -> None:
        with self._locked_conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS biometrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    when_date TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_biometrics_user_date ON biometrics (user_id, when_date DESC);

                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    when_date TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts (user_id, when_date DESC);

                CREATE TABLE IF NOT EXISTS nutrition (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    when_date TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_nutrition_user_date ON nutrition (user_id, when_date DESC);

                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    note TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def _seed_default_knowledge(self) -> None:
        defaults = [
            KnowledgeSnippet(
                source="NSCA Essentials",
                topic="progressive overload",
                note="Increase training stress gradually via load, reps, sets, or density.",
            ),
            KnowledgeSnippet(
                source="Sports Nutrition Position Stand",
                topic="protein",
                note="Daily protein targets are usually distributed over multiple meals.",
            ),
            KnowledgeSnippet(
                source="ACSM Guidelines",
                topic="pain management",
                note="Sharp or escalating pain during training is a signal to stop and reassess.",
            ),
        ]
        with self._locked_conn() as conn:
            existing = conn.execute("SELECT COUNT(*) AS count FROM knowledge").fetchone()
            if existing and int(existing["count"]) > 0:
                return
            conn.executemany(
                "INSERT INTO knowledge (source, topic, note) VALUES (?, ?, ?)",
                [(item.source, item.topic, item.note) for item in defaults],
            )
            conn.commit()

    def _open_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _locked_conn(self):
        return _LockedConnectionContext(self._lock, self._open_conn)


class _LockedConnectionContext:
    def __init__(self, lock: Lock, conn_factory) -> None:
        self._lock = lock
        self._conn_factory = conn_factory
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self._lock.acquire()
        self._conn = self._conn_factory()
        return self._conn

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._conn is not None:
                if exc:
                    self._conn.rollback()
                self._conn.close()
        finally:
            self._lock.release()
