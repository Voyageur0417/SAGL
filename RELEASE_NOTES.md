# SAGL v1.0.0 — Research Code and Sports-ReID Weights

This release provides the completed-tracklet identity-repair implementation and the exact original Sports-ReID OSNet-x1.0 checkpoint used by the SAGL manuscript. The release tag pins the public source snapshot; the archived algorithm freeze is f4db30b3a5aefb147867f7e141402a9de30b480b and the experiment-script archive is d79778c88aa777a8e41170127ebf147906522d41. Scientific matching rules and parameters are unchanged.

## Model asset

- File: clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
- Size:30,535,806 bytes
- SHA256:0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9
- OSNet-x1.0;512-dimensional embedding; RGB input width128, height256; ImageNet normalization; eval mode and float32 inference; normalized embeddings cached as float16.
- ImageNet initialization, SportsMOT train-only, fixed epoch60, seed42. The original checkpoint retains classifier/optimizer/scheduler state. No encoder-only conversion or retraining was performed.

The trained file is a separate attachment and is not committed to Git. SHA256SUMS.txt is included.

## Environment and commands

Verified Linux stack: Python3.10.19, PyTorch2.5.1/CUDA11.8 for GPU extraction, NumPy1.26.4, SciPy1.15.3, OpenCV4.11.0, Pillow12.1.0 and PyYAML6.0.3. Linking runs on CPU. Follow README installation instructions and provide legally obtained media and the matching carrier outputs.

```bash
python scripts/download_checkpoint.py
python scripts/verify_model.py --checkpoint checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth --device cuda:0
python scripts/extract_features.py --config configs/sportsmot_ocsort.yaml --device cuda:0 --output outputs/features
python scripts/run_sagl.py --config configs/sportsmot_ocsort.yaml --cache-dir outputs/features --output outputs/prediction
python scripts/evaluate.py --config configs/sportsmot_ocsort.yaml --gt-root data/sportsmot_ocsort/gt --predictions outputs/prediction/tracker/data --output outputs/evaluation
```

Edit input paths/sequence selection first. The extractor loads the supplied checkpoint through the strict encoder-parameter interface; optional --checkpoint changes only its location. Exact per-sequence FPS, crop/normalization, batch and cache mapping are documented. No GT is read during features or inference. The fixed parameters remain lambda0.84, beta0.02 and delta0.03.

## Validation scope

The earlier package regenerated42,039 embeddings on four representative complete sequence/carrier cases and checked1,462,753 feature keys across155 sequence/carrier entries. Final predictions matched the frozen references, while regenerated floating-point features and some candidate/qualified edges differed. This release additionally reran a complete real SportsMOT sequence (11,075 embeddings), real-crop inference, SAGL, ID-only/reference checks and local TrackEval; prediction bytes and corresponding metrics matched the frozen reference. CPU cached inference and independent GPU workflow were verified. Complete fresh CPU sequence extraction, all155 fresh-image cases and other OS platforms are not claimed verified.

This is not one-command reproduction of every ablation/external-method table. Benchmark media, GT, real carrier outputs, caches and predictions are not bundled. Official SportsMOT HOTA68.24 (carrier),75.77 (penalized matching) and75.80 (SAGL) are previously obtained official results, not recomputed by this release.

## Publication and licensing

The repository maintainer authorised public publication of this code and original model. No project-wide software/model reuse licence was selected; availability is distinct from unrestricted reuse. OSNet and TrackEval retain their original MIT notices. Their source licences do not automatically govern the project-trained checkpoint or benchmark data. No institutional/data-provider clearance is invented.
