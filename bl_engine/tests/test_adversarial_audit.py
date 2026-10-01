from stateful_author.adversarial import run_adversarial_audit


def test_adversarial_audit_catches_layer_specific_failures():
    report = run_adversarial_audit()
    expected = {
        "STAIR_STEP_ATTACK": "PARAGRAPH_FRAGMENTATION",
        "STORY_PROSE_LEAK_ATTACK": "SOURCE_BOUNDARY_LEAK:paragraph_topology",
        "MEMORY_BIOGRAPHY_ATTACK": "NARRATIVE_MODE_DRIFT",
        "GENERIC_PRIOR_ATTACK": "MODEL_PRIOR_REVERSION",
        "CLOSURE_STACK_ATTACK": "CLOSURE_STACKING",
        "SOURCE_RESIDUE_ATTACK": "SOURCE_RESIDUE",
        "SERIAL_CLIFFHANGER_ATTACK": "SERIAL_STAGNATION",
    }
    for attack, failure in expected.items():
        assert failure in report[attack]


def test_adversarial_audit_catches_rc3_intelligence_failures():
    report = run_adversarial_audit()
    expected = {
        'INTELLIGENCE_ALL_ON_ATTACK': 'INTELLIGENCE_OVERACTIVATION',
        'INTELLIGENCE_REVEAL_MUNDANE_ATTACK': 'INTELLIGENCE_OVERACTIVATION',
        'INTELLIGENCE_HUMOR_SURFACE_ATTACK': 'INTELLIGENCE_DIMENSION_LEAK:HUMOR_COGNITION:paragraph_topology',
        'INTELLIGENCE_MISDIRECTION_NO_VALUE_ATTACK': 'MISDIRECTION_WITHOUT_VALUE',
        'INTELLIGENCE_RECURRENCE_NO_RECODING_ATTACK': 'RECURRENCE_WITHOUT_RECODING',
        'INTELLIGENCE_LIBRARY_DUMP_ATTACK': 'INTELLIGENCE_PAYLOAD_BLOAT',
        'INTELLIGENCE_CHARACTER_GENERICITY_ATTACK': 'CHARACTER_GENERICITY',
    }
    for attack, failure in expected.items():
        assert failure in report[attack]
