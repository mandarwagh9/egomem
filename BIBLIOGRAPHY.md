# BIBLIOGRAPHY — EgoMem

**Real sources only, with working links.** No source is listed here unless this
loop has actually fetched/verified it. Populated starting in Phase 1 (RESEARCH).

Format per entry:
- **[key]** Authors. *Title.* Venue/Year. <link> — one line on why it matters
  (memory mechanism; model-bound vs model-agnostic; substrate).

## Sources

_Verified (fetched and read) on 2026-06-13 during Phase 1 lit-map run._

- **[embodied-videoagent]** Fan, Ma, Su, Guo, Wu, Chen, Li. *Embodied VideoAgent: Persistent Memory from Egocentric Videos and Embodied Sensors Enables Dynamic Scene Understanding.* ICCV 2025. <https://arxiv.org/abs/2501.00358> — persistent **object memory** + temporal memory fed by **egocentric video + depth + pose**; queried by an **LLM agent** (not a control policy / world model). The closest bridge to our substrate; memory is agent-bound, not a neutral layer.
- **[map-vla]** Li, Guo, Wu, Wang, Deng, Weng, Tan, Wang. *MAP-VLA: Memory-Augmented Prompting for Vision-Language-Action Model in Robotic Manipulation.* 2025. <https://arxiv.org/abs/2511.09516> — soft-prompt memory library + trajectory-similarity retrieval; **plug-and-play on a frozen VLA** (model-agnostic *within* the VLA paradigm only); fed by robot demos. +7.0% sim / +25.0% real on long-horizon.
- **[mem]** Torne, Pertsch, Walke, Vedder, Nair, Ichter, Ren, Wang, Tang, Stachowicz, Dhabalia, Equi, Vuong, Springenberg, Levine, Finn, Driess. *MEM: Multi-Scale Embodied Memory for Vision Language Action Models.* 2026. <https://arxiv.org/abs/2603.03596> — dual short-term video + long-term text memory; **VLA-bound**; enables ~15-min tasks; fed by robot video + text.
- **[ne-dreamer]** Bredis, Balagansky, Gavrilov, Rakhimov. *Next Embedding Prediction Makes World Models Stronger (NE-Dreamer).* 2026. <https://arxiv.org/abs/2603.02765> — keeps Dreamer's **RSSM** (deterministic recurrent state + stochastic latent); memory is **internal & inseparable** from the world model, not an external queryable layer.
- **[wm-survey]** Li, He, Zhang, Wu, Li, Liu. *A Comprehensive Survey on World Models for Embodied AI.* 2025. <https://arxiv.org/abs/2510.16732> — frames world models as internal simulators; confirms memory is **model-internal** across the field.
- **[megohand]** Zhou, Zhan, Zhang, Lu. *MEgoHand: Multimodal Egocentric Hand-Object Interaction Motion Generation.* 2025. <https://arxiv.org/abs/2505.16602> — large **egocentric human** HOI corpus (3.35M RGB-D frames, 24K interactions, 1.2K objects) with RGB + monocular depth + hand pose. Evidence our substrate exists at scale.
- **[lerobot-v3]** Hugging Face. *LeRobotDataset v3.0: Bringing large-scale datasets to lerobot.* 2025. <https://huggingface.co/blog/lerobot-datasets-v3> — neutral storage format: parquet (state/action) + MP4 (video) + JSON metadata, multi-episode packing, many embodiments. The container both consumers already read. (Docs: <https://huggingface.co/docs/lerobot/main/lerobot-dataset-v3>)
