# Feature extraction

Use scripts/extract_features.py --config CONFIG --device cuda:0 --output NEW_DIRECTORY. The configuration specifies a dataset profile, carrier root, exact model path/checksum, sequence names/FPS and JPEG directories or video paths. --checkpoint PATH overrides only the location. The output directory must not already exist.

Preprocessing, cache ordering, batch layout and dataset-specific missing-crop behavior are defined in feature_cache_format.md. JPEG input is read by OpenCV; bbox tlwh uses floor/ceil-and-clip cropping, BGR-to-RGB conversion and INTER_LINEAR resize(W128,H256). ImageNet-normalized float32 tensors are evaluated without AMP; normalized512-D embeddings are stored as float16. Downstream operations cast to float32 without observation-wise renormalization.

observation_manifest.json records every original carrier row and its feature index, including null for ineligible observations. It records the actual crop bounds/status. Missing-image/invalid-crop fallbacks are recorded, not silently interpreted as successful crops. No GT or training identity mapping is an input.

A complete representative fresh-feature sequence has been validated on GPU. CPU loading/real-crop inference is supported, but full fresh-feature CPU sequence completion is not claimed. Keep the original batch defaults and inspect all extraction-manifest counts.
