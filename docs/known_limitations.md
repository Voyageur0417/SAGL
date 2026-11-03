# Known limitations

- The checkpoint is confirmed and executable but is not publicly deposited; its redistribution permission and a verified acquisition URL remain unresolved. Recipients without the exact model cannot reproduce the paper merely from this archive.
- Rights holders must select/confirm the SAGL-owned code licence before public redistribution. Third-party code notices are included separately and do not grant rights to benchmark imagery or weights.
- Historical feature values are not reproduced bit-for-bit. Crop/input and encoder-loading controls were run; the remaining discrepancy is not uniquely explained by one floating-point/backend factor.
- Four representative complete sequence/carrier cases (three underlying media sources) were freshly regenerated. All 155 development sequence/carrier key mappings were checked, but the other sequences were not freshly extracted or re-evaluated in this release task.
- Fresh features can change candidate retrieval, qualification order or prototype deduplication even when final links and predictions agree. Inspect the documented intermediate differences; final equivalence is sample-specific.
- A clean CPU-only environment passed cached full-sequence linking/evaluation and eight real-crop feature inference. The full-sequence single-thread CPU extraction attempt was stopped for runtime and is NOT counted as completed. A separate newly installed CUDA11.8 environment passed a complete real-sequence media-to-feature-to-prediction-to-evaluation test.
- Other operating systems and GPU architectures were not tested. Keep the published sequence order, FPS, crop layout/batch profiles, and TeamTrack missing-area behavior.
- Official hidden-test HOTA is an external result; this package does not contain official test GT or reproduce server scores locally.
- Benchmark media, real carrier outputs, caches, GT mappings and predictions are not bundled without permission. Synthetic examples are format checks only.
