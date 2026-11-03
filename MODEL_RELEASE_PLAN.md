# Sports-ReID model release

The repository maintainer authorised public publication of the exact original model in release v1.0.0. No model is committed to source history. No new checkpoint is trained or substituted.

- Model: Sports-ReID OSNet-x1.0;512-dimensional embeddings.
- Provenance: ImageNet initialization; SportsMOT train-only; fixed epoch60, seed42.
- Input: RGB crop width128, height256, ImageNet mean/std, float32 inference.
- Original filename: clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
- Size:30,535,806 bytes.
- Original SHA256: `0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9`.
- Release: https://github.com/Voyageur0417/SAGL/releases/tag/v1.0.0
- Download: https://github.com/Voyageur0417/SAGL/releases/download/v1.0.0/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth

The original checkpoint retains classifier, optimizer and scheduler state. Content inspection found no embedded private path/credential strings or original media. It loads successfully with strict original state shapes. v1.0.0 distributes this already validated file; no encoder-only derivative was exported, avoiding an unnecessary checksum/loader compatibility change.

Use `python scripts/download_checkpoint.py` and `python scripts/verify_model.py --checkpoint PATH`. The feature extractor accepts the same checkpoint through the configuration or --checkpoint PATH and validates its configured SHA. An independently downloaded copy must match the original SHA before use.

Publication was authorised by the maintainer in the release task. No approval from an institution or third-party provider is inferred or fabricated. No separate broad model reuse licence has been selected. OSNet's MIT source licence does not, by itself, determine rights in ImageNet initialization or project-trained weights. Benchmark media/GT must be obtained separately and are not published here.
