from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

from bleepling.models.project import Project
from bleepling.services.environment_service import EnvironmentService
from bleepling.services.time_service import format_time_point, parse_time_point


@dataclass
class CandidateEntry:
    timestamp: str
    candidate: str
    context: str
    line_number: int


@dataclass
class CandidateDecision:
    timestamp: str
    candidate: str
    normalized_candidate: str
    context: str
    decision: str
    reason: str
    line_number: int


class BleepingService:
    def __init__(self) -> None:
        self.environment_service = EnvironmentService()

    DEFAULT_SETTINGS: dict[str, int | str] = {
        "blocklist_threshold": 88,
        "allowlist_threshold": 96,
        "bleep_padding_ms": 250,
        "bleep_duration_ms": 1500,
        "quick_rebleep_mode": "new_only",
        "whisper_model": "medium",
        "whisper_device": "auto",
        "whisper_compute_type": "float16",
        "cuda_extra_paths": "",
    }


    TITLE_WORDS = {
        "herr", "herrn", "frau", "dr", "dr.", "prof", "prof.", "professor", "professorin", "doktor",
        "minister", "ministerin", "staatsminister", "staatsministerin",
        "richter", "richterin", "vorsitzender", "vorsitzende",
        "präsident", "präsidentin", "direktor", "direktorin",
        "staatsanwalt", "staatsanwältin", "justizinspektor", "justizinspektorin",
        "amtsrat", "amtsrätin", "justizrat", "justizrätin",
    }

    GREETING_WORDS = {"lieber", "liebe", "hallo", "geehrte", "geehrter"}

    BAD_NAME_WORDS = {
        "die", "der", "den", "dem", "des", "ein", "eine", "einer", "eines", "einem", "einen",
        "jetzt", "heute", "morgen", "gestern", "inhalt", "frage", "fragen", "antwort",
        "vorrede", "ki", "justiz", "urteil", "entscheidung", "entscheidungen",
        "ihre", "ihrer", "ihren", "ihrem", "ihrererseits", "sein", "seine", "seiner",
        "das", "dass", "dies", "diese", "dieser", "diesem", "dieses",
        "also", "genug", "pizza", "chat", "wort", "koordinaten", "google",
        "und", "oder", "aber", "auch", "mit", "ohne", "für", "gegen", "von", "vor", "nach", "bei",
        "okay", "dank", "ciao", "prima", "gut", "super", "hallo", "tschüss", "tschuess",
        "preise", "preis", "vorteile", "vorteil", "testlauf", "art", "übersicht", "uebersicht",
        "ich", "du", "er", "sie", "es", "wir", "ihr", "euch", "dir", "mir", "uns",
        "ist", "sind", "war", "waren", "heißt", "heisst", "kann", "koennen", "können", "wird", "werden",
        "hat", "habe", "hatte", "hatten", "weiß", "weiss", "weißt", "weisst", "gibt", "gibts", "was", "irgendwas",
    }

    NAME_FOLLOW_VERBS = {
        "fragt", "sagt", "meint", "erwähnt", "schreibt", "antwortet", "weist", "meldet",
        "bemerkt", "erklärt", "hinterfragt", "betont", "erläutert", "ergänzt", "berichtet",
        "verweist", "schildert", "entgegnet", "erwidert", "kommentiert", "beschreibt",
    }

    CONNECTOR_WORDS = {"am", "im", "des", "der", "bei", "beim"}

    INSTITUTION_WORDS = {
        "staatsanwaltschaft", "generalstaatsanwaltschaft", "amtsgericht", "landgericht", "oberlandesgericht",
        "arbeitsgericht", "landesarbeitsgericht", "verwaltungsgericht", "oberverwaltungsgericht",
        "sozialgericht", "landessozialgericht", "finanzgericht", "verfassungsgerichtshof",
        "bundesverfassungsgericht", "bundesgerichtshof", "bundesarbeitsgericht",
        "bundesverwaltungsgericht", "bundessozialgericht", "bundesfinanzhof",
    }

    SUPPORTIVE_PREV_WORDS = {"dem", "den", "der", "des", "mit", "bei", "beim", "am", "im", "auf", "von"}
    ARTICLE_PREV_WORDS = {"die", "der", "dem", "den", "des"}
    VERBISH_FOLLOW_WORDS = {
        "sagt", "sage", "sagte", "meint", "meine", "meinte", "fragt", "frage", "fragte",
        "schreibt", "schrieb", "antwortet", "antwortete", "erklärt", "erklaert", "erklärte",
        "weiß", "weiss", "weißt", "weisst", "hat", "hatte", "arbeitet", "arbeitet", "kommt",
        "kam", "soll", "sollte", "wird", "war", "ist", "habe", "haben", "hieß", "hies",
        "reingeschrieben", "steht", "läuft", "laeuft", "genannt", "wurde", "verwiesen", "angeboten",
    }

    FIRSTNAME_ARTICLE_FOLLOW_WORDS = {
        "hat", "hatte", "habe", "hieß", "hies", "sagte", "meinte", "schrieb",
        "reingeschrieben", "arbeitet", "läuft", "laeuft", "verwiesen", "angeboten",
    }

    FIRSTNAME_COMP_PREV_WORDS = {"dass", "weil", "wenn", "ob"}
    FIRSTNAME_COMP_FOLLOW_WORDS = {"immer", "auch", "noch", "hat", "hatte", "habe", "war", "ist", "wird"}

    def load_lists(self, project: Project) -> tuple[str, str]:
        return (
            project.blocklist_file.read_text(encoding="utf-8") if project.blocklist_file.exists() else "",
            project.allowlist_file.read_text(encoding="utf-8") if project.allowlist_file.exists() else "",
        )

    def save_lists(self, project: Project, blocklist_text: str, allowlist_text: str) -> None:
        project.blocklist_file.write_text(self._normalize_multiline_text(blocklist_text), encoding="utf-8")
        project.allowlist_file.write_text(self._normalize_multiline_text(allowlist_text), encoding="utf-8")

    def load_settings(self, project: Project) -> dict[str, int | str]:
        settings = dict(self.DEFAULT_SETTINGS)
        if project.app_state_file.exists():
            try:
                payload = json.loads(project.app_state_file.read_text(encoding="utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
            saved = payload.get("bleeping", {})
            if isinstance(saved, dict):
                settings.update(saved)
        return settings

    def save_settings(self, project: Project, settings: dict[str, int | str]) -> None:
        payload: dict[str, object] = {}
        if project.app_state_file.exists():
            try:
                payload = json.loads(project.app_state_file.read_text(encoding="utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
        payload["bleeping"] = settings
        project.app_state_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def list_raw_candidate_files(self, project: Project) -> list[Path]:
        return self._list_files(project.candidates_raw_dir, "*.txt")

    def list_words_json_files(self, project: Project) -> list[Path]:
        return self._list_files(project.transcription_json_dir, "*.words.json")

    def list_video_files(self, project: Project) -> list[Path]:
        return self._list_files(project.input_video_dir, "*")

    def list_audio_files(self, project: Project) -> list[Path]:
        return self._list_files(project.input_audio_dir, "*") + self._list_files(project.transcription_wav_dir, "*.wav")

    def create_wav_from_video(self, project: Project, video_path: Path) -> Path:
        if not video_path.exists():
            raise FileNotFoundError(f"Videodatei nicht gefunden: {video_path}")
        project.transcription_wav_dir.mkdir(parents=True, exist_ok=True)
        output = project.transcription_wav_dir / f"{video_path.stem}.wav"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(output),
        ]
        self._run_subprocess(cmd, cwd=project.root_path)
        return output

    def transcribe_wav_to_words_json(
        self,
        project: Project,
        wav_path: Path,
        model: str = "medium",
        device: str = "auto",
        compute_type: str = "float16",
        extra_cuda_paths: str = "",
    ) -> Path:
        if not wav_path.exists():
            raise FileNotFoundError(f"WAV-Datei nicht gefunden: {wav_path}")
        script_path = self._legacy_script_path("transcribe_with_word_timestamps.py")
        extra_paths = [part.strip() for part in str(extra_cuda_paths).split(";") if part.strip()]
        runtime_env = self.environment_service.build_runtime_env(extra_paths)

        requested_mode = (device or "auto").lower()
        attempts: list[tuple[str, str]] = []
        if requested_mode == "cpu":
            attempts = [("cpu", "int8")]
        elif requested_mode == "gpu":
            attempts = [("cuda", compute_type or "float16")]
        else:
            attempts = [("cuda", compute_type or "float16"), ("cpu", "int8")]

        def build_cmd(selected_device: str, selected_compute_type: str) -> list[str]:
            return [
                sys.executable,
                str(script_path),
                "--input",
                str(wav_path),
                "--output-dir",
                str(project.transcription_json_dir),
                "--model",
                model,
                "--device",
                selected_device,
                "--compute-type",
                selected_compute_type,
                "--language",
                project.language,
            ]

        errors: list[str] = []
        for selected_device, selected_compute_type in attempts:
            try:
                self._log(project, f"Transkription startet: device={selected_device}, compute_type={selected_compute_type}, wav={wav_path.name}")
                self._run_subprocess(build_cmd(selected_device, selected_compute_type), cwd=project.root_path, env=runtime_env)
                self._log(project, f"Transkription erfolgreich: device={selected_device}, wav={wav_path.name}")
                output = project.transcription_json_dir / f"{wav_path.stem}.words.json"
                if not output.exists():
                    raise FileNotFoundError("Die Transkription wurde ausgeführt, aber die words.json wurde nicht gefunden.")
                return output
            except Exception as exc:
                details = str(exc)
                errors.append(f"{selected_device}: {details}")
                self._log(project, f"Transkription fehlgeschlagen: device={selected_device}, details={details}")
                if requested_mode == "gpu":
                    raise RuntimeError(
                        "Die GPU-Transkription ist fehlgeschlagen. Bitte die Prüfung im Reiter Einstellungen / Logs ausführen.\n\n"
                        f"Details:\n{details}"
                    )
                if requested_mode == "cpu":
                    raise RuntimeError(
                        "Die CPU-Transkription ist fehlgeschlagen.\n\n"
                        f"Details:\n{details}"
                    )
                continue

        raise RuntimeError(
            "Die Transkription ist fehlgeschlagen.\n\nVersuchte Modi:\n- "
            + "\n- ".join(errors)
            + "\n\nBitte die Prüfung im Reiter Einstellungen / Logs ausführen."
        )

    def generate_candidate_file_from_words_json(self, project: Project, words_json_path: Path) -> Path:
        if not words_json_path.exists():
            raise FileNotFoundError(f"words.json nicht gefunden: {words_json_path}")
        project.candidates_raw_dir.mkdir(parents=True, exist_ok=True)
        candidates = self.extract_candidates_from_words_json(words_json_path)
        output = project.candidates_raw_dir / f"{words_json_path.stem.replace('.words', '')}_NAMEN_KANDIDATEN_auto.txt"
        lines = [f"{ts} | {name} | {ctx}" for ts, name, ctx in candidates]
        output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return output

    def extract_candidates_from_words_json(self, words_json_path: Path) -> list[tuple[str, str, str]]:
        data = json.loads(words_json_path.read_text(encoding="utf-8"))
        words: list[dict] = []
        for segment in data.get("segments", []):
            for word in segment.get("words", []):
                if word.get("start") is None or word.get("word") is None:
                    continue
                cleaned = self.clean_word(str(word["word"]))
                if not cleaned:
                    continue
                words.append({"start": float(word["start"]), "word": cleaned})
        if not words:
            return []

        tokens = [w["word"] for w in words]
        lowers = [t.lower() for t in tokens]
        results: list[tuple[str, str, str]] = []
        seen: set[tuple[str, str]] = set()

        def add_candidate(start_idx: int, candidate: str) -> None:
            candidate = " ".join(candidate.split()).strip()
            if not candidate:
                return
            norm = self.normalize_name(candidate)
            if not norm:
                return
            ts = self.seconds_to_ts(float(words[start_idx]["start"]))
            key = (ts, norm)
            if key in seen:
                return
            seen.add(key)
            results.append((ts, candidate, self.make_context(words, start_idx)))

        intro_words = self.TITLE_WORDS | self.GREETING_WORDS

        # starke Anrede-/Titelkontexte
        for i, low in enumerate(lowers):
            if low not in intro_words:
                continue
            j = i + 1
            while j < len(tokens) and lowers[j] in intro_words:
                j += 1
            if j >= len(tokens):
                continue

            # Justiz-Funktionskette bis zum Namensblock
            if low in self.TITLE_WORDS:
                k = j
                while k < len(tokens) and lowers[k] in self.TITLE_WORDS:
                    k += 1
                while k < len(tokens) and (lowers[k] in self.CONNECTOR_WORDS or self._is_institution_word(tokens[k])):
                    k += 1
                if k < len(tokens) and self._looks_like_name_token(tokens[k], strong=True):
                    if k + 1 < len(tokens) and self._looks_like_name_token(tokens[k + 1], strong=True):
                        add_candidate(k, f"{tokens[k]} {tokens[k + 1]}")
                    add_candidate(k, tokens[k])

            # normaler Anredeblock, bis der nächste Intro-Block beginnt
            parts: list[str] = []
            start_idx = None
            k = j
            while k < len(tokens) and len(parts) < 2:
                if lowers[k] in intro_words:
                    break
                if self._looks_like_name_token(tokens[k], strong=True):
                    if start_idx is None:
                        start_idx = k
                    parts.append(tokens[k])
                    k += 1
                    continue
                break
            if parts and start_idx is not None:
                add_candidate(start_idx, " ".join(parts))

        # einzelner Name vor typischem Folgeverb
        for i, token in enumerate(tokens[:-1]):
            if self._looks_like_name_token(token, strong=False) and lowers[i + 1] in self.NAME_FOLLOW_VERBS:
                add_candidate(i, token)

        # gezielte Vornamenmuster: "von X auf Y"
        for i in range(len(tokens) - 3):
            if lowers[i] == "von" and lowers[i + 2] == "auf":
                if self._is_likely_first_name_token(tokens[i + 1]):
                    add_candidate(i + 1, tokens[i + 1])
                if self._is_likely_first_name_token(tokens[i + 3]):
                    add_candidate(i + 3, tokens[i + 3])

        # gezielte Vornamenmuster: "die/der X hatte ..." oder "dass X immer ..."
        for i in range(1, len(tokens) - 1):
            prev_low = lowers[i - 1]
            next_low = lowers[i + 1]
            if self._is_likely_first_name_token(tokens[i]):
                if prev_low in self.ARTICLE_PREV_WORDS and next_low in self.FIRSTNAME_ARTICLE_FOLLOW_WORDS:
                    add_candidate(i, tokens[i])
                    continue
                if prev_low in self.FIRSTNAME_COMP_PREV_WORDS and next_low in self.FIRSTNAME_COMP_FOLLOW_WORDS:
                    add_candidate(i, tokens[i])
                    continue

        # freie Vorname-Nachname-Paare
        blocked_prev = {"ein", "eine", "einem", "einen", "einer", "eines"}
        for i in range(len(tokens) - 1):
            first, second = tokens[i], tokens[i + 1]
            prev_low = lowers[i - 1] if i > 0 else ""
            if prev_low in blocked_prev:
                continue
            if not self._looks_like_name_token(first, strong=False):
                continue
            if not self._looks_like_name_token(second, strong=False):
                continue
            if self._pair_should_be_blocked(first, second):
                continue
            add_candidate(i, f"{first} {second}")

        # bestätigte Namen dateiintern nachverfolgen
        confirmed_parts: set[str] = set()
        for _, cand, _ in results:
            norm = self.normalize_name(cand)
            if not norm:
                continue
            for p in norm.split():
                if len(p) >= 3 and p not in self.BAD_NAME_WORDS:
                    confirmed_parts.add(p)
                    if p.endswith("s") and len(p) >= 4:
                        confirmed_parts.add(p[:-1])
                    else:
                        confirmed_parts.add(p + "s")
        for i, token in enumerate(tokens):
            norm_tok = self.normalize_name(token)
            if not norm_tok or len(norm_tok) < 3 or norm_tok in self.BAD_NAME_WORDS:
                continue
            if norm_tok in confirmed_parts and self._looks_like_name_token(token, strong=True):
                add_candidate(i, token)

        # lokale Konsolidierung: Vollname schlägt Teilname in der Nähe
        enriched = []
        for ts, cand, ctx in results:
            enriched.append((self._ts_to_seconds(ts), ts, cand, ctx, self.normalize_name(cand).split()))
        keep = [True] * len(enriched)
        for i, (sec, ts, cand, ctx, parts) in enumerate(enriched):
            if len(parts) != 1:
                continue
            for j, (sec2, ts2, cand2, ctx2, parts2) in enumerate(enriched):
                if i == j or len(parts2) < 2:
                    continue
                if abs(sec - sec2) <= 2.0 and parts[0] in parts2:
                    keep[i] = False
                    break
        filtered = [(ts, cand, ctx) for keep_it, (_, ts, cand, ctx, _) in zip(keep, enriched) if keep_it]
        filtered.sort(key=lambda item: item[0])
        return filtered

    def build_blocklist_from_candidate_file(self, candidate_file: Path) -> str:
        entries = self.parse_candidate_file(candidate_file)
        names = sorted({entry.candidate.strip() for entry in entries if entry.candidate.strip()}, key=str.casefold)
        return "\n".join(names) + ("\n" if names else "")

    def parse_candidate_file(self, path: Path) -> list[CandidateEntry]:
        entries: list[CandidateEntry] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(" | ", 2)]
            if len(parts) < 2:
                continue
            timestamp = parts[0]
            candidate = parts[1]
            context = parts[2] if len(parts) > 2 else ""
            entries.append(CandidateEntry(timestamp=timestamp, candidate=candidate, context=context, line_number=line_number))
        return entries

    def evaluate_candidates(
        self,
        entries: Iterable[CandidateEntry],
        blocklist_text: str,
        allowlist_text: str,
        blocklist_threshold: int,
        allowlist_threshold: int,
    ) -> list[CandidateDecision]:
        blocklist = self._prepare_name_list(blocklist_text)
        allowlist = self._prepare_name_list(allowlist_text)
        blocklist_is_empty = len(blocklist) == 0

        decisions: list[CandidateDecision] = []
        for entry in entries:
            normalized_candidate = self.normalize_name(entry.candidate)
            if not normalized_candidate:
                decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "ignorieren", "leerer Kandidat nach Normalisierung", entry.line_number))
                continue

            allow_match, allow_score = self._best_match(normalized_candidate, allowlist)
            if allow_match and allow_score >= allowlist_threshold:
                decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "erlaubt", f"Allowlist: {allow_match} ({allow_score}%)", entry.line_number))
                continue

            if blocklist_is_empty:
                if self._looks_like_person_name(entry.candidate, entry.context):
                    decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "prüfen", "Blocklist leer: möglicher Personenname, bitte prüfen", entry.line_number))
                else:
                    decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "ignorieren", "Blocklist leer, aber Form spricht eher gegen Personenname", entry.line_number))
                continue

            block_match, block_score = self._best_match(normalized_candidate, blocklist)
            if block_match and block_score >= blocklist_threshold:
                decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "bleepen", f"Blocklist: {block_match} ({block_score}%)", entry.line_number))
                continue

            if self._looks_like_person_name(entry.candidate, entry.context):
                decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "prüfen", "kein Treffer oberhalb der Schwelle", entry.line_number))
            else:
                decisions.append(CandidateDecision(entry.timestamp, entry.candidate, normalized_candidate, entry.context, "ignorieren", "Form spricht eher gegen Personenname", entry.line_number))
        return decisions

    def write_reviewed_candidates(self, project: Project, source_file: Path, decisions: list[CandidateDecision]) -> Path:
        output_path = project.candidates_reviewed_dir / f"{source_file.stem}_reviewed.txt"
        lines = [f"{item.timestamp} | {item.candidate} | {item.decision.upper()} | {item.reason} | {item.context}".rstrip() for item in decisions]
        output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return output_path

    def write_point_times_file(self, project: Project, source_file: Path, decisions: list[CandidateDecision]) -> Path:
        output_path = project.times_dir / self._build_times_filename(source_file)
        timestamps = [item.timestamp for item in decisions if item.decision == "bleepen"]
        unique_timestamps = list(dict.fromkeys(timestamps))
        output_path.write_text("\n".join(unique_timestamps) + ("\n" if unique_timestamps else ""), encoding="utf-8")
        return output_path

    def write_times_file(self, project: Project, source_file: Path, decisions: list[CandidateDecision]) -> Path:
        # Transitional compatibility wrapper: this legacy writer still persists
        # point-based .times.txt files for the existing bleeping workflow.
        return self.write_point_times_file(project, source_file, decisions)

    def write_quick_rebleep_file(self, project: Project, source_file: Path, decisions: list[CandidateDecision]) -> Path:
        target = project.times_dir / self._build_quick_rebleep_filename(source_file)
        desired = [item.timestamp for item in decisions if item.decision == "bleepen"]
        existing_regular = project.times_dir / self._build_times_filename(source_file)
        existing: set[str] = set()
        if existing_regular.exists():
            existing = {line.strip() for line in existing_regular.read_text(encoding="utf-8").splitlines() if line.strip()}
        new_only = [timestamp for timestamp in desired if timestamp not in existing]
        unique_new_only = list(dict.fromkeys(new_only))
        target.write_text("\n".join(unique_new_only) + ("\n" if unique_new_only else ""), encoding="utf-8")
        return target

    def summarize_decisions(self, decisions: Iterable[CandidateDecision]) -> dict[str, int]:
        summary = {"gesamt": 0, "bleepen": 0, "erlaubt": 0, "prüfen": 0, "ignorieren": 0}
        for item in decisions:
            summary["gesamt"] += 1
            summary[item.decision] = summary.get(item.decision, 0) + 1
        return summary

    def normalize_name(self, name: str) -> str:
        name = name.strip().lower()
        name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        name = re.sub(r"[^a-z0-9 \-]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        changed = True
        while changed:
            changed = False
            for prefix in (
                "herr ", "herrn ", "frau ", "dr ", "prof ", "professor ", "professorin ", "doktor ",
                "minister ", "ministerin ", "staatsminister ", "staatsministerin ",
                "richter ", "richterin ", "vorsitzender ", "vorsitzende ",
                "präsident ", "präsidentin ", "direktor ", "direktorin ",
                "staatsanwalt ", "staatsanwältin ", "justizinspektor ", "justizinspektorin ",
                "amtsrat ", "amtsrätin ", "justizrat ", "justizrätin ",
                "lieber ", "liebe ", "geehrte ", "geehrter ", "hallo ",
            ):
                if name.startswith(prefix):
                    name = name[len(prefix):].strip()
                    changed = True
        return name

    def clean_word(self, word: str) -> str:
        return word.strip().strip(".,;:!?()[]{}\"'“”‚‘«»")

    def is_capitalized_name_like(self, word: str) -> bool:
        return bool(re.match(r"^[A-ZÄÖÜ][A-Za-zÄÖÜäöüß\-]{2,}$", word))

    def _looks_like_name_token(self, word: str, strong: bool = False) -> bool:
        cleaned = self.clean_word(word)
        if not cleaned:
            return False
        norm = self.normalize_name(cleaned)
        if len(norm) < 3 or norm in self.BAD_NAME_WORDS:
            return False
        if norm in self.CONNECTOR_WORDS:
            return False
        if self._is_institution_word(cleaned):
            return False
        if strong:
            return self.is_capitalized_name_like(cleaned)
        return self.is_capitalized_name_like(cleaned)

    def _looks_like_second_name_token(self, word: str) -> bool:
        cleaned = self.clean_word(word)
        if not self._looks_like_name_token(cleaned, strong=False):
            return False
        norm = self.normalize_name(cleaned)
        return len(norm) >= 4

    def _is_likely_first_name_token(self, word: str) -> bool:
        cleaned = self.clean_word(word)
        if not self._looks_like_name_token(cleaned, strong=False):
            return False
        norm = self.normalize_name(cleaned)
        if norm in self.TITLE_WORDS or norm in self.CONNECTOR_WORDS or self._is_institution_word(cleaned):
            return False
        if len(norm) < 4 or len(norm) > 12:
            return False
        return True

    def _pair_should_be_blocked(self, first: str, second: str) -> bool:
        n1 = self.normalize_name(first)
        n2 = self.normalize_name(second)
        if not n1 or not n2:
            return True
        if n1 == n2:
            return True
        blocked = self.BAD_NAME_WORDS | self.GREETING_WORDS | self.TITLE_WORDS | self.CONNECTOR_WORDS
        return n1 in blocked or n2 in blocked or n2 in {"ich", "du", "er", "sie", "es", "wir", "ihr"}

    def _is_institution_word(self, word: str) -> bool:
        norm = self.normalize_name(word)
        if norm in self.INSTITUTION_WORDS:
            return True
        if norm.endswith("s") and norm[:-1] in self.INSTITUTION_WORDS:
            return True
        return False

    def is_bad_name(self, word: str) -> bool:
        return self.normalize_name(word) in self.BAD_NAME_WORDS

    def seconds_to_ts(self, seconds: float) -> str:
        return format_time_point(seconds, clamp_zero=False)

    def make_context(self, words: list[dict], index: int, window: int = 10) -> str:
        left = max(0, index - window)
        right = min(len(words), index + window + 1)
        return " ".join(self.clean_word(str(w.get("word", ""))) for w in words[left:right]).strip()

    def _ts_to_seconds(self, timestamp: str) -> float:
        point = parse_time_point(timestamp)
        if point is None:
            raise ValueError(f"Ungültiger Zeitstempel: {timestamp}")
        return point.seconds

    def _list_files(self, folder: Path, pattern: str) -> list[Path]:
        if not folder.exists():
            return []
        paths = [p for p in folder.glob(pattern) if p.is_file()]
        return sorted(paths, key=lambda p: p.name.lower())

    def _legacy_script_path(self, script_name: str) -> Path:
        root = Path(__file__).resolve().parents[3]
        path = root / "legacy_reference" / "v5_scripts" / script_name
        if not path.exists():
            raise FileNotFoundError(f"Legacy-Skript nicht gefunden: {path}")
        return path

    def _run_subprocess(self, cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
        result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or "Unbekannter Fehler"
            raise RuntimeError(details)

    def _log(self, project: Project, message: str) -> None:
        try:
            project.log_file.parent.mkdir(parents=True, exist_ok=True)
            with project.log_file.open("a", encoding="utf-8") as handle:
                handle.write(message.rstrip() + "\n")
        except Exception:
            pass

    def get_runtime_cuda_paths(self, extra_cuda_paths: str = "") -> list[Path]:
        extra_paths = [part.strip() for part in str(extra_cuda_paths).split(";") if part.strip()]
        return self.environment_service.get_recommended_cuda_paths(extra_paths)


    def _looks_like_person_name(self, candidate: str, context: str) -> bool:
        normalized = self.normalize_name(candidate)
        if not normalized:
            return False
        parts = [p for p in re.split(r"\s+", candidate.strip()) if p]
        if not parts or len(parts) > 3:
            return False
        if any(self.is_bad_name(p) for p in parts):
            return False
        if len(parts) == 1:
            return self._looks_like_name_token(parts[0], strong=True)
        return all(self._looks_like_name_token(p, strong=True) for p in parts)

    def _prepare_name_list(self, text: str) -> list[str]:
        values = []
        for line in text.splitlines():
            normalized = self.normalize_name(line)
            if normalized and normalized not in values:
                values.append(normalized)
        return values

    def _best_match(self, candidate: str, values: list[str]) -> tuple[str | None, int]:
        best_value = None
        best_score = 0
        variants = {candidate}
        if candidate.endswith("s") and len(candidate) > 4:
            variants.add(candidate[:-1])
        else:
            variants.add(candidate + "s")
        for value in values:
            for cand in variants:
                score = int(round(SequenceMatcher(None, cand, value).ratio() * 100))
                if cand == value:
                    score = 100
                if score > best_score:
                    best_value = value
                    best_score = score
        return best_value, best_score

    def _normalize_multiline_text(self, text: str) -> str:
        lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + ("\n" if lines else "")

    def _build_times_filename(self, source_file: Path) -> str:
        stem = source_file.stem
        if not stem.lower().endswith(".times"):
            stem = f"{stem}.times"
        return f"{stem}.txt"

    def _build_quick_rebleep_filename(self, source_file: Path) -> str:
        return f"{source_file.stem}.quick.times.txt"
