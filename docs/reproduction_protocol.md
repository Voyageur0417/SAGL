# Reproduction protocol

1. Verify the checkpoint SHA and carrier/input-cache hashes before running.
2. Reconstruct observation mapping directly from carrier rows and the published dataset profile, then compare the ordered keys with the reference cache.
3. Generate the entire selected sequence from original media; do not fill missing features from a reference cache.
4. Run the unchanged SAGL pipeline independently on the reference and fresh cache.
5. Compare all feasible/candidate/qualified graphs, current P cardinality, selected edge sets/order, prototype selection, identity maps/chains and prediction rows. Compare raw arrays as well as file hashes: compressed NPZ files need not have deterministic ZIP timestamps.
6. Verify every non-ID token and original row order, and reject duplicate (frame,ID).
7. Evaluate both outputs with the same legal validation GT using the separate TrackEval entry.
8. Copy only the source package to an independent directory, install its documented dependencies in a clean venv, and repeat with explicitly staged local inputs. No development checkout or hidden input mapping is required.

A fresh-cache final prediction match is not evidence that all intermediate arrays match. If graph membership or ordering differs, report it. Numerical residuals are not automatically attributed to floating-point precision; preprocessing, model loading, batch boundaries and layout must be checked. Conclusions apply only to the sequences and environments actually exercised.
