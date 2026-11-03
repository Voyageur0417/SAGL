# Required checkpoint

Sports-ReID OSNet-x1.0, SportsMOT train-only, ImageNet-initialized, epoch60, seed42; 512-dimensional embeddings.

- File: clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
- Size: 30,535,806 bytes
- SHA256: 0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9

The exact file exists and has been loaded and used for real feature generation. It contains training-head, optimizer and scheduler state. It is NOT included in this archive because permission to redistribute the trained model is not established. No public download URL has been verified. Ask the rights holders/corresponding author to provide the original checkpoint subject to the relevant permissions; the code archive alone currently cannot supply it.

Only use trusted local PyTorch checkpoints. Do not substitute an ImageNet OSNet checkpoint, a similarly named epoch file, a differently trained model, or an encoder-only derivative when validating against the SHA above. The model loader verifies missing/unexpected encoder layers; extraction additionally checks the configured checkpoint SHA. A mismatched SHA is rejected. No training or replacement model is part of this reproduction.
