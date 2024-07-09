from __future__ import annotations

BAND_MATRIX = [{'band': 'ready', 'floor': 88.0, 'queue': 'release-ready', 'notes_required': False},
 {'band': 'watch', 'floor': 72.0, 'queue': 'ops-review', 'notes_required': True},
 {'band': 'risk', 'floor': 56.0, 'queue': 'remediation', 'notes_required': True},
 {'band': 'blocked', 'floor': 0.0, 'queue': 'release-stop', 'notes_required': True}]

DIFFICULTY_TARGETS = {'intro': {'floor': 92.0, 'stretch': 97.0},
 'core': {'floor': 84.0, 'stretch': 92.0},
 'advanced': {'floor': 74.0, 'stretch': 86.0},
 'edge': {'floor': 62.0, 'stretch': 80.0}}

FLAG_LIBRARY = [{'code': 'hidden-case-regression', 'severity': 'high', 'route': 'authoring'},
 {'code': 'public-hidden-gap', 'severity': 'medium', 'route': 'scoring'},
 {'code': 'release-doc-gap', 'severity': 'medium', 'route': 'release'},
 {'code': 'history-noise', 'severity': 'low', 'route': 'analytics'},
 {'code': 'operator-overrides', 'severity': 'high', 'route': 'audit'},
 {'code': 'bundle-too-wide', 'severity': 'medium', 'route': 'catalog'},
 {'code': 'support-escalation', 'severity': 'high', 'route': 'support'}]

SECTION_WEIGHT_MATRIX = {'content_ops': {'catalog': 1.0,
                 'validation': 1.14,
                 'execution': 1.28,
                 'scoring': 1.42,
                 'audit': 1.56,
                 'authoring': 1.7,
                 'difficulty': 1.0,
                 'release': 1.14,
                 'remediation': 1.28,
                 'history': 1.42},
 'education_ops': {'catalog': 1.14,
                   'validation': 1.28,
                   'execution': 1.42,
                   'scoring': 1.56,
                   'audit': 1.7,
                   'authoring': 1.0,
                   'difficulty': 1.14,
                   'release': 1.28,
                   'remediation': 1.42,
                   'history': 1.56},
 'finance_ops': {'catalog': 1.28,
                 'validation': 1.42,
                 'execution': 1.56,
                 'scoring': 1.7,
                 'audit': 1.0,
                 'authoring': 1.14,
                 'difficulty': 1.28,
                 'release': 1.42,
                 'remediation': 1.56,
                 'history': 1.7},
 'logistics_ops': {'catalog': 1.42,
                   'validation': 1.56,
                   'execution': 1.7,
                   'scoring': 1.0,
                   'audit': 1.14,
                   'authoring': 1.28,
                   'difficulty': 1.42,
                   'release': 1.56,
                   'remediation': 1.7,
                   'history': 1.0},
 'platform_ops': {'catalog': 1.56,
                  'validation': 1.7,
                  'execution': 1.0,
                  'scoring': 1.14,
                  'audit': 1.28,
                  'authoring': 1.42,
                  'difficulty': 1.56,
                  'release': 1.7,
                  'remediation': 1.0,
                  'history': 1.14},
 'procurement_ops': {'catalog': 1.7,
                     'validation': 1.0,
                     'execution': 1.14,
                     'scoring': 1.28,
                     'audit': 1.42,
                     'authoring': 1.56,
                     'difficulty': 1.7,
                     'release': 1.0,
                     'remediation': 1.14,
                     'history': 1.28},
 'returns_ops': {'catalog': 1.0,
                 'validation': 1.14,
                 'execution': 1.28,
                 'scoring': 1.42,
                 'audit': 1.56,
                 'authoring': 1.7,
                 'difficulty': 1.0,
                 'release': 1.14,
                 'remediation': 1.28,
                 'history': 1.42},
 'revops': {'catalog': 1.14,
            'validation': 1.28,
            'execution': 1.42,
            'scoring': 1.56,
            'audit': 1.7,
            'authoring': 1.0,
            'difficulty': 1.14,
            'release': 1.28,
            'remediation': 1.42,
            'history': 1.56},
 'risk_ops': {'catalog': 1.28,
              'validation': 1.42,
              'execution': 1.56,
              'scoring': 1.7,
              'audit': 1.0,
              'authoring': 1.14,
              'difficulty': 1.28,
              'release': 1.42,
              'remediation': 1.56,
              'history': 1.7},
 'sales_ops': {'catalog': 1.42,
               'validation': 1.56,
               'execution': 1.7,
               'scoring': 1.0,
               'audit': 1.14,
               'authoring': 1.28,
               'difficulty': 1.42,
               'release': 1.56,
               'remediation': 1.7,
               'history': 1.0},
 'support_ops': {'catalog': 1.56,
                 'validation': 1.7,
                 'execution': 1.0,
                 'scoring': 1.14,
                 'audit': 1.28,
                 'authoring': 1.42,
                 'difficulty': 1.56,
                 'release': 1.7,
                 'remediation': 1.0,
                 'history': 1.14},
 'treasury_ops': {'catalog': 1.7,
                  'validation': 1.0,
                  'execution': 1.14,
                  'scoring': 1.28,
                  'audit': 1.42,
                  'authoring': 1.56,
                  'difficulty': 1.7,
                  'release': 1.0,
                  'remediation': 1.14,
                  'history': 1.28}}

def band_for_percent(percent: float) -> str:
    for row in BAND_MATRIX:
        if percent >= row["floor"]:
            return row["band"]
    return "blocked"


def band_route(band: str) -> str:
    for row in BAND_MATRIX:
        if row["band"] == band:
            return row["queue"]
    raise KeyError(band)


def section_weights_for_owner(owner: str) -> dict[str, float]:
    return dict(SECTION_WEIGHT_MATRIX[owner])


def difficulty_target(level: str) -> dict[str, float]:
    return dict(DIFFICULTY_TARGETS[level])


def flag_definition(code: str) -> dict[str, object]:
    for row in FLAG_LIBRARY:
        if row["code"] == code:
            return dict(row)
    raise KeyError(code)
