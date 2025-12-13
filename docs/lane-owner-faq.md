# Lane owner FAQ

## Why does the control plane keep both machine summaries and human briefs?

Because release work crosses shifts and teams. A packet should be reproducible by code and readable by people.

## Why do lane names stay specific instead of collapsing into one generic imaging status?

Because the release decision is usually lane-local. A codec lane, a tile lane, and a partner-export lane fail for different reasons.

## Why is manifest drift treated seriously even when the image looks fine?

Because downstream consumers often depend on filenames, packet contents, metadata, and stable digests just as much as the visual output.

## Why are warnings preserved instead of hidden after a release moves forward?

Because the next incident often starts with a warning pattern the team ignored last week.
