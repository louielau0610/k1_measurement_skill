# Main Paper Table Pack v1

Recommended main-paper tables (3-4 concise tables). Source tables are in `paper/tables/`.

---

## Table 1: Method Stage I/O Contract (recommended for Method §3)

| stage | input | output | producer_script | non_goals |
| --- | --- | --- | --- | --- |
| 1. Measurement | K1 field ROS2 logs | Velocity profile v0 | M7/M8 workflow | Not compensation-ready |
| 2. Dataset | Measurement v0 + schema v1 | Dataset v1 (5 records) | `build_velocity_response_dataset_v1.py` | No numeric fabrication |
| 3. Response model | Dataset v1 | 5 predictions + uncertainty labels | `run_velocity_response_model_v1.py` | Not calibrated probabilities |
| 4. Risk mapping | Response predictions | 5 risk assessments + warnings | `run_navigation_risk_mapping_v1.py` | No compensation/control |
| 5. Evaluation | All upstream outputs | Evaluation report + claim governance | `generate_research_pipeline_evaluation_v1.py` | Not publication readiness |

**Source**: `paper/tables/method_stage_io_contract_table.md` (condensed).  
**Claim boundary**: Structural pipeline description only. Does not validate performance.

---

## Table 2: Current Evaluation Metrics (recommended for Experiments §4)

| metric | available | value |
| --- | --- | --- |
| Dataset records | yes | 5 (4 numeric, 1 qualitative) |
| Response predictions | yes | 5 |
| Risk assessments | yes | 5 (critical=1, high=2, medium=2) |
| Advisory warnings | yes | 5 |
| Exact-source MAE | sanity check only | 0.0 m/s |
| Held-out prediction error | **no** | — |
| Collision / near-miss / success rate | **no** | — |
| Calibrated uncertainty | **no** | — |
| Multi-surface generalization | **no** | — |

**Source**: `paper/tables/experiment_metrics_status_table.md` (condensed).  
**Claim boundary**: Available metrics are structural only. Unavailable metrics require future experiments.

---

## Table 3: Evidence Boundary / Claim-Upgrade Requirements (recommended for Discussion §5 or Appendix)

| claim type | current status | required evidence |
| --- | --- | --- |
| Pipeline existence | supported (structural) | Already met |
| Dataset construction | supported (structural) | Already met |
| Model predictive quality | not supported | Held-out evaluation on repeated trials |
| Risk warning usefulness | not supported | Navigation outcome trials |
| Navigation safety improvement | **prohibited** | Navigation trials + collision/success metrics |
| Calibrated uncertainty | **prohibited** | Repeated trials + calibration protocol |
| Generalization | **prohibited** | Multi-surface, multi-session data |
| Compensation readiness | **prohibited** | All above + offline compensation validation |
| Safe command adapter | **prohibited** | All above + safety validation |

**Source**: `paper/tables/claim_upgrade_requirements_table.md` (condensed).  
**Claim boundary**: Documents what evidence is needed before upgrading each claim. Prohibited claims remain prohibited until evidence exists.

