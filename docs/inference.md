# Inference

`python scripts/run_sagl.py --config CONFIG --cache-dir CACHE --output NEW_DIRECTORY`

CACHE contains features.npy and features.keys.json. The loader verifies feature counts, sequence/track/frame mapping, confidence and available bbox/area metadata before prototype construction. Original observation strings are kept for ID projection; rows from ineligible tracklets remain in the output.

The frozen modules compute all temporally feasible scores before source-tier sparsification. Output files: all_feasible_scores.npz, candidate_graph.npz, qualified_graph.npz, prototype_statistics.json, quantity_stage.json, edge_sets.npz, selection_details.npz, accepted_links.json, identity_chains.json, id_map.json, input_manifest.json, output_manifest.json and tracker/data/SEQUENCE.txt. Diagnostic exports do not change a solver input or selected edge. identity_chains.json groups original IDs by final identity; within-group IDs are listed numerically, not asserted to be a temporal traversal.

Missing/invalid crops follow the documented original dataset-specific fallback; inspect extraction_manifest.json counts and observation_manifest.json. An absent media root or checkpoint is rejected. Never use a wrong checkpoint merely because its tensor shapes load.
