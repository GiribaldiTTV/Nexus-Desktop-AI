import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class CommandAction:
    id: str
    title: str
    target_kind: str
    target: str
    aliases: tuple[str, ...]


DEFAULT_COMMAND_ACTIONS = (
    CommandAction(
        id="open_jarvis_workspace",
        title="Open Jarvis Workspace",
        target_kind="folder",
        target=str(ROOT_DIR),
        aliases=("open jarvis workspace", "open workspace", "open jarvis folder"),
    ),
    CommandAction(
        id="open_jarvis_docs",
        title="Open Jarvis Docs",
        target_kind="folder",
        target=str(ROOT_DIR / "docs"),
        aliases=("open jarvis docs", "open docs", "open jarvis folder"),
    ),
    CommandAction(
        id="open_windows_explorer",
        title="Open Windows Explorer",
        target_kind="app",
        target="explorer.exe",
        aliases=("open windows explorer", "open file explorer", "windows explorer"),
    ),
)


def normalize_command_text(text: str) -> str:
    normalized = (text or "").strip().casefold()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[.!?]+$", "", normalized)
    return normalized.strip()


def resolve_command_actions(text: str, actions=DEFAULT_COMMAND_ACTIONS):
    normalized = normalize_command_text(text)
    if not normalized:
        return []

    matches = []
    for action in actions:
        candidates = (action.title, *action.aliases)
        if any(normalize_command_text(candidate) == normalized for candidate in candidates):
            matches.append(action)
    return matches


def launch_command_action(action: CommandAction):
    if action.target_kind == "app":
        subprocess.Popen([action.target], shell=False)
        return

    os.startfile(action.target)


class CommandOverlayModel:
    def __init__(self, actions=DEFAULT_COMMAND_ACTIONS):
        self.actions = tuple(actions)
        self.visible = False
        self.phase = "hidden"
        self.input_armed = False
        self.input_text = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()

    def open(self):
        self.visible = True
        self.phase = "entry"
        self.input_armed = False
        self.input_text = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()

    def close(self):
        self.visible = False
        self.phase = "hidden"
        self.input_armed = False
        self.input_text = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()

    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.open()

    def append_text(self, char: str):
        if not self.visible or self.phase != "entry" or not self.input_armed or not char:
            return

        self.input_text += char
        self.status_kind = "idle"
        self.status_text = ""

    def set_input_text(self, text: str):
        if not self.visible or self.phase != "entry":
            return

        self.input_text = text or ""
        self.status_kind = "idle"
        self.status_text = ""
        self.pending_action = None
        self.pending_matches = ()

    def backspace(self):
        if not self.visible or self.phase != "entry" or not self.input_armed:
            return

        self.input_text = self.input_text[:-1]
        self.status_kind = "idle"
        self.status_text = ""

    def escape(self):
        if not self.visible:
            return "ignored"

        if self.phase == "confirm":
            self.phase = "entry"
            self.input_armed = True
            self.status_kind = "idle"
            self.status_text = ""
            self.pending_action = None
            self.pending_matches = ()
            return "confirm_cancelled"

        self.close()
        return "closed"

    def submit(self):
        if not self.visible:
            return ("ignored", None)

        if self.phase == "entry":
            if not self.input_armed:
                self.status_kind = "idle"
                self.status_text = "Click inside the command box to begin typing."
                return ("awaiting_click_arm", None)

            if not normalize_command_text(self.input_text):
                self.status_kind = "idle"
                self.status_text = ""
                return ("awaiting_input", None)

            self.last_request = self.input_text
            matches = tuple(resolve_command_actions(self.input_text, self.actions))
            self.pending_matches = matches

            if len(matches) == 1:
                self.phase = "confirm"
                self.input_armed = False
                self.pending_action = matches[0]
                self.status_kind = "ready"
                self.status_text = ""
                return ("confirm_ready", matches[0])

            self.pending_action = None
            if not matches:
                self.status_kind = "not_found"
                self.status_text = "No saved action or alias matched that request."
                return ("not_found", None)

            self.status_kind = "ambiguous"
            self.status_text = "Multiple saved actions matched that request."
            return ("ambiguous", matches)

        if self.phase == "confirm" and self.pending_action is not None:
            return ("execute_confirmed", self.pending_action)

        return ("ignored", None)

    def show_result(self, status_kind: str, status_text: str):
        self.phase = "result"
        self.input_armed = False
        self.status_kind = status_kind
        self.status_text = status_text

    def view_payload(self):
        action = self.pending_action
        return {
            "visible": self.visible,
            "phase": self.phase,
            "input_armed": self.input_armed,
            "input_text": self.input_text,
            "status_kind": self.status_kind,
            "status_text": self.status_text,
            "typed_request": self.last_request,
            "pending_action": None
            if action is None
            else {
                "id": action.id,
                "title": action.title,
                "target_kind": action.target_kind,
                "target": action.target,
            },
            "ambiguous_titles": [match.title for match in self.pending_matches] if self.status_kind == "ambiguous" else [],
        }
