# Autoresearch Skill Evaluation / 自动研究 Skill 评估

## Repository Inspection Summary

- Repository root: `C:\Users\86138\Desktop\Calibration Claw\k1_measurement_skill`
- Existing repo-scoped skill directory: none; `.agents/skills/` did not exist before P0.
- Existing governance file: `AGENTS.md` defines measurement-only boundaries, no secrets, no unverified ROS2 topics, no compensation logic, and no unsafe movement code.
- Existing research-relevant artifacts:
  - `docs/real_k1_forward_velocity_field_test_v0.md`
  - `reports/real_k1_forward_velocity_analysis_v0.md`
  - `docs/real_k1_velocity_profile_contract_v0.md`
  - `docs/measurement_v0_closure_handoff.md`
  - `docs/downstream_usage_boundary_v0.md`
  - `outputs/real_k1_field_tests/*.json|*.yaml|*.csv`
- Existing paper workspace: none before P0.

## Search Status

External web search was available. No external skill content was installed verbatim. No external scripts were executed.

Relevant external sources inspected:

- OpenAI Codex Agent Skills documentation: `https://developers.openai.com/codex/skills`
- Open Agent Skills directory: `https://agentskill.sh/`
- Open Agent Skills Literature Review Agent page: `https://agentskill.sh/%40majiayu000/lit-review`
- Local skill search under `C:\Users\86138\.codex\skills` and `C:\Users\86138\Desktop`

## Scoring Rubric

Each score is 0-5:

1. Source trustworthiness.
2. Research workflow fit.
3. Citation integrity.
4. Claim-control strength.
5. Compatibility with Codex repo-scoped skills.
6. Low dependency burden.
7. Safety and auditability.
8. Robotics / engineering research relevance.

## Candidate Evaluation Table

| candidate_name | source_url_or_local_path | source_type | maintainer / author | license | last updated | executable code | external services | API keys | citation-verification rules | hallucination-prevention rules | claim tracking | literature matrix | BibTeX / DOI / arXiv metadata | robotics / engineering workflow | security risks | maintainability risks | fit for this project | scores 1-8 | decision | rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI Codex Agent Skills documentation | `https://developers.openai.com/codex/skills` | official documentation | OpenAI | documentation terms; not a skill payload | current page inspected 2026-06-09 | no | no runtime service required | no | no domain-specific rules | general skill authoring only | no | no | no | no | low | not a research skill | strong format guidance, no autoresearch workflow | 5,1,1,1,5,5,5,1 | adapt | Use for repo-scoped skill structure only. Does not solve citation or claim workflow. |
| Open Agent Skills directory | `https://agentskill.sh/` | skill directory / marketplace | agentskill.sh / Yuki Capital page footer | unclear per candidate | directory page inspected 2026-06-09 | varies | varies | varies | varies | varies | varies | varies | varies | varies | third-party install risk if used blindly | quality varies; many candidates not domain fit | useful for discovery, not direct inclusion | 3,2,1,1,3,2,3,1 | reject as install source | Directory is useful for discovery but not itself an inspectable project-specific skill. |
| Literature Review Agent | `https://agentskill.sh/%40majiayu000/lit-review` | third-party skill page | `majiayu000` listed on page | not confirmed from page | Updated June 1, 2026 | page says 1 `SKILL.md`; no code inspected locally | OpenAlex API workflow described | likely no hidden key, but external API dependence | partial literature database focus | not enough project-specific claim control | not apparent from inspected page | likely yes for literature database | likely metadata-oriented | sociology-focused, not robotics-specific | external API dependency; license unclear; content not imported | not tailored to K1 robotics claim registry | useful ideas but not safe to install verbatim | 3,3,3,2,3,2,3,1 | adapt/reject install | Good research-review direction, but domain mismatch, external API assumption, unclear license for repository inclusion. |
| Local `karpathy-guidelines` skill | `C:\Users\86138\Desktop\andrej-karpathy-skills-main\andrej-karpathy-skills-main\skills\karpathy-guidelines\SKILL.md` | local skill | local downloaded repo; upstream not inspected in this task | not evaluated | local file found 2026-06-09 | no | no | no | no | coding quality guidance only | no | no | no | no | low | not research workflow | useful coding discipline, no literature/citation workflow | 2,1,1,1,4,5,4,1 | reject | It is a coding-behavior skill, not autoresearch. |
| Custom repo-scoped `autoresearch` skill | `.agents/skills/autoresearch/SKILL.md` | custom repo skill | this repository | project-owned | created P0 | no | no network runtime behavior | no | yes | yes | yes | yes | yes | yes | low | maintained in repo; project-specific updates needed | best fit | 5,5,5,5,5,5,5,5 | accept | Safest option: instruction-only, no external code, explicit citation and claim governance, robotics-specific lens. |

## Decision

Accepted candidate: custom repo-scoped `autoresearch` skill.

Reason:

- No external candidate was both inspectable, license-clear, dependency-free, citation-safe, claim-registry-oriented, and robotics-specific.
- The project needs strict separation of verified facts, cited prior work, project evidence, hypotheses, planned experiments, and unsupported claims.
- An instruction-only repo skill has the lowest security risk and best governance fit.
