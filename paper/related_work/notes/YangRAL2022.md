# YangRAL2022

## Bibliographic metadata
- Title: Online Kinematic Calibration for Legged Robots
- Authors: Shuo Yang; Howie Choset; Zachary Manchester
- Year: 2022
- Venue / status: IEEE Robotics and Automation Letters 7(3), peer-reviewed
- DOI: not recorded in P1
- arXiv: not recorded in P1
- Official URL: https://publications.ri.cmu.edu/online-kinematic-calibration-for-legged-robots
- PDF URL: available from CMU RI page
- Verification status: verified
- Reading status: abstract_read

## Problem addressed

Legged robot kinematic parameters can be hard to measure offline and can vary with deformation and contact conditions.

## Method summary

The method estimates kinematic parameters online by using velocity prediction errors and integrates calibration into state estimation.

## Assumptions

The method assumes access to kinematic model and estimator internals.

## Experiment setup / platform

Simulation and hardware validation are reported on the CMU RI page.

## Metrics

Position drift and velocity prediction comparisons are reported in the metadata summary.

## Key findings

Safe P1 summary: velocity prediction error can be used as a calibration signal in legged robotics.

## Limitations

This is not a closed-source external command-response interface.

## Relevance to our project

Strong seed for discrepancy-driven calibration framing.

## Difference from our project

Our project does not calibrate kinematic parameters or modify state estimation.

## Safe citation claims

YangRAL2022 uses velocity prediction error for online kinematic calibration in legged robots.

## Do-not-claim notes

Do not claim our black-box response model is equivalent to kinematic calibration.

## BibTeX

See `paper/related_work/seed_references.bib`.

