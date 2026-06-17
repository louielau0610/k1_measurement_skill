# scripts 实现文档

## 职责

`scripts/` 是项目 CLI 和实验编排层。脚本通常很薄，调用 `k1_measurement/`、`calibration_core/` 或 `platforms/` 的库函数，负责参数解析、文件路径、artifact 写入和实验流程串联。

## 编码注意

以下脚本含 BOM；刷新 AST 索引时使用 `utf-8-sig`：`scripts/analyze_m19_repeated_validation.py`、`scripts/generate_m19_figures.py`、`scripts/validate_future_data_collection_pack.py`、`scripts/validate_future_experiment_protocol_schema.py`。

## Session、采集与日志脚本

- `scripts/create_real_k1_field_session.py`: `parse_args` line 17，`main` line 24。
- `scripts/create_real_k1_field_test_pack.py`: `main` line 15。
- `scripts/start_real_k1_field_logger.py`: `parse_args` line 17，`main` line 24。
- `scripts/normalize_real_k1_logs.py`: `parse_args` line 17，`main` line 23。
- `scripts/run_forward_baseline.py`: `parse_args` line 18，`print_summary` line 26，`main` line 44。
- `scripts/run_booster_k1_measurement.py`: `main` line 29。
- `scripts/run_m19c_ros2_odometer_trials.py`: `speed_code` line 64，`trial_id` line 68，`generate_trial_plan` line 72，`phase_at` line 96，`write_csv` line 104，`record_for_trial` line 112，`run_trial_execute` line 133，`spin_until` line 197，`write_run_summary` line 205，`main` line 233。
- `scripts/run_m19c_ros2_odometer_smoke_trials.py`: `run_trials` line 23，`spin_for` line 85，`write_summary` line 93，`main` line 116。
- `scripts/run_m19c_sdk_state_smoke_trials.py`: `run_trials` line 22，`main` line 78。
- `scripts/log_k1_ros2_odometer_state.py`: `write_rows` line 32，`log_odometer_state` line 40，`write_summary` line 93，`main` line 128。
- `scripts/log_k1_sdk_state_smoke.py`: `try_import_sdk` line 18，`init_channel` line 27，`sample_transform` line 36，`make_sample_row` line 54，`log_standing_state` line 66，`main` line 115。
- `scripts/log_m23b_k1_compensation_trial.py`: `_mock_sample` line 49，`main` line 65。
- `scripts/log_m24b_s2_profile_refresh_trial.py`: `main` line 42，`build_mock_rows` line 79，`collect_ros2_rows` line 88，`mock_pose` line 136，`build_row` line 146，`_format_pose` line 172，`write_rows` line 178。
- `scripts/log_m24h_controlled_s2_replication_trial.py`: `main` line 43，`build_mock_rows` line 79，`collect_ros2_rows` line 88，`mock_pose` line 136，`build_row` line 146，`_format_pose` line 172，`write_rows` line 178。
- `scripts/run_m23b_k1_compensation_trials.py`: `main` line 62，`_dry_run` line 289，`_append_record` line 309，`_build_logger_command` line 332，`_build_sdk_command` line 357，`_command_for_display` line 383。
- `scripts/run_m24b_s2_profile_refresh_trials.py`: `main` line 49，`load_and_validate_plan` line 178，`dry_run` line 196，`append_record` line 212，`build_logger_command` line 244，`build_sdk_command` line 278，`_display` line 311。
- `scripts/run_m24h_controlled_s2_replication_trials.py`: `main` line 52，`_append_record` line 252。
- `scripts/send_m23b_k1_velocity_command.py`: `main` line 50，`_send_phase` line 161，`_write_command_log` line 175。

## Discovery 与校验脚本

- `scripts/check_environment.py`: `dependency_available` line 13，`main` line 17。
- `scripts/discover_ros2_topics.py`: `classify_topic` line 30，`classify_topics` line 53，`discover_topics` line 62，`print_summary` line 74，`save_grouped_topics` line 88，`parse_args` line 102，`main` line 108。
- `scripts/discover_k1_sdk_state_sources.py`: `public_methods` line 26，`public_fields` line 30，`try_import_sdk` line 34，`class_info` line 44，`discover` line 68，`render_report` line 111，`main` line 138。
- `scripts/validate_real_k1_topic_mapping.py`: `parse_args` line 17，`main` line 23。
- `scripts/validate_ros2_readonly_topics.py`: `parse_args` line 16，`main` line 27。
- `scripts/validate_profile_schema.py`: `load_json` line 19，`validate_profile` line 24，`parse_args` line 31，`main` line 44。
- `scripts/validate_velocity_response_dataset_schema.py`: `load_json` line 28，`resolve_path` line 33，`parse_args` line 40，`main` line 60。
- `scripts/validate_measurement_contract.py`: `main` line 36，`_print_result` line 105。
- `scripts/validate_measurement_manifest.py`: `main` line 18。
- `scripts/validate_measurement_module_closure.py`: `main` line 36。
- `scripts/validate_calibration_profile.py`: `validate_profile` line 30，`main` line 64。
- `scripts/validate_m19_annotation_intake.py`: `read_csv` line 55，`has_any_column` line 61，`first_value` line 65，`issue` line 72，`expected_and_invalid_ids` line 76，`contains_placeholder` line 92，`validate_annotation_intake` line 99，`write_outputs` line 210，`main` line 237。
- `scripts/validate_future_data_collection_pack.py`: 含 BOM，刷新时使用 `utf-8-sig`。
- `scripts/validate_future_experiment_protocol_schema.py`: 含 BOM，刷新时使用 `utf-8-sig`。

## 抽取、转换与 QC 脚本

- `scripts/extract_booster_k1_measurements.py`: `main` line 24。
- `scripts/extract_m19_measurements_from_ros2_odometer_logs.py`: `parse_float` line 44，`wrap_to_pi` line 57，`forward_displacement_m` line 61，`select_window` line 68，`extract_trial_measurement` line 78，`read_csv` line 125，`discover_log_files` line 130，`extract_from_logs` line 138，`render_report` line 193，`main` line 208。
- `scripts/extract_m19_measurements_from_sdk_state_logs.py`: `parse_float` line 35，`yaw_to_deg` line 48，`wrapped_yaw_diff_deg` line 58，`forward_displacement_m` line 63，`select_window` line 70，`extract_trial_measurement` line 82，`read_log_csv` line 112，`discover_log_files` line 117，`extract_from_logs` line 125，`main` line 189。
- `scripts/extract_m23b_k1_compensation_trials.py`: `main` line 35，`_extract_trial` line 96，`_build_report` line 168。
- `scripts/extract_m24b_s2_profile_refresh_trials.py`: `main` line 32，`read_trial_records` line 85，`read_json` line 92，`extract_record` line 98，`_float` line 172，`_wrap_to_pi` line 179，`build_report` line 183。
- `scripts/extract_m24f_corrected_s2_profile_refresh_trials.py`: `main` line 42，`extract_session` line 53，`extract_trial` line 93，`read_csv` line 161，`write_csv` line 166，`read_json` line 173，`to_float` line 177，`maybe_float` line 184，`wrap_to_pi` line 191，`build_report` line 195。
- `scripts/extract_m24h_controlled_s2_replication_trials.py`: `main` line 35，`_extract_trial` line 93，`_safe_floats` line 147，`_build_report` line 157。
- `scripts/convert_measurements_to_contract.py`: `main` line 34。
- `scripts/process_trial_logs.py`: `_validate_profile` line 28，`process_trial_logs` line 33，`parse_args` line 47，`main` line 54。
- `scripts/qc_booster_k1_measurement_session.py`: `main` line 22。
- `scripts/qc_m19_measurement_annotations.py`: `read_annotations` line 30，`has_measurement` line 36，`qc_annotations` line 40，`write_outputs` line 115，`main` line 141。
- `scripts/qc_m19_real_test_records.py`: `default_input_csv` line 34，`read_csv_records` line 42，`parse_bool` line 47，`parse_float` line 51，`debug_indicator` line 66，`resolve_data_path` line 77，`_extract_series` line 95，`_first_number` line 107，`compute_measurements_from_normalized` line 123，`build_qc` line 159，`_csv_write` line 257，`aggregate_rows` line 264，`write_outputs` line 334，`render_report` line 382，`render_missing_report` line 414，`main` line 430。
- `scripts/qc_m19c_ros2_odometer_measurement_run.py`: `read_csv` line 19，`count_phase_rows` line 26，`qc_measurement_run` line 30，`render_qc_report` line 131，`main` line 148。
- `scripts/qc_m23b_k1_compensation_session.py`: `main` line 24。
- `scripts/qc_m24b_s2_profile_refresh_session.py`: `main` line 21，`qc_session` line 40，`_read_csv` line 102，`_read_json` line 109，`_check` line 115，`build_report` line 121。
- `scripts/qc_m24f_corrected_s2_profile_refresh_session.py`: `main` line 16，`qc` line 25，`read_csv` line 78，`build_report` line 83。
- `scripts/qc_m24h_controlled_s2_replication_session.py`: `main` line 26，`_build_qc_md` line 137。

## 分析、建模与补偿脚本

- `scripts/analyze_real_k1_forward_velocity.py`: `load_yaml_record` line 63，`validate_record` line 73，`tracking_category` line 91，`analyze_trial` line 111，`analyze_record` line 131，`write_csv` line 190，`write_json` line 200，`render_markdown_report` line 214，`write_markdown_report` line 313，`write_plot` line 319，`run_analysis` line 352，`parse_args` line 368，`main` line 378。
- `scripts/analyze_m19c_empirical_response.py`: `parse_float` line 21，`surface_from_trial_id` line 29，`load_trial_surfaces` line 34，`read_measurements` line 41，`compute_cell_stats` line 62，`write_csv` line 101，`build_gold_profile` line 109，`analyze` line 142，`render_gold_profile` line 173，`render_report` line 183，`main` line 204。
- `scripts/analyze_m23c_k1_compensation_results.py`: `main` line 60，`analyze_session` line 81，`validate_inputs` line 143，`build_pair_rows` line 208，`build_per_velocity_rows` line 247，`build_aggregate_metrics` line 278，`compute_statistical_tests` line 310，`determine_claim_level` line 357，`build_report` line 368，`build_claim_boundary` line 450。
- `scripts/analyze_m24c_s2_profile_refresh.py`: `main` line 87，`analyze` line 114，`validate_session` line 168，`build_per_velocity` line 243，`build_old_new_comparison` line 285，`build_m23c_check` line 327，`decide` line 359，`build_summary` line 378，`build_candidate_profile` line 441，`build_ingestion_summary` line 465，`build_report` line 537。
- `scripts/analyze_m24f_corrected_s2_profile_refresh.py`: `main` line 26，`analyze` line 41，`per_velocity_summary` line 73，`old_new_comparison` line 112，`m23c_consistency` line 141，`faulty_vs_corrected` line 163，`decide` line 184，`build_summary` line 199，`build_candidate` line 231。
- `scripts/analyze_m24i_controlled_s2_replication.py`: `main` line 56，`_build_ingestion` line 160，`_verify_session` line 175，`_compute_per_velocity` line 234，`_compare_m24f` line 281，`_compare_m19c` line 313，`_compare_m23c` line 351，`_make_decision` line 397，`_build_profile_candidate` line 443，`_build_report` line 469。
- `scripts/classify_m19c_risk_regions.py`: `f` line 21，`classify_region` line 28，`risk_score` line 50，`classify_rows` line 62，`read_csv` line 72，`write_csv` line 77，`main` line 98。
- `scripts/build_velocity_response_dataset_v1.py`: `parse_args` line 26，`main` line 43。
- `scripts/run_velocity_response_model_v1.py`: `parse_args` line 32，`main` line 42。
- `scripts/run_navigation_risk_mapping_v1.py`: `parse_args` line 24，`main` line 33。
- `scripts/build_real_k1_velocity_profile.py`: `parse_args` line 26，`main` line 34。
- `scripts/offline_compensate_velocity.py`: `build_request` line 17，`main` line 32。
- `scripts/revised_offline_compensate_velocity.py`: `build_request` line 22，`main` line 42。
- `scripts/batch_offline_compensation_sweep.py`: `parse_velocities` line 21，`run_sweep` line 27，`write_outputs` line 46，`render_markdown` line 80，`main` line 98。
- `scripts/run_m23e_revised_compensator_sweep.py`: `main` line 49，`run_sweep` line 65，`build_report` line 123，`_fmt` line 158。
- `scripts/verify_offline_compensator.py`: `main` line 39，`_write_loro_csv` line 170，`_write_baseline_csv` line 182，`_write_policy_csv` line 194，`_build_edge_case_md` line 205，`_build_report_md` line 223。
- `scripts/audit_m23f_revised_compensator.py`: `main` line 48，`audit` line 60，`build_audit_table` line 80，`build_summary` line 127，`classify_readiness` line 168，`build_second_validation_recommendation` line 187，`build_audit_report` line 212。
- `scripts/diagnose_m23d_compensation_failure.py`: `main` line 42，`diagnose` line 55，`build_failure_mode_table` line 73，`build_failure_mode_summary` line 124，`build_diagnosis_summary` line 177，`build_report` line 195。
- `scripts/audit_m24d_response_consistency.py`: `main` line 59，`audit` line 76，`build_disagreement_rows` line 102，`build_assumption_rows` line 146，`build_diagnosis` line 175，`build_adoption_decision` line 213，`build_summary` line 235。
- `scripts/audit_m24e_extraction_method.py`: `main` line 66，`_inspect_raw_log` line 194，`_extract_with_method` line 271，`_compute_from_subset` line 313，`_build_method_comparison` line 382，`_crosscheck_with_m24c` line 427，`_compute_anomaly_summary` line 463，`_make_extraction_decision` line 514。

## 计划、报告和展示脚本

- `scripts/generate_cross_platform_trial_plan.py`: `parse_csv_text` line 19，`parse_speeds` line 23，`default_surfaces_and_speeds` line 27，`build_plan` line 34，`write_csv` line 68，`main` line 87。
- `scripts/generate_dummy_raw_log.py`: `_phase_for_time` line 44，`_format_row` line 52，`generate_dummy_raw_log` line 62，`parse_args` line 138，`main` line 144。
- `scripts/generate_dummy_profile.py`: `main` line 11。
- `scripts/generate_measurement_report.py`: `parse_args` line 20，`main` line 27。
- `scripts/generate_research_pipeline_evaluation_v1.py`: `parse_args` line 25，`main` line 35。
- `scripts/generate_m19r_b_completion_pack.py`: `default_input_csv` line 41，`read_csv` line 47，`speed_code` line 52，`cell_key` line 56，`derive_replacement_plan` line 61，`annotation_rows` line 102，`write_csv` line 153，`render_plan` line 161，`generate_pack` line 187，`main` line 228。
- `scripts/generate_m19r_c_prep_valid_annotations.py`: `read_csv` line 37，`write_csv` line 42，`is_execution_valid` line 50，`surface_id` line 54，`build_valid_annotation_rows` line 58，`build_worklist` line 86，`summarize` line 110，`render_worklist` line 142，`render_report` line 175，`generate_prep` line 211，`main` line 227。
- `scripts/generate_m23a_k1_compensation_experiment_plan.py`: `main` line 46，`_build_trial_plan` line 154，`_write_csv` line 215，`_validate_trial_plan` line 227，`_build_executable_trials` line 247，`_build_plan_data` line 274，`_build_executable_summary` line 324，`_build_plan_md` line 364，`_build_analysis_md` line 428，`_build_executable_summary_md` line 479。
- `scripts/generate_m24a_s2_profile_refresh_plan.py`: `main` line 35，`build_plan` line 79，`write_csv` line 100，`build_summary` line 107，`build_markdown` line 158。
- `scripts/generate_m24g_controlled_s2_replication_plan.py`: `main` line 40，`build_plan` line 76，`build_trials` line 84，`write_csv` line 109，`build_summary` line 116，`build_manifest` line 155，`build_plan_markdown` line 174，`build_manifest_markdown` line 220。
- `scripts/list_calibration_platforms.py`: `main` line 16。
- `scripts/show_calibration_profile.py`: `profile_for_platform` line 17，`main` line 37。
- `scripts/show_measurement_module_status.py`: `load_status` line 16，`main` line 20。
## M25 CLI Entry Points

- `scripts/validate_m25_full_range_velocity_config.py:16` validates the M25 YAML config and returns JSON-compatible errors.
- `scripts/plan_full_range_velocity_profile.py:16` generates exploration or formal JSON/Markdown planning artifacts under `outputs/full_range_velocity_profile/`.
- `scripts/validate_m25_collected_session.py:16` validates collected trial rows against the M25 domain and extraction contract.
- `scripts/build_m25_candidate_profile.py:16` builds or dry-runs a candidate profile from valid collected rows.
- `scripts/audit_m25_historical_compatibility.py:23` audits historical CSV/JSON rows for valid-speed reuse as `historical_reference_only`.

## M25-R CLI Entry Points

- `scripts/validate_m25_safe_speed_confirmation.py:16` validates operator safe-speed evidence files.
- `scripts/validate_m25_real_collection_preflight.py:16` validates real-collection readiness and exits nonzero while blocked.
- `scripts/prepare_m25r_collection_package.py:16` writes exploration/formal collection package JSON and Markdown artifacts.
- `scripts/evaluate_m25_exploration_gate.py:17` evaluates exploration extraction readiness for formal collection without M26 model fitting.

## M26-E Packaging and Release Gate Scripts

- `scripts/run_tests_hermetically.py`: `git_status` line 29, `run_child` line 42, `build_summary` line 52, `parse_args` line 73, `main` line 83, `_human_summary` line 133.
- `scripts/run_local_release_gate.py`: `run` line 29, `git_status` line 40, `check_repo_clean` line 47, `validate_packaging_metadata` line 65, `inspect_artifacts` line 95, `build_check` line 121, `install_smoke` line 132, `no_vendor_check` line 146, `check_order` line 167, `write_summary` line 186, `main` line 191.
- `calibration_skill/cli.py`: package console entry point `main` line 27, parser construction `_parser` line 55, validation `_validate` line 83, dry-run invocation `_invoke` line 111, generated example payloads `_example_request` line 203.

M26-E scripts are packaging and validation orchestration only. They do not connect to hardware, call vendor processes, start DDS, send UDP, or restore repository state automatically.
