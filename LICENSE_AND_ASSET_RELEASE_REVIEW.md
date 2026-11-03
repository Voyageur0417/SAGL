# License and asset release review

The maintainer authorised public source/model publication for v1.0.0. This records that instruction and component boundaries; it is not an invented external legal clearance.

| Component | Evidence / access route | Candidate package decision |
|---|---|---|
| SAGL-owned frozen source and wrappers | No project licence in the frozen repository | Public publication authorised by the maintainer; no project-wide reuse licence selected. LICENSE records that distinction. |
| OSNet source | Official deep-person-reid MIT licence; source SHA and notice retained | Minimal osnet.py and MIT notice included. This does not automatically license weights. |
| TrackEval source | Original experiment snapshot; MIT notice by Jonathon Luiten; full source hash manifest | Included unchanged with notice. Upstream revision was not recorded; content hashes identify this exact snapshot. |
| NumPy, SciPy, PyTorch, OpenCV, Pillow, PyYAML and transitive packages | Installed wheel metadata/individual terms, recorded separately | Dependencies are installed by the recipient, not redistributed as binaries in this archive. |
| Final Sports-ReID checkpoint | Project training on SportsMOT train from ImageNet initialization; confirmed SHA | Maintainer-authorised v1.0.0 Release attachment; exact original SHA retained; no automatic third-party MIT coverage asserted. |
| ImageNet initialization weights | Local hash and declared training provenance | Not bundled; no inference that a source-code MIT licence settles pretrained-weight terms. |
| SportsMOT videos, frames, GT and crops | Official repository specifies CC BY-NC4.0 and written permission before dataset redistribution | Do not bundle. Recipient obtains the dataset from its provider. |
| SoccerNet media/annotations | Official FAQ discusses copyrighted videos, NDA preventing redistribution and noncommercial research | Do not bundle. Recipient follows official acquisition terms. |
| TeamTrack videos/annotations | Official repository has MIT code licence and provider download routes; underlying footage clearance not established by this review | Do not bundle benchmark assets; recipient follows provider terms. |
| Real carrier outputs, feature caches, GT mappings and predictions | Benchmark-derived assets; no blanket redistribution authorisation established | Retained only in the local private validation area. Hashes and non-identifying numerical summaries may accompany the code; the raw assets are excluded. |
| examples/make_synthetic_example.py | Author-generated toy observation strings and artificial one-hot features | Included, explicitly labelled synthetic format example; not an experimental sports sample. |

Primary sources: [SportsMOT terms](https://github.com/MCG-NJU/SportsMOT#terms), [OSNet licence](https://github.com/KaiyangZhou/deep-person-reid/blob/master/LICENSE), [TrackEval licence](https://github.com/JonathonLuiten/TrackEval/blob/master/LICENSE), [SoccerNet FAQ](https://www.soccer-net.org/faq), [TeamTrack](https://github.com/AtomScott/TeamTrack).

Source and model publication was authorised in this release task. No institution/data-provider agreement or general reuse licence is invented. Benchmark media, raw GT, real carriers/caches/predictions remain outside the source repository.
