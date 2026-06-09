# FuCVPRW2022

## Bibliographic metadata
- Title: Coupling Vision and Proprioception for Navigation of Legged Robots
- Authors: Zipeng Fu; Ashish Kumar; Ananye Agarwal; Haozhi Qi; Jitendra Malik; Deepak Pathak
- Year: 2022
- Venue / status: CVPR Workshops 2022
- DOI: not recorded in P1
- arXiv: not recorded in P1
- Official URL: https://openaccess.thecvf.com/content/CVPR2022W/MULA/html/Fu_Coupling_Vision_and_Proprioception_for_Navigation_of_Legged_Robots_CVPRW_2022_paper.html
- PDF URL: https://openaccess.thecvf.com/content/CVPR2022W/MULA/papers/Fu_Coupling_Vision_and_Proprioception_for_Navigation_of_Legged_Robots_CVPRW_2022_paper.pdf
- Verification status: verified
- Reading status: abstract_read

## Problem addressed

Navigation should account for both visual terrain context and proprioceptive evidence of what the walking controller can handle.

## Method summary

The paper combines a vision cost map with a proprioceptive safety advisor and speed limits for point-goal legged navigation.

## Assumptions

The method assumes integration with a navigation stack and walking policy.

## Experiment setup / platform

Legged robot point-goal navigation experiments are described by the CVF page.

## Metrics

Navigation performance metrics are discussed at abstract level; P1 did not extract numerical results.

## Key findings

Safe P1 summary: high-level navigation can benefit from low-level locomotion capability signals.

## Limitations

Workshop scope and not a closed-source command-response calibration study.

## Relevance to our project

Strong seed for navigation/locomotion coupling and advisory interpretation.

## Difference from our project

Our project produces offline risk labels and does not control navigation.

## Safe citation claims

FuCVPRW2022 couples vision and proprioception to improve legged robot navigation decisions.

## Do-not-claim notes

Do not claim our M16 risk map has demonstrated navigation improvement.

## BibTeX

See `paper/related_work/seed_references.bib`.

