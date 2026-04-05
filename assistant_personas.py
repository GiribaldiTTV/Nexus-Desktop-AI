from dataclasses import dataclass


@dataclass(frozen=True)
class PersonaConfig:
    persona_id: str
    display_name: str
    expanded_name: str
    voice_id: str
    error_voice_id: str
    ui_title_text: str


PERSONA_REGISTRY = {
    "orin": PersonaConfig(
        persona_id="orin",
        display_name="ORIN",
        expanded_name="Operational Response and Intelligence Nexus",
        voice_id="en-GB-RyanNeural",
        error_voice_id="en-GB-RyanNeural",
        ui_title_text="ORIN",
    ),
    "aria": PersonaConfig(
        persona_id="aria",
        display_name="ARIA",
        expanded_name="Adaptive Runtime Intelligence Assistant",
        voice_id="en-US-AriaNeural",
        error_voice_id="en-US-AriaNeural",
        ui_title_text="ARIA",
    ),
}

# Pre-Beta and Beta ship ORIN only. ARIA stays dormant until a later
# explicitly approved persona-selection slice.
RELEASED_PERSONA_IDS = ("orin",)
DEFAULT_PERSONA_ID = "orin"


def get_persona_config(persona_id: str = DEFAULT_PERSONA_ID) -> PersonaConfig:
    normalized = (persona_id or DEFAULT_PERSONA_ID).strip().lower()
    if normalized not in PERSONA_REGISTRY:
        normalized = DEFAULT_PERSONA_ID
    return PERSONA_REGISTRY[normalized]


def get_released_persona_config(persona_id: str = DEFAULT_PERSONA_ID) -> PersonaConfig:
    normalized = (persona_id or DEFAULT_PERSONA_ID).strip().lower()
    if normalized not in RELEASED_PERSONA_IDS:
        normalized = DEFAULT_PERSONA_ID
    return get_persona_config(normalized)

