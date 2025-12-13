# Packet digest troubleshooting

Digest drift is one of the fastest ways to learn that the lane contract moved. Use this checklist when a packet digest changes unexpectedly.

## Check order

1. confirm the bundle id and lane name
2. compare artifact lists
3. compare metadata payloads
4. check added or removed files
5. confirm whether ordering changed in a tile or atlas lane
6. read the operator brief for any approved exception or intentional contract note

## Common causes

- required codec disappeared
- sidecar changed name
- metadata field changed value or ordering
- artifact lineage changed across accepted manifests
- tile set or order changed

## Safe workflow

Do not rewrite the old packet. Build a new packet, diff it, and preserve both digests in the investigation notes.
