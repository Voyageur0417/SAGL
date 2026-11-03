# Release scope

Included: the frozen SAGL inference pipeline; OSNet feature extraction and explicit observation mapping; input profiles; ID-only checks; standard TrackEval snapshot; comparison utilities; unit tests and a synthetic format example.

Not included: a one-command reproduction of every paper table, all ablation runners, GTA/AFLink dependencies/models, original detection/tracker pipelines, training code or benchmark assets. The original ablation/external scripts exist at the archived experiment commit but use author-local preflight/configuration paths and third-party assets. They were inspected rather than copied into an apparently portable experiments/ directory. Their licence/asset dependencies require separate preparation. Excluding those runners changes no paper result.

Source distribution remains pending project-code licence approval. The model remains an external permission-controlled requirement; public data access remains subject to provider terms.
