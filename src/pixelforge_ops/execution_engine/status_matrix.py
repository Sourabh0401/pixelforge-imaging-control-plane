from __future__ import annotations

STATUS_MATRIX = [{'status': 'pass',
  'operator_action': 'review',
  'counts_toward_score': True,
  'counts_toward_runtime': True,
  'severity': 'low',
  'notes': 'Status pass determines score inclusion, operator routing, and replay messaging.'},
 {'status': 'fail',
  'operator_action': 'rerun',
  'counts_toward_score': False,
  'counts_toward_runtime': True,
  'severity': 'medium',
  'notes': 'Status fail determines score inclusion, operator routing, and replay messaging.'},
 {'status': 'timeout',
  'operator_action': 'escalate',
  'counts_toward_score': False,
  'counts_toward_runtime': True,
  'severity': 'high',
  'notes': 'Status timeout determines score inclusion, operator routing, and replay '
           'messaging.'},
 {'status': 'error',
  'operator_action': 'none',
  'counts_toward_score': False,
  'counts_toward_runtime': True,
  'severity': 'info',
  'notes': 'Status error determines score inclusion, operator routing, and replay messaging.'},
 {'status': 'missing',
  'operator_action': 'review',
  'counts_toward_score': False,
  'counts_toward_runtime': False,
  'severity': 'low',
  'notes': 'Status missing determines score inclusion, operator routing, and replay '
           'messaging.'},
 {'status': 'late-pass',
  'operator_action': 'rerun',
  'counts_toward_score': True,
  'counts_toward_runtime': True,
  'severity': 'medium',
  'notes': 'Status late-pass determines score inclusion, operator routing, and replay '
           'messaging.'},
 {'status': 'late-fail',
  'operator_action': 'escalate',
  'counts_toward_score': False,
  'counts_toward_runtime': True,
  'severity': 'high',
  'notes': 'Status late-fail determines score inclusion, operator routing, and replay '
           'messaging.'}]

def status_definition(status: str) -> dict[str, object]:
    for row in STATUS_MATRIX:
        if row["status"] == status:
            return dict(row)
    raise KeyError(status)


def counts_toward_score(status: str) -> bool:
    return bool(status_definition(status)["counts_toward_score"])


def operator_action(status: str) -> str:
    return str(status_definition(status)["operator_action"])
