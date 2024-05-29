from __future__ import annotations

RELEASE_PROFILES = [{'profile_id': 'profile-01',
  'bundle_id': 'merchant-closeout',
  'channels': ['internal', 'rehearsal', 'pilot'],
  'owner': 'education_ops',
  'score_floor': 73,
  'hidden_floor': 61,
  'max_public_hidden_gap': 19,
  'notes': 'Release profile for merchant-closeout controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-02',
  'bundle_id': 'warehouse-routing',
  'channels': ['internal', 'rehearsal', 'pilot', 'partner'],
  'owner': 'finance_ops',
  'score_floor': 74,
  'hidden_floor': 62,
  'max_public_hidden_gap': 20,
  'notes': 'Release profile for warehouse-routing controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-03',
  'bundle_id': 'claims-intake',
  'channels': ['internal', 'rehearsal'],
  'owner': 'logistics_ops',
  'score_floor': 75,
  'hidden_floor': 63,
  'max_public_hidden_gap': 21,
  'notes': 'Release profile for claims-intake controls minimum score floors and hidden/public '
           'spread.'},
 {'profile_id': 'profile-04',
  'bundle_id': 'reserve-rollforward',
  'channels': ['internal', 'rehearsal', 'pilot'],
  'owner': 'platform_ops',
  'score_floor': 76,
  'hidden_floor': 64,
  'max_public_hidden_gap': 22,
  'notes': 'Release profile for reserve-rollforward controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-05',
  'bundle_id': 'identity-refresh',
  'channels': ['internal', 'rehearsal', 'pilot', 'partner'],
  'owner': 'procurement_ops',
  'score_floor': 77,
  'hidden_floor': 65,
  'max_public_hidden_gap': 23,
  'notes': 'Release profile for identity-refresh controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-06',
  'bundle_id': 'subscriber-billing',
  'channels': ['internal', 'rehearsal'],
  'owner': 'returns_ops',
  'score_floor': 78,
  'hidden_floor': 66,
  'max_public_hidden_gap': 24,
  'notes': 'Release profile for subscriber-billing controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-07',
  'bundle_id': 'seat-allocation',
  'channels': ['internal', 'rehearsal', 'pilot'],
  'owner': 'revops',
  'score_floor': 79,
  'hidden_floor': 67,
  'max_public_hidden_gap': 18,
  'notes': 'Release profile for seat-allocation controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-08',
  'bundle_id': 'fulfillment-ledger',
  'channels': ['internal', 'rehearsal', 'pilot', 'partner'],
  'owner': 'risk_ops',
  'score_floor': 80,
  'hidden_floor': 68,
  'max_public_hidden_gap': 19,
  'notes': 'Release profile for fulfillment-ledger controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-09',
  'bundle_id': 'document-classifier',
  'channels': ['internal', 'rehearsal'],
  'owner': 'sales_ops',
  'score_floor': 81,
  'hidden_floor': 69,
  'max_public_hidden_gap': 20,
  'notes': 'Release profile for document-classifier controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-10',
  'bundle_id': 'vendor-settlement',
  'channels': ['internal', 'rehearsal', 'pilot'],
  'owner': 'support_ops',
  'score_floor': 82,
  'hidden_floor': 70,
  'max_public_hidden_gap': 21,
  'notes': 'Release profile for vendor-settlement controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-11',
  'bundle_id': 'pricing-handoff',
  'channels': ['internal', 'rehearsal', 'pilot', 'partner'],
  'owner': 'treasury_ops',
  'score_floor': 83,
  'hidden_floor': 71,
  'max_public_hidden_gap': 22,
  'notes': 'Release profile for pricing-handoff controls minimum score floors and '
           'hidden/public spread.'},
 {'profile_id': 'profile-12',
  'bundle_id': 'returns-recovery',
  'channels': ['internal', 'rehearsal'],
  'owner': 'content_ops',
  'score_floor': 84,
  'hidden_floor': 72,
  'max_public_hidden_gap': 23,
  'notes': 'Release profile for returns-recovery controls minimum score floors and '
           'hidden/public spread.'}]

def profile_for_bundle(bundle_id: str) -> dict[str, object]:
    for row in RELEASE_PROFILES:
        if row["bundle_id"] == bundle_id:
            return dict(row)
    raise KeyError(bundle_id)


def channels_for_bundle(bundle_id: str) -> list[str]:
    return list(profile_for_bundle(bundle_id)["channels"])


def score_floor(bundle_id: str) -> float:
    return float(profile_for_bundle(bundle_id)["score_floor"])
