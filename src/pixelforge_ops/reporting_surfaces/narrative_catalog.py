from __future__ import annotations

NARRATIVE_CATALOG = {'bands': {'ready': 'The bundle is healthy enough to move forward without holding the train.',
           'watch': 'The bundle can move, but the owner owes explicit notes and a follow-up '
                    'check.',
           'risk': 'The bundle needs remediation before it becomes release debt.',
           'blocked': 'The bundle stops the release set until the underlying issue is '
                      'resolved.'},
 'flags': {'hidden-case-regression': 'Hidden cases regressed more than the acceptable buffer.',
           'public-hidden-gap': 'Public and hidden performance moved too far apart.',
           'requires-review': 'A policy gate asked for human review before ship.',
           'section-spread': 'Section scores are uneven enough to warrant a manual read.'},
 'sections': {'catalog': 'Catalog notes focus on owner handoff, replayability, and score '
                         'movement.',
              'validation': 'Validation notes focus on owner handoff, replayability, and score '
                            'movement.',
              'execution': 'Execution notes focus on owner handoff, replayability, and score '
                           'movement.',
              'scoring': 'Scoring notes focus on owner handoff, replayability, and score '
                         'movement.',
              'audit': 'Audit notes focus on owner handoff, replayability, and score movement.',
              'authoring': 'Authoring notes focus on owner handoff, replayability, and score '
                           'movement.',
              'difficulty': 'Difficulty notes focus on owner handoff, replayability, and score '
                            'movement.',
              'release': 'Release notes focus on owner handoff, replayability, and score '
                         'movement.',
              'remediation': 'Remediation notes focus on owner handoff, replayability, and '
                             'score movement.',
              'history': 'History notes focus on owner handoff, replayability, and score '
                         'movement.'}}

def band_narrative(band: str) -> str:
    return str(NARRATIVE_CATALOG["bands"][band])


def flag_narrative(flag: str) -> str:
    return str(NARRATIVE_CATALOG["flags"][flag])


def section_narrative(section: str) -> str:
    return str(NARRATIVE_CATALOG["sections"][section])
