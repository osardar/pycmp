# Schema-3 baseline model cards

These cards document the three frozen checkpoints produced by the September 11,
2026 schema-3 capped baseline. They are research artifacts, not promoted models.

The [November 15 review](../PROJECT-REVIEW.md) consolidates training philosophy,
features actually consumed by the encoder, and later cross-runtime pilot results.
The cards' completed bytecode results use the older decoder and Python 3.14
gallery; they do not qualify the standalone vectorizer or every supported runtime.

| Checkpoint | Seed | SHA-256 | Status |
|---|---:|---|---|
| [model-seed0.pt](schema3-baseline-seed0.md) | 0 | `6977e90753a0a4a166e3ef3ab696b1c9bfe3a0385195585559c066590897f1db` | Not promoted |
| [model-seed1.pt](schema3-baseline-seed1.md) | 1 | `f4a212fcfc33e37dc7ea5a1b0cfed552deabda58ddace0379f32d70f3e7d2f11` | Not promoted |
| [model-seed2.pt](schema3-baseline-seed2.md) | 2 | `13bfabe9df059bc703d73bb19647c4f61f5375326bc012451105a40b81e26ae9` | Not promoted |

All three use the same architecture, corpus, training procedure and evaluation
sets. Seeds change initialization and training order. No checkpoint has a
consistent learned advantage over the fixed untrained encoder, and all three
trail hashed-graph and opcode-structure baselines on direct bytecode retrieval.
Use multiple methods and analyst review rather than selecting a checkpoint as an
automatic decision-maker.

The checkpoint files and generated evaluation artifacts are local ignored files;
a Git clone contains these cards and reports, not the weights themselves. No
standalone checkpoint license is declared in the recorded artifacts.
