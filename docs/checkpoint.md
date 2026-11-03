# Original Sports-ReID checkpoint

Sports-ReID OSNet-x1.0, SportsMOT train-only, ImageNet-initialized, epoch60, seed42;512-D embeddings.

- File: clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
- Bytes:30,535,806
- SHA256: `0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9`
- Download: https://github.com/Voyageur0417/SAGL/releases/download/v1.0.0/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth

From the repository root:

```bash
python scripts/download_checkpoint.py --output checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
python scripts/verify_model.py --checkpoint checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth --device cuda:0
```

The original file is a separate v1.0.0 Release asset and remains excluded from Git. Its classifier/optimizer/scheduler state is retained, with no encoder-only conversion. Use only the trusted, checksum-verified attachment. Do not substitute a similarly named file or a differently trained OSNet. The default configuration paths point to this local download location; use --checkpoint PATH to override only its location.

The maintainer authorised publication. Reuse licensing remains distinct from availability; see LICENSE and MODEL_RELEASE_PLAN.md. Original benchmark media, GT, carrier outputs and precomputed caches are not part of the model attachment.
