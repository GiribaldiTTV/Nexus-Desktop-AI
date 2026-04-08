from .shared_action_model import (
    CommandActionCatalog,
    DEFAULT_COMMAND_ACTION_CATALOG,
)


class CommandOverlayModel:
    def __init__(self, actions=None, action_catalog: CommandActionCatalog | None = None):
        if action_catalog is None:
            action_catalog = (
                DEFAULT_COMMAND_ACTION_CATALOG
                if actions is None
                else CommandActionCatalog(actions)
            )

        self.action_catalog = action_catalog
        self.actions = tuple(action_catalog.actions)
        self.visible = False
        self.phase = "hidden"
        self.input_armed = False
        self.input_text = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()

    def open(self, *, arm_input: bool = False):
        self.visible = True
        self.phase = "entry"
        self.input_armed = bool(arm_input)
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
        self.last_request = ""
        self.status_kind = "idle"
        self.status_text = ""

    def set_input_text(self, text: str):
        if not self.visible or self.phase != "entry":
            return

        self.input_text = text or ""
        self.last_request = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.pending_action = None
        self.pending_matches = ()

    def backspace(self):
        if not self.visible or self.phase != "entry" or not self.input_armed:
            return

        self.input_text = self.input_text[:-1]
        self.last_request = ""
        self.status_kind = "idle"
        self.status_text = ""

    def escape(self):
        if not self.visible:
            return "ignored"

        if self.phase == "choose":
            self.phase = "entry"
            self.input_armed = True
            self.last_request = ""
            self.status_kind = "idle"
            self.status_text = ""
            self.pending_action = None
            self.pending_matches = ()
            return "choice_cancelled"

        if self.phase == "confirm":
            self.phase = "entry"
            self.input_armed = True
            self.last_request = ""
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
                self.status_text = "Type a saved action or alias to begin."
                return ("awaiting_click_arm", None)

            if not self.action_catalog.normalize_text(self.input_text):
                self.status_kind = "idle"
                self.status_text = ""
                return ("awaiting_input", None)

            self.last_request = self.input_text
            matches = self.action_catalog.resolve_actions(self.input_text)
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

            self.phase = "choose"
            self.input_armed = False
            self.status_kind = "ambiguous"
            self.status_text = "Press a number key or click the intended action below."
            return ("ambiguous", matches)

        if self.phase == "confirm" and self.pending_action is not None:
            return ("execute_confirmed", self.pending_action)

        return ("ignored", None)

    def choose_match(self, index: int):
        if not self.visible or self.phase != "choose":
            return ("ignored", None)

        if index < 0 or index >= len(self.pending_matches):
            return ("ignored", None)

        action = self.pending_matches[index]
        self.phase = "confirm"
        self.input_armed = False
        self.pending_action = action
        self.status_kind = "ready"
        self.status_text = ""
        return ("confirm_ready", action)

    def show_result(self, status_kind: str, status_text: str):
        self.phase = "result"
        self.input_armed = False
        self.input_text = ""
        self.status_kind = status_kind
        self.status_text = status_text
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()

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
                "target_display": self.action_catalog.format_target_display(
                    action.target_kind,
                    action.target,
                ),
            },
            "ambiguous_titles": [match.title for match in self.pending_matches] if self.status_kind == "ambiguous" else [],
            "ambiguous_matches": [
                {
                    "index": index,
                    "id": match.id,
                    "title": match.title,
                    "target_kind": match.target_kind,
                    "target": match.target,
                    "target_display": self.action_catalog.format_target_display(
                        match.target_kind,
                        match.target,
                    ),
                }
                for index, match in enumerate(self.pending_matches)
            ]
            if self.status_kind == "ambiguous"
            else [],
        }
