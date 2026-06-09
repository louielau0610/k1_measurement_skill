# TanRSS2018

## Bibliographic metadata
- Title: Sim-to-Real: Learning Agile Locomotion For Quadruped Robots
- Authors: Jie Tan; Tingnan Zhang; Erwin Coumans; Atil Iscen; Yunfei Bai; Danijar Hafner; Steven Bohez; Vincent Vanhoucke
- Year: 2018
- Venue / status: Robotics: Science and Systems 2018, peer-reviewed
- DOI: 10.15607/RSS.2018.XIV.010
- arXiv: not recorded in P1
- Official URL: https://m.roboticsproceedings.org/rss14/p10.html
- PDF URL: https://m.roboticsproceedings.org/rss14/p10.pdf
- Verification status: verified
- Reading status: abstract_read

## Problem addressed

Simulation-trained quadruped policies can fail on hardware because simulation omits or misrepresents actuator behavior, latency, and other dynamics.

## Method summary

The paper combines reinforcement learning with simulator improvements, system identification, actuator modeling, latency modeling, and dynamics randomization for quadruped locomotion transfer.

## Assumptions

The authors can train policies and modify the simulator/controller stack.

## Experiment setup / platform

Quadruped locomotion transfer from simulation to real robot.

## Metrics

P1 recorded high-level deployment and locomotion metrics from official metadata/abstract only.

## Key findings

The official abstract supports the safe claim that actuator modeling, latency simulation, and system identification are important for sim-to-real locomotion.

## Limitations

This is not a closed-source SDK command-response calibration paper.

## Relevance to our project

Supports our conservative framing that deployment mismatch needs explicit measurement/modeling.

## Difference from our project

Our project does not train a locomotion policy or edit the simulator/controller. It measures sparse command-to-motion response artifacts externally.

## Safe citation claims

TanRSS2018 is prior work showing sim-to-real quadruped locomotion benefits from system identification, actuator modeling, latency modeling, and dynamics randomization.

## Do-not-claim notes

Do not claim it validates our K1 response model or proves our pipeline is novel.

## BibTeX

See `paper/related_work/seed_references.bib`.

