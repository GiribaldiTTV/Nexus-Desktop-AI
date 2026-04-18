import os
from dataclasses import dataclass

from .shared_action_model import (
    CommandAction,
    CommandActionCatalog,
    CommandGroup,
    DEFAULT_COMMAND_ACTION_CATALOG,
    build_default_command_action_catalog,
    format_action_origin_label,
    reload_default_command_action_catalog,
)


@dataclass(frozen=True)
class CommandExecutionIntent:
    execution_type: str
    action: CommandAction
    group: CommandGroup | None = None

    @property
    def action_id(self) -> str:
        return self.action.id

    @property
    def group_id(self) -> str:
        return "" if self.group is None else self.group.id

    @property
    def resolved_member_action_ids(self) -> tuple[str, ...]:
        return () if self.group is None else self.group.member_action_ids

    @property
    def resolved_member_actions(self) -> tuple[CommandAction, ...]:
        return () if self.group is None else self.group.member_actions


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
        self.pending_group = None
        self.pending_execution_intent = None

    def _clear_execution_intent(self):
        self.pending_execution_intent = None

    def _consume_execution_intent(self):
        intent = self.pending_execution_intent
        self.pending_execution_intent = None
        return intent

    def _bind_execution_intent(self, action: CommandAction):
        if self.pending_group is not None:
            self.pending_execution_intent = CommandExecutionIntent(
                execution_type="group",
                action=action,
                group=self.pending_group,
            )
            return
        self.pending_execution_intent = CommandExecutionIntent(
            execution_type="single",
            action=action,
        )

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
        self.pending_group = None
        self._clear_execution_intent()

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
        self.pending_group = None
        self._clear_execution_intent()

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
        self.pending_group = None
        self._clear_execution_intent()

    def set_input_text(self, text: str):
        if not self.visible or self.phase != "entry":
            return

        self.input_text = text or ""
        self.last_request = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.pending_action = None
        self.pending_matches = ()
        self.pending_group = None
        self._clear_execution_intent()

    def set_entry_feedback(self, status_kind: str, status_text: str):
        if not self.visible or self.phase != "entry":
            return

        self.status_kind = status_kind or "idle"
        self.status_text = status_text or ""
        self.last_request = ""
        self.pending_action = None
        self.pending_matches = ()
        self.pending_group = None
        self._clear_execution_intent()

    def set_action_catalog(self, action_catalog: CommandActionCatalog):
        self.action_catalog = action_catalog
        self.actions = tuple(action_catalog.actions)

    def reload_action_catalog(self, source_path: str | os.PathLike[str] | None = None):
        action_catalog = (
            reload_default_command_action_catalog()
            if source_path is None
            else build_default_command_action_catalog(source_path)
        )
        self.set_action_catalog(action_catalog)
        return action_catalog

    def backspace(self):
        if not self.visible or self.phase != "entry" or not self.input_armed:
            return

        self.input_text = self.input_text[:-1]
        self.last_request = ""
        self.status_kind = "idle"
        self.status_text = ""
        self.pending_group = None
        self._clear_execution_intent()

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
            self.pending_group = None
            self._clear_execution_intent()
            return "choice_cancelled"

        if self.phase == "confirm":
            self.phase = "entry"
            self.input_armed = True
            self.last_request = ""
            self.status_kind = "idle"
            self.status_text = ""
            self.pending_action = None
            self.pending_matches = ()
            self.pending_group = None
            self._clear_execution_intent()
            return "confirm_cancelled"

        self.close()
        return "closed"

    def submit(self):
        if not self.visible:
            return ("ignored", None)

        if self.phase == "entry":
            if not self.input_armed:
                self.status_kind = "idle"
                self.status_text = "Type an action or alias to begin."
                return ("awaiting_click_arm", None)

            if not self.action_catalog.normalize_text(self.input_text):
                self.status_kind = "idle"
                self.status_text = ""
                return ("awaiting_input", None)

            self.last_request = self.input_text
            matched_group = self.action_catalog.resolve_group(self.input_text)
            if matched_group is not None:
                self.phase = "choose"
                self.input_armed = False
                self.pending_group = matched_group
                self.pending_matches = matched_group.member_actions
                self.pending_action = None
                self._clear_execution_intent()
                self.status_kind = "ambiguous"
                self.status_text = "Choose a member from the matched group."
                return ("ambiguous", matched_group.member_actions)

            matches = self.action_catalog.resolve_actions(self.input_text)
            self.pending_matches = matches
            self.pending_group = None

            if len(matches) == 1:
                self.phase = "confirm"
                self.input_armed = False
                self.pending_action = matches[0]
                self._bind_execution_intent(matches[0])
                self.status_kind = "ready"
                self.status_text = ""
                return ("confirm_ready", matches[0])

            self.pending_action = None
            self._clear_execution_intent()
            if not matches:
                self.status_kind = "not_found"
                self.status_text = "No action or alias matched that request."
                return ("not_found", None)

            self.phase = "choose"
            self.input_armed = False
            self.status_kind = "ambiguous"
            self.status_text = "Press a number key or click the intended action below."
            return ("ambiguous", matches)

        if self.phase == "confirm":
            intent = self._consume_execution_intent()
            if intent is not None:
                return ("execute_confirmed", intent)
            return ("ignored", None)

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
        self._bind_execution_intent(action)
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
        self.pending_group = None
        self._clear_execution_intent()

    def _serialize_action(self, action, *, index: int | None = None):
        if action is None:
            return None

        payload = {
            "id": action.id,
            "title": action.title,
            "origin": action.origin,
            "origin_label": format_action_origin_label(action.origin),
            "target_kind": action.target_kind,
            "target": action.target,
            "target_display": self.action_catalog.format_target_display(
                action.target_kind,
                action.target,
            ),
        }
        if index is not None:
            payload["index"] = index
        return payload

    def _serialize_group(self, group):
        if group is None:
            return None

        return {
            "id": group.id,
            "title": group.title,
            "aliases": list(group.aliases),
            "member_count": len(group.member_actions),
            "member_action_ids": list(group.member_action_ids),
        }

    def view_payload(self):
        action = self.pending_action
        saved_action_inventory = self.action_catalog.saved_action_inventory
        saved_group_inventory = self.action_catalog.saved_group_inventory
        return {
            "visible": self.visible,
            "phase": self.phase,
            "input_armed": self.input_armed,
            "input_text": self.input_text,
            "status_kind": self.status_kind,
            "status_text": self.status_text,
            "typed_request": self.last_request,
            "pending_action": self._serialize_action(action),
            "pending_group": self._serialize_group(self.pending_group),
            "selection_context": (
                "group"
                if self.pending_group is not None and self.phase in {"choose", "confirm"}
                else "ambiguity"
                if self.phase == "choose"
                else ""
            ),
            "ambiguous_titles": [match.title for match in self.pending_matches] if self.status_kind == "ambiguous" else [],
            "ambiguous_matches": [
                self._serialize_action(match, index=index)
                for index, match in enumerate(self.pending_matches)
            ]
            if self.status_kind == "ambiguous"
            else [],
            "saved_action_inventory": {
                "visible": saved_action_inventory.visible,
                "status_kind": saved_action_inventory.status_kind,
                "status_text": saved_action_inventory.status_text,
                "guidance_text": saved_action_inventory.guidance_text,
                "path": saved_action_inventory.path,
                "path_display": self.action_catalog.format_target_display(
                    "file",
                    saved_action_inventory.path,
                )
                if saved_action_inventory.path
                else "",
                "count": len(saved_action_inventory.actions),
                "items": [
                    self._serialize_action(saved_action)
                    for saved_action in saved_action_inventory.actions
                ],
            },
            "saved_group_inventory": {
                "visible": saved_group_inventory.visible,
                "status_kind": saved_group_inventory.status_kind,
                "status_text": saved_group_inventory.status_text,
                "guidance_text": saved_group_inventory.guidance_text,
                "path": saved_group_inventory.path,
                "path_display": self.action_catalog.format_target_display(
                    "file",
                    saved_group_inventory.path,
                )
                if saved_group_inventory.path
                else "",
                "count": len(saved_group_inventory.groups),
                "items": [
                    {
                        "id": group.id,
                        "title": group.title,
                        "aliases": list(group.aliases),
                        "member_action_ids": list(group.member_action_ids),
                        "member_count": len(group.member_actions),
                    }
                    for group in saved_group_inventory.groups
                ],
            },
        }
