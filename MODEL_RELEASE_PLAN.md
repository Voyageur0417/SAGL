# Model release plan

## Exact model identity

Sports-ReID OSNet-x1.0,512-dimensional embeddings; ImageNet initialization followed by SportsMOT train-only training, fixed epoch60 and seed42. Input crop width128, height256; the original model structure and preprocessing remain unchanged.

- Original filename: clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
- Original size:30,535,806 bytes
- Original SHA256:0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9
- Identity/loading/representative inference have been verified. The original file also contains classifier, optimizer and scheduler state.

## Current access and permission

RELEASE_PERMISSION_REVIEW_REQUIRED. No verified public download address is established, and the model is not included in this repository or its archive. Obtain permission from the appropriate rights holders; confirm how ImageNet initialization and SportsMOT training terms affect redistribution. OSNet's MIT source-code licence is not assumed to cover these assets. Recipients without the exact authorised checkpoint cannot reproduce the paper's embeddings merely from this source repository.

## Recommended release route after approval

Publish a separately approved model attachment via GitHub Releases or an appropriate persistent model repository, with a model card, licence/access terms, original-file checksum and a clear association with the approved source release. This is a proposal, not an existing release or URL. Do not commit the weight to the source tree or upload the training directory.

No encoder-only checkpoint is exported in this preparation. If the rights holders later approve an inference-only derivative, compare its outputs with the original model under controlled identical inputs and record a separate filename, size and SHA256. Keep the original SHA above as provenance; do not label a different file with that checksum. Update loader/configuration documentation and rerun identity/equivalence checks before treating that derivative as supported.

There is no model replacement, retraining, tuning or automatic upload in this release task.
