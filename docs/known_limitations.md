# Known limitations

- The original checkpoint is a separate v1.0.0 Release attachment. Dataset media and exact carrier inputs remain external requirements; code and weights alone do not supply those assets.
- Public publication was authorised by the maintainer. No project-wide software/model reuse licence was selected; do not infer unrestricted reuse from availability or from the MIT licences of third-party implementations.
- Historical feature values are not reproduced bit-for-bit. Crop/input and encoder-loading controls were run; the remaining discrepancy is not uniquely explained by one floating-point/backend factor.
- Four representative complete sequence/carrier cases (three underlying media sources) were freshly regenerated. All 155 development sequence/carrier key mappings were checked, but the other sequences were not freshly extracted or re-evaluated in this release task.
- Fresh features can change candidate retrieval, qualification order or prototype deduplication even when final links and predictions agree. Inspect the documented intermediate differences; final equivalence is sample-specific.
- A clean CPU-only environment passed cached full-sequence linking/evaluation and eight real-crop feature inference. The full-sequence single-thread CPU extraction attempt was stopped for runtime and is NOT counted as completed. A separate newly installed CUDA11.8 environment passed a complete real-sequence media-to-feature-to-prediction-to-evaluation test.
- Other operating systems and GPU architectures were not tested. Keep the published sequence order, FPS, crop layout/batch profiles, and TeamTrack missing-area behavior.
- Official hidden-test HOTA is an external result; this package does not contain official test GT or reproduce server scores locally.
- Benchmark media, real carrier outputs, caches, GT mappings and predictions are not bundled without permission. Synthetic examples are format checks only.
