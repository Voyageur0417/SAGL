# Evaluation protocol

Evaluation is a separate script and the only executable that reads GT. It accepts the same sequence/FPS configuration, a GT root, a directory of completed predictions and a new output directory. Each sequence is 1-based, with GT_ROOT/SEQUENCE/gt/gt.txt and GT_ROOT/SEQUENCE/seqinfo.ini. Predictions are comma-separated MOT records: frame,id,left,top,width,height,confidence,... .

For SportsMOT validation the original protocol uses MotChallenge2DBox, BENCHMARK=SportsMOT, SPLIT_TO_EVAL=val, SKIP_SPLIT_FOL=True and DO_PREPROC=True. For SoccerNet game9 and TeamTrack local validation it uses BENCHMARK=MOT17, SPLIT_TO_EVAL=train, SKIP_SPLIT_FOL=True and DO_PREPROC=False. These labels select the existing MOT reader; they do not relabel the dataset as MOT17. Sequence lengths are taken from each supplied seqinfo.ini. The supplied FPS values are for SAGL gap calculations, not a GT-assisted matching input.

SportsMOT raw GT can be used in this directory structure. The original SoccerNet and TeamTrack MOT-format GT mappings must be supplied or regenerated using the dataset provider's mapping. Do not infer a frame offset or identity namespace from a filename. Evaluation manifests hash the exact GT files used. No GT files or derived GT mirrors are redistributed in the code archive.

The original experiment used a TrackEval snapshot in the PuTR checkout. Its upstream TrackEval Git revision was not independently recorded. This package preserves that exact source tree and MIT notice; manifests/trackeval_source_manifest.json records the parent checkout revision and every source hash. NumPy's deprecated int/float aliases are supplied by the external evaluation wrapper, with no change to metric source. HOTA, DetA and AssA are means over TrackEval's 19 alpha thresholds multiplied by100; IDF1/MOTA are percentages. Combined results use TrackEval's metric-specific aggregation.

Official SportsMOT test HOTA remains the externally reported Carrier68.24, P75.77 and SAGL75.80. This package has no hidden-test GT and does not claim to recompute those scores. Local validation reproduction metrics are stored separately from manuscript experiments.
