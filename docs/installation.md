# Installation

The README contains the locally exercised installation commands. CPU cached-feature inference and public tests use requirements-ci.txt in a clean Python3.10 venv, without PyTorch. A runtime with requirements-core.txt alone can link precomputed features. Full feature extraction uses requirements.txt, including PyTorch2.5.1, and the exact private checkpoint.

The Linux CUDA11.8 Conda explicit package list is made of public-channel dependency URLs; it is not an original-project environment clone. Activate it, set PYTHONNOUSERSITE=1, and install requirements.txt plus this repository in editable mode. Single-thread BLAS variables follow the tested numerical profile.

An alternative CPU feature environment can install the official CPU wheel before resolving the rest of requirements.txt:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-deps torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
```

CPU real-crop forward inference was verified in the prior package; a complete fresh-feature CPU sequence was not completed. Neither the optional environment.yml solver route nor other operating systems are claimed to be independently verified. Torchvision and torchreid are not required. CLI scripts determine their code root from their own file location; no developer checkout or fixed local home directory is required.
