# SAGL: Sparse Appearance-Guided Global Linking for Sports Multi-Object Tracking

Research code and the original Sports-ReID checkpoint are provided with [release v1.0.0](https://github.com/Voyageur0417/SAGL/releases/tag/v1.0.0). The repository maintainer has authorised public publication. No project-wide software/model reuse licence has been selected; public availability is distinct from a blanket open-source licence (see [LICENSE](LICENSE)).

## Overview

SAGL repairs long-range identity fragmentation in completed sports tracklets. It combines robust appearance evidence, sparse temporal candidates and decoupled global linking. Identity projection changes only identity labels: detection rows, frame indices, bounding boxes, confidence values, other fields and original row order are preserved. The input carrier tracker has already run; SAGL does not add detections or split internally contaminated tracklets.

## Method

1. **Robust multi-prototype representation:** a frozen Sports-ReID OSNet supplies observation embeddings. Mean, temporal-anchor and quality-selected prototypes represent tracklet appearance variation.
2. **Sparse temporal candidate graph:** temporally feasible tracklet pairs are scored, source-tier Top-10 candidates are retained across five temporal tiers, and dual appearance qualification defines admissible links. All feasible pairs are still scored before sparsification.
3. **Decoupled global linking:** optional penalized matching determines link cardinality; competition-aware exact fixed-cardinality matching selects identities at that count. Identity chains are projected onto the original observations.

The inference entry fixes `lambda=0.84`, `beta=0.02` and `delta=0.03`. It uses neither GT nor historical link counts. The frozen source commit is recorded in `manifests/frozen_source_manifest.json`; internal module filenames are retained for compatibility and do not define public method variants.

## Installation

Python 3.10 on Linux is the tested platform. Run commands from this repository root. Use a new output directory for every run.

### CPU cached-feature inference and public tests

This lightweight route needs no model weights, datasets, CUDA or PyTorch:

```bash
python3.10 -m venv ../sagl-cpu-env
. ../sagl-cpu-env/bin/activate
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-ci.txt
python -m pip install --no-deps -e .
python -m pip check
python -m unittest discover -s tests -v
python scripts/ci_smoke.py
```

`requirements-core.txt` alone provides the cached linking dependencies. `requirements-ci.txt` additionally supplies OpenCV and Pillow for crop tests and the evaluation import path; it does not install PyTorch.

### GPU feature extraction

The verified Linux CUDA 11.8 route uses a public-channel Conda dependency specification and a compatible NVIDIA driver:

```bash
conda create -y --prefix ../sagl-gpu-env --file environments/linux-cuda118-explicit.txt
conda activate ../sagl-gpu-env
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
python -m pip check
python scripts/verify_environment.py
```

These are standard dependency packages, not a clone of a development checkout. The numerical stack is Python 3.10, PyTorch 2.5.1, NumPy 1.26.4, SciPy 1.15.3 and OpenCV 4.11. An alternative CPU PyTorch installation is described in [installation.md](docs/installation.md); complete fresh-feature CPU sequence extraction has not been validated. GPU is optional for linking and used for the verified complete fresh-feature test.

## Quick start: synthetic example

No private data or checkpoint is needed after the lightweight installation:

```bash
python examples/make_synthetic_example.py --output outputs/toy
python scripts/run_sagl.py --config outputs/toy/config.json --cache-dir outputs/toy/cache --output outputs/toy/prediction
python scripts/verify_predictions.py --carrier outputs/toy/carrier/toy.txt --prediction outputs/toy/prediction/tracker/data/toy.txt
```

This creates six artificial observations with one-hot features. It tests interfaces and ID-only projection; it is not a sports experiment or a reproduction of the paper's results. `scripts/ci_smoke.py` runs the same example in temporary storage, checks CLI help and configuration parsing, and verifies the expected two links.

## Data preparation

Acquire [SportsMOT](https://github.com/MCG-NJU/SportsMOT), [SoccerNet-Tracking](https://www.soccer-net.org/tasks/tracking) and [TeamTrack](https://github.com/AtomScott/TeamTrack) through their providers and comply with their terms. No original media, real crops, GT, carrier predictions or feature caches are included here.

Edit a configuration under `configs/` to provide your carrier root and media paths. Relative paths resolve against the configuration file, not the shell working directory. Preserve sequence order, minimum observations and per-sequence FPS. For an initial test, explicitly select one complete sequence. The exact paper carriers are identified by hashes in `manifests/experiment_manifest.json`; there is no claim that a different tracker output reproduces the paper's carrier-specific scores. See [datasets.md](docs/datasets.md).

## Model checkpoint

The required model is **Sports-ReID OSNet-x1.0**, producing 512-dimensional embeddings from 128-by-256 crops. It was initialized from ImageNet and trained on SportsMOT train only, with the fixed epoch-60, seed-42 checkpoint.

- Filename: `clean_sportsmot_train_only_osnet_x1_0_epoch60.pth`
- Size: 30,535,806 bytes
- SHA256: `0634e9782792d27ff066e3c20f6c00a93d7bb662c51a4976e39eae2bf36507f9`

The exact original checkpoint is hosted as a separate [GitHub Release attachment](https://github.com/Voyageur0417/SAGL/releases/download/v1.0.0/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth); it is not committed to Git. Download and verify it from the repository root:

```bash
python scripts/download_checkpoint.py --output checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth
python scripts/verify_model.py --checkpoint checkpoint/clean_sportsmot_train_only_osnet_x1_0_epoch60.pth --device cuda:0
```

The downloader checks both the original size and SHA256. The loader reconstructs OSNet-x1.0 and verifies encoder parameters; the extraction entry uses the same loader. The original checkpoint includes the training classifier, optimizer and scheduler state. No encoder-only replacement is needed for v1.0.0. Use this trusted, verified file; another OSNet model is not an exact-reproduction substitute. Model provenance and publication details are recorded in [MODEL_RELEASE_PLAN.md](MODEL_RELEASE_PLAN.md) and [checkpoint.md](docs/checkpoint.md).

## Feature extraction

After supplying valid media, carrier files and the checkpoint in the configuration:

```bash
python scripts/extract_features.py --config configs/sportsmot_ocsort.yaml --device cuda:0 --output outputs/features
```

`--checkpoint PATH` changes the file location; the configured checksum must remain the required model identity. Outputs include `features.npy`, `features.keys.json`, `observation_manifest.json` and `extraction_manifest.json`. Each feature maps explicitly to sequence, frame, original carrier identity, source row and bounding box. No GT is read. Keep the batch defaults (192 for SportsMOT/SoccerNet; 256 for TeamTrack) when following the frozen profile. Details: [feature_extraction.md](docs/feature_extraction.md) and [feature_cache_format.md](docs/feature_cache_format.md).

## SAGL inference

```bash
python scripts/run_sagl.py --config configs/sportsmot_ocsort.yaml --cache-dir outputs/features --output outputs/prediction
python scripts/verify_predictions.py --carrier data/sportsmot_ocsort/carrier/v_00HRwkvvjtQ_c001.txt --prediction outputs/prediction/tracker/data/v_00HRwkvvjtQ_c001.txt
```

The second command checks the named sequence; run it for each configured sequence as needed. Outputs include feasible scores, candidate and qualified graphs, first-stage cardinality, selected links, identity chains, ID map, hashes and `tracker/data/SEQUENCE.txt`. Existing cache/key paths can instead be specified in the configuration. Details: [inference.md](docs/inference.md).

## Evaluation

```bash
python scripts/evaluate.py --config configs/sportsmot_ocsort.yaml --gt-root data/sportsmot_ocsort/gt --predictions outputs/prediction/tracker/data --output outputs/evaluation
```

GT is read only by this separate evaluation entry. The unchanged, licensed TrackEval snapshot saves raw metrics and combined HOTA, DetA, AssA, IDF1, MOTA, IDSW, FP and FN. Sequence mapping, frame indexing and dataset-specific preprocessing must match the original protocol. Local validation metrics are distinct from official hidden-test results; the package does not recompute official SportsMOT test HOTA locally. See [evaluation.md](docs/evaluation.md).

## Results

The following SportsMOT official-test HOTA scores were obtained previously and reported in the manuscript. They are **not** newly evaluated by this release task.

| Method | Official-test HOTA |
|---|---:|
| OC-SORT carrier | 68.24 |
| Penalized Matching | 75.77 |
| SAGL | 75.80 |

These official results are separate from local validation and the representative-sequence reproduction checks below.

## Reproducibility and scope

The previously validated package covered four representative complete sequence/carrier cases: 42,039 regenerated embeddings, plus exact mapping checks for 1,462,753 feature keys across 155 sequence/carrier entries. Final predictions were identical on the four representative cases despite numerical feature differences. The SoccerNet sample changed a small number of candidate and qualified edges; intermediate graphs and features are **not** claimed to be bit-exact. Ten local TrackEval runs agreed with the corresponding frozen sequence results. These are not four full-setting reruns or four combined-setting HOTA measurements.

This repository has been independently installed and exercised; the exact current test scope is in `manifests/github_validation.json`. Full regeneration for all155 entries, all-sequence fresh-feature equivalence, complete CPU fresh sequence extraction and other operating systems remain unverified. GitHub Actions covers only public unit/interface/configuration/synthetic tests, not real data, weights or paper performance. Its job commands have also been exercised locally; hosted Actions status is separate from the real-data validation.

To compare legal reference artifacts after inference:

```bash
python scripts/verify_reproduction.py --reference-inference outputs/reference_run --candidate-inference outputs/prediction --reference-cache outputs/reference_cache --candidate-cache outputs/features --carrier-root data/sportsmot_ocsort/carrier --report outputs/comparison.json
```

The tool distinguishes `EXACT_MATCH`, `NUMERICALLY_EQUIVALENT` and `NOT_REPRODUCED`. This repository supports the core method, feature generation and standard evaluation; it does **not** offer one-command reproduction of every paper table, all ablations or all GTA/AFLink runners. See [reproduction.md](docs/reproduction.md).

## Citation

Publication metadata has not been assigned. Cite the manuscript without inventing a DOI, journal volume or pages:

```bibtex
@unpublished{hu_sagl,
  author = {Hu, Songming and Han, Bing and Su, Zhigang and Hao, Jingtang},
  title = {SAGL: Sparse Appearance-Guided Global Linking for Sports Multi-Object Tracking},
  note = {Unpublished manuscript}
}
```

`CITATION.cff` provides the same author order. The software release is v1.0.0; software versioning does not introduce a series of scientific method variants.

## License and availability

The repository maintainer has authorised public publication of the research code and the original trained checkpoint. No MIT, Apache-2.0 or other project-wide reuse licence has been selected for SAGL-owned material. See [LICENSE](LICENSE) and [CODE_LICENSE_DECISION.md](CODE_LICENSE_DECISION.md) for that distinction. OSNet and TrackEval retain their original MIT notices; those notices do not relicense SAGL-owned code, trained weights or benchmark media. Data must still be acquired separately under the providers' terms.

## Acknowledgments

SAGL uses the OSNet implementation from [deep-person-reid](https://github.com/KaiyangZhou/deep-person-reid) and the [TrackEval](https://github.com/JonathonLuiten/TrackEval) evaluation code. Their MIT notices are retained. We acknowledge SportsMOT, SoccerNet-Tracking and TeamTrack and their data providers. Third-party implementations, trained weights and benchmark media have separate rights and access conditions.
