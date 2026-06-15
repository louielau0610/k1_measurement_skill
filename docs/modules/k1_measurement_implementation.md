# k1_measurement 实现文档

## 职责

`k1_measurement/` 是测量阶段的主包，覆盖 dry-run 命令安全、field session、只读 ROS2 discovery、topic mapping、日志归一化、测量指标、profile、dataset、响应模型、风险映射、报告和图像输出。

## 函数与类索引

### `k1_measurement/command_runner.py`

- `VelocityCommand`: line 13，前向速度命令数据结构。
- `CommandSafetyError`: line 21，安全校验异常。
- `K1CommandRunner`: line 25，默认 dry-run 的命令执行器。
- `CommandRunner`: line 137，兼容旧调用的包装器。

### `k1_measurement/field_logging.py`

- `build_rosbag_record_command`: line 18，构造 `ros2 bag record` 命令。
- `start_field_logger`: line 23，启动只读 rosbag record 并写 run summary。

### `k1_measurement/field_session.py`

- `_utc_now`: line 23，生成 UTC 时间戳。
- `_git_commit`: line 27，读取当前 git commit。
- `_copy_or_write`: line 41，复制模板或写默认内容。
- `create_field_session`: line 49，创建真实 K1 field session 目录。
- `load_ground_truth_sheet`: line 101，读取 ground truth sheet。
- `validate_ground_truth_columns`: line 106，校验 ground truth 列。
- `summarize_ground_truth_sheet`: line 114，汇总 ground truth 行。
- `load_session_config`: line 148，读取 session 配置。

### `k1_measurement/field_test_pack.py`

- `write_ground_truth_trial_sheet`: line 34，写 ground truth trial sheet。

### `k1_measurement/logger_node.py`

- `K1MeasurementLogger`: line 45，真实 logger 前的安全骨架。
- `LoggerNodePlaceholder`: line 151，兼容旧接口且无 ROS2 副作用。

### `k1_measurement/m19_validation_schema.py`

- 当前文件含 BOM；用 `utf-8` 直接 AST 解析会在 line 1 报 `U+FEFF`。刷新索引时使用 `utf-8-sig`。

### `k1_measurement/metrics.py`

- `_validate_time_interval`: line 24，校验时间区间。
- `_ensure_numeric`: line 31，数值转换。
- `_mean`: line 37，均值。
- `_sample_std`: line 41，样本标准差。
- `compute_actual_velocity`: line 47，根据位移和时间计算实际速度。
- `compute_speed_gain`: line 56，计算 actual/commanded。
- `compute_absolute_error`: line 64，计算速度误差。
- `compute_relative_error`: line 70，计算相对误差。
- `compute_lateral_drift_rate`: line 78，计算横向漂移率。
- `compute_yaw_drift_rate`: line 87，计算 yaw 漂移率。
- `compute_tracking_rmse`: line 96，计算 tracking RMSE。
- `summarize_trials`: line 112，按命令速度汇总重复试验。
- `velocity_error`: line 157，兼容函数，返回 actual - commanded。
- `mean_velocity`: line 163，速度均值。
- `population_std`: line 171，总体标准差。
- `summarize_velocity_samples`: line 183，汇总单个 command speed 的速度样本。

### `k1_measurement/navigation_risk_mapping.py`

- `NavigationRiskAssessment`: line 31，单条风险评估。
- `NavigationRiskMapEvaluation`: line 55，风险图评估汇总。
- `load_response_model_predictions`: line 66，读取响应模型预测。
- `extract_predictions`: line 75，抽取 prediction records。
- `NavigationRiskMapper`: line 93，生成 advisory risk assessment。
- `assessment_to_dict`: line 278，序列化评估。
- `evaluation_to_dict`: line 282，序列化汇总。
- `build_risk_map_payload`: line 286，生成风险图 payload。
- `build_risk_evaluation_payload`: line 320，生成风险评估 payload。
- `_contains_any`: line 341，关键字匹配。
- `_optional_str`: line 348，可选字符串转换。
- `_optional_float`: line 352，可选浮点转换。
- `_max_risk`: line 356，风险等级合成。

### `k1_measurement/profile_builder.py`

- `_coerce_row`: line 49，CSV row 类型转换。
- `load_raw_log`: line 59，读取 raw measurement CSV。
- `_group_by_trial`: line 67，按 trial 分组。
- `_stable_command_rows`: line 74，筛选稳定命令段。
- `_summarize_single_trial`: line 88，汇总单次 trial。
- `_environment_from_rows`: line 126，从 rows 提取环境。
- `build_environment_profile`: line 138，从 raw log 构造 profile。
- `save_environment_profile`: line 199，写 profile JSON。
- `build_measurement_profile`: line 207，兼容旧 dummy 脚本。

### `k1_measurement/real_log_normalizer.py`

- `_field`: line 32，字段读取。
- `_first_available`: line 38，选择首个可用字段。
- `_topic_rows`: line 45，读取 topic rows。
- `_ground_truth_by_trial`: line 54，建立 trial ground truth 索引。
- `normalize_exported_csv_logs`: line 61，归一化 exported CSV logs。

### `k1_measurement/report_generator.py`

- `load_profile`: line 14，读取 profile JSON。
- `_bool_text`: line 31，布尔文本格式化。
- `_format_number`: line 35，数字格式化。
- `_warnings`: line 41，提取 warning。
- `_contains_dummy_warning`: line 48，识别 dummy warning。
- `generate_markdown_report`: line 52，生成中文优先 Markdown 报告。
- `save_markdown_report`: line 181，保存报告。
- `generate_report_from_profile`: line 189，读取 profile 并生成报告。
- `render_markdown_summary`: line 198，兼容旧调用。

### `k1_measurement/research_dataset_schema.py`

- `load_velocity_response_schema`: line 45，加载 schema。
- `validate_velocity_response_schema`: line 54，校验 schema 本体。
- `validate_velocity_response_record`: line 98，校验 response record。
- `_validate_dataset_record_collection`: line 122，校验 record 集合。
- `_validate_single_velocity_response_record`: line 148，校验单条 record。
- `assert_velocity_response_record_valid`: line 173，断言式校验。
- `get_disallowed_fields`: line 182，读取禁用字段。
- `_get_required_record_fields`: line 194，读取必填字段。
- `_get_either_or_groups`: line 203，读取 either/or 组。
- `_get_false_only_fields`: line 217，读取只能为 false 的字段。
- `_iter_disallowed_record_fields`: line 226，遍历禁用字段。
- `_find_required_field_paths`: line 244，查找必填路径。

### `k1_measurement/research_pipeline_evaluation.py`

- `ResearchPipelineArtifact`: line 15，artifact 描述。
- `ResearchPipelineEvaluation`: line 27，pipeline 评估汇总。
- `load_json`: line 44，读取 JSON。
- `collect_research_artifacts`: line 53，收集 research artifacts。
- `evaluate_research_pipeline`: line 81，生成 pipeline 评估。
- `build_artifact_table`: line 204，构建 artifact table。
- `write_markdown_report`: line 224，写 Markdown report。
- `write_json_report`: line 253，写 JSON report。
- `write_artifact_table_markdown`: line 305，写 artifact table Markdown。
- `write_limitations_markdown`: line 319，写 limitations Markdown。
- `_write_json`: line 337，写 JSON helper。
- `_write_text`: line 345，写文本 helper。
- `_list_section`: line 351，渲染列表段。
- `_chapter_for_milestone`: line 357，milestone 到章节映射。

### `k1_measurement/ros2_readonly_validator.py`

- `_utc_now`: line 32，UTC 时间。
- `_preview`: line 36，输出预览。
- `_run_command`: line 40，执行只读命令。
- `check_ros2_availability`: line 54，检查 `ros2 --help`。
- `parse_topic_list`: line 95，解析 `ros2 topic list`。
- `parse_topic_list_with_types`: line 106，解析 `ros2 topic list -t`。
- `_result_payload`: line 128，命令结果 payload。
- `discover_topics`: line 137，运行只读 discovery。
- `classify_topic`: line 191，保守分类 candidate topic。
- `classify_topics`: line 216，按候选类型分组。
- `inspect_message_interfaces`: line 225，读取 message interface。
- `planned_print_only_report`: line 264，生成 dry-run discovery report。
- `build_validation_report`: line 294，生成 JSON/Markdown report。
- `write_reports`: line 353，写 report 文件。
- `render_markdown_report`: line 365，渲染中文优先 field review 摘要。

### `k1_measurement/topic_mapping.py`

- `load_topic_mapping`: line 16，读取 mapping。
- `is_tbd`: line 24，识别 TBD。
- `confirmed_topics`: line 28，提取已确认 topics。
- `validate_topic_mapping`: line 37，校验 mapping 且不假设真实 topic。

### `k1_measurement/trial_manager.py`

- `TrialSpec`: line 13，兼容 compact trial spec。
- `K1TrialManager`: line 21，生成/校验 dry-run-only 前向 baseline trial plan。
- `build_forward_trial_plan`: line 130，兼容函数。

### `k1_measurement/velocity_profile.py`

- `load_json`: line 17，读取 JSON。
- `load_yaml`: line 27，读取 YAML。
- `_topic_profile`: line 37，topic profile。
- `_trial_point`: line 45，trial point。
- `build_velocity_profile`: line 62，构建 measurement-only velocity profile。
- `validate_velocity_profile`: line 155，校验 profile contract 和安全 flags。
- `write_json`: line 201，稳定格式写 JSON。

### `k1_measurement/velocity_response_dataset_builder.py`

- `load_measurement_v0_artifacts`: line 23，读取 measurement v0 artifacts。
- `build_velocity_response_dataset_v1`: line 64，构建 dataset v1。
- `build_future_trial_template`: line 154，生成 future trial template。
- `validate_built_dataset`: line 202，校验生成的数据集。
- `write_json`: line 211，写 JSON。
- `build_validation_report`: line 219，构建 validation report。
- `_build_records`: line 249，构建 records。
- `_load_json`: line 331，读取 JSON。
- `_load_csv`: line 339，读取 CSV。
- `_environment_from_sources`: line 344，环境来源。
- `_localization_source`: line 353，定位来源。
- `_collect_limitations`: line 365，收集限制。
- `_downstream_flags`: line 381，下游 flags。
- `_confidence_label`: line 393，置信标签。
- `_first_string`: line 402，首个字符串。
- `_is_date`: line 409，日期判断。

### `k1_measurement/velocity_response_model.py`

- `VelocityResponsePrediction`: line 20，响应预测。
- `VelocityResponseModelEvaluation`: line 40，模型评估。
- `load_velocity_response_dataset`: line 51，读取 dataset。
- `extract_velocity_response_records`: line 60，抽取 records。
- `VelocityResponseModel`: line 72，响应模型。
- `prediction_to_dict`: line 430，序列化 prediction。
- `evaluation_to_dict`: line 434，序列化 evaluation。
- `record_id`: line 438，record id。
- `_has_numeric_response`: line 442，数值响应判断。
- `_label`: line 446，标签转换。
- `_linear_interpolate`: line 451，线性插值。
- `_normalized_confidence`: line 458，置信归一化。
- `_model_limitations`: line 468，模型限制说明。

### `k1_measurement/visualization.py`

- `_ensure_output_dir`: line 12，确保输出目录。
- `_try_matplotlib`: line 18，尝试导入 matplotlib。
- `_png_chunk`: line 30，PNG chunk helper。
- `_write_png`: line 34，写 PNG。
- `_set_pixel`: line 44，像素写入。
- `_draw_line`: line 50，fallback 画线。
- `_fallback_line_plot`: line 80，无 matplotlib 时画简图。
- `load_velocity_profile`: line 115，读取 profile 中的 velocity_profile。
- `_records`: line 122，读取 records。
- `_has_columns`: line 130，列存在判断。
- `_column`: line 134，取列。
- `generate_command_vs_actual_velocity_plot`: line 138，命令/实际速度图。
- `generate_speed_gain_plot`: line 166，speed gain 图。
- `generate_trial_time_series_plot`: line 194，trial 时间序列图。
- `generate_drift_plot`: line 221，漂移图。
- `generate_measurement_plots`: line 252，生成所有可用静态图。
## M25 Full-Range Velocity Profiling

- `k1_measurement/full_range_velocity_profile.py:30` defines `M25ValidationError`, the machine-readable validation exception used by M25 CLIs.
- `k1_measurement/full_range_velocity_profile.py:42` defines `ValidSpeedDomain`, including `valid_command_speed_min`, unresolved `safe_command_speed_max`, and the high-priority actual-speed interval.
- `k1_measurement/full_range_velocity_profile.py:121` defines `M25Config`, the typed planner/config wrapper for exploration points, formal grid, repeats, random seed, and randomization mode.
- `k1_measurement/full_range_velocity_profile.py:173` loads YAML M25 configuration.
- `k1_measurement/full_range_velocity_profile.py:181` validates canonical command grids for finite positive speeds, duplicates, strict ordering, and domain limits.
- `k1_measurement/full_range_velocity_profile.py:209` builds blocked or executable exploration/formal plans.
- `k1_measurement/full_range_velocity_profile.py:252` and `k1_measurement/full_range_velocity_profile.py:291` render and write JSON/Markdown planning artifacts.
- `k1_measurement/full_range_velocity_profile.py:300` validates collected session rows against the M25 contract.
- `k1_measurement/full_range_velocity_profile.py:335` builds candidate full-range velocity profiles without marking them validated.
- `k1_measurement/full_range_velocity_profile.py:383` rejects targets outside the observed reachable actual-speed interval.
- `k1_measurement/full_range_velocity_profile.py:393` audits historical rows as `historical_reference_only` without deadzone inference.

## M25-R Real Collection Preflight

- `k1_measurement/m25_real_collection_preflight.py:30` defines `SafeSpeedConfirmation`, the operator/supervisor evidence contract for resolving `safe_command_speed_max`.
- `k1_measurement/m25_real_collection_preflight.py:86` validates safe-speed confirmation files and rejects unresolved placeholders or unsupported evidence types.
- `k1_measurement/m25_real_collection_preflight.py:101` evaluates real-collection preflight readiness, including speed domain, timing, output writability, mappings, safeguards, hashes, and trial counts.
- `k1_measurement/m25_real_collection_preflight.py:210` builds exploration/formal collection packages without executing robot motion.
- `k1_measurement/m25_real_collection_preflight.py:241` writes package JSON/Markdown artifacts.
- `k1_measurement/m25_real_collection_preflight.py:276` evaluates the exploration-to-formal gate without fitting an M26 model.
- `k1_measurement/m25_real_collection_preflight.py:326` and `k1_measurement/m25_real_collection_preflight.py:330` provide deterministic file/object hashes for reproducibility metadata.
