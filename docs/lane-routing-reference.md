# Lane routing reference

Use this reference when a packet needs a fast routing decision.

- codec and quantization problems: codec owners first, release owners second
- color and histogram drift: color owners first, release owners if the gate already blocked
- alpha halos and premultiplication: alpha owners first
- tile coverage and atlas structure: raster or sprite owners first
- metadata, ICC, or EXIF issues: metadata owners first, partner owners when an external packet is involved
- manifest or digest drift: release owners first
- partner file or delivery failures: partner owners first, support owners if a live incident is active

Routing should stay visible in the operator brief so the next shift does not have to guess.
