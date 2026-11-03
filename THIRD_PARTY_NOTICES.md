# Third-party notices

| Component | Source | Licence / copyright | Included files | Changes |
|---|---|---|---|---|
| OSNet | [deep-person-reid](https://github.com/KaiyangZhou/deep-person-reid/blob/master/torchreid/models/osnet.py) | MIT; copyright(c)2018 Kaiyang Zhou | vendor/osnet.py; vendor/OSNET_MIT_LICENSE.txt | Byte-preserved from the previously verified package; executable source was checked against the official implementation in that audit. No changes in this GitHub preparation. |
| TrackEval | [TrackEval](https://github.com/JonathonLuiten/TrackEval) snapshot included in the original experiment's PuTR checkout | MIT; copyright(c)2020 Jonathon Luiten | vendor/trackeval/**; vendor/TRACKEVAL_LICENSE.txt | Source files unchanged; source manifest records every hash. The original snapshot's standalone upstream commit was not recorded. |
| Python dependencies | Declared public pip/Conda packages | Each package's own licence; installed metadata is recorded in manifests/dependency_licences.json | Dependency specifications only; no pip/Conda binary environment is redistributed | No third-party library patches. |

Original MIT notices remain in full. The evaluation wrapper supplies NumPy deprecated-name compatibility aliases outside vendored source; it does not alter metric equations. OSNet pretrained URL constants are inherited source code; SAGL extraction uses pretrained=False and the explicitly supplied, checksum-checked Sports-ReID checkpoint, not an automatic model download.

Manifests identify the exact vendored sources. The TrackEval parent checkout revision identifies a PuTR repository, not a falsely inferred standalone TrackEval revision. Source-code permissions do not establish dataset or checkpoint redistribution permission. No GTA/AFLink implementation or benchmark image is added. The maintainer-authorised original Sports-ReID checkpoint is distributed as a separate Release attachment; it is not governed automatically by the source-code notices.
