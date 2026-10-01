from stateful_author.packet import compile_writer_packet


def test_packet_allows_only_compact_author_intelligence_payloads():
    packet = compile_writer_packet({
        'event': {'action': 'refuse'},
        'author_intelligence': [
            {'id': 'DIALOGUE_AS_RELATIONAL_ACTION', 'guidance': ['Let the refusal alter status.']}
        ],
    })
    assert packet['author_intelligence'] == [
        {'id': 'DIALOGUE_AS_RELATIONAL_ACTION', 'guidance': ['Let the refusal alter status.']}
    ]


def test_packet_strips_full_manifest_fields_recursively():
    packet = compile_writer_packet({
        'author_intelligence': [{
            'id': 'HUMOR_COGNITION',
            'guidance': ['Keep humor character-owned.'],
            'trigger': {'any': ['humor_opportunity']},
            'owns_dimensions': ['comparison_choice'],
            'forbidden_dimensions': ['paragraph_topology'],
            'verifier_checks': ['INTELLIGENCE_DIMENSION_LEAK'],
        }]
    })
    assert packet['author_intelligence'] == [
        {'id': 'HUMOR_COGNITION', 'guidance': ['Keep humor character-owned.']}
    ]


def test_packet_strips_source_and_verifier_meta_keys():
    packet = compile_writer_packet({
        'author_intelligence': [{
            'id': 'REVEAL_CAUSAL_ACCOUNTING',
            'guidance': ['Preserve prior plausibility.'],
            'source_author': 'DO_NOT_LEAK',
            'source_excerpt': 'DO_NOT_LEAK_EITHER',
            'failure_history': ['MODEL_PRIOR_REVERSION'],
        }]
    })
    flat = repr(packet)
    assert 'DO_NOT_LEAK' not in flat
    assert 'MODEL_PRIOR_REVERSION' not in flat


def test_packet_bounds_guidance_per_card():
    packet = compile_writer_packet({
        'author_intelligence': [{'id': 'X', 'guidance': [str(i) for i in range(20)]}]
    })
    assert len(packet['author_intelligence'][0]['guidance']) <= 4


def test_full_library_dump_without_guidance_is_removed():
    packet = compile_writer_packet({
        'author_intelligence': [{
            'id': 'REVEAL_CAUSAL_ACCOUNTING',
            'purpose': 'full manifest',
            'trigger': {'any': ['reveal']},
            'context_requirements': {'required': []},
        }]
    })
    assert packet.get('author_intelligence', []) == []
