# Observation cache and mapping

`features.npy`: N×512 float16, finite; encoder eval/no_grad,float32,no AMP, L2 normalization(dim=1,eps=1e-12), then float16. Frozen downstream casts to float32 without per-observation renormalization.

`features.keys.json`: JSON list, each item corresponds to exactly one NPY row. SportsMOT/SoccerNet order = config sequence order → original ID increasing → frame increasing, eligible tracks only. Fields: sequence,tid,local_index(0-based within-track),frame,score,area=max(0,w)*max(0,h). TeamTrack order = config sequence order → original carrier row order; all rows incl singleton. Fields: sequence,scene,track_id,row_index(0-based within-sequence),frame,bbox,score,valid_bbox. **TeamTrack omits area intentionally**; adding it changes frozen quality ranking. Original TeamTrack keys file wraps this list in a `keys` object; the frozen reader accepts both shapes.

`observation_manifest.json` also accounts for every original row, including ineligible rows with feature_index=null. It records raw_line_number, zero-based nonempty row_index, sequence, frame, original_ID, bbox, confidence, exact feature_index, actual crop bounds and status. No hidden training ID table is required. `extraction_manifest.json` records checkpoint/carrier/media hashes, batch layout, environment, finite checks and timing.

Crop = clip(floor(left,top),ceil(left+width,top+height)) with lower corners bounded by image_size−1 and upper corners by image_size. Valid crop converts BGR→RGB, OpenCV INTER_LINEAR resize(width128,height256),float32/255,mean(.485,.456,.406),std(.229,.224,.225),CHW. Sports/SoccerNet missing/empty crops send a black image through the encoder; TeamTrack invalid/empty/unreadable-frame rows remain zero features. These are different historical fallbacks and must not be conflated.

Sports/SoccerNet batches use contiguous NCHW as the original DataLoader; batch192 spans sequences. TeamTrack retains original NumPy stacked tensor layout and flushes batch256 at sequence ends. Changing layout or batch boundaries can change numerical results. The release does not claim feature byte identity across backends.
