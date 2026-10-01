_FORBIDDEN = {
    'HUMOR_COGNITION': {'paragraph_topology', 'pov_distance', 'story_causality'},
    'STORY_ARCHITECTURE': {'paragraph_topology', 'lexical_register', 'narrator_voice', 'abstraction_band', 'pov_distance'},
    'BASE_PROSE': set(),
}


def validate_overlay(layer: str, changes: dict) -> list[str]:
    forbidden = _FORBIDDEN.get(layer, set())
    return [f'SOURCE_BOUNDARY_LEAK:{key}' for key in changes if key in forbidden]
