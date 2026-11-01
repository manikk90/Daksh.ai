# v3 validation report

**Result:** PASS for the bounded source-inclusion and packaging checks below. This is NOT a guarantee of exhaustive historical content, source correctness, installed behavior or media quality.

| Check | Actual result |
|---|---|
| status | PASS_BOUNDED_DOCUMENTATION_AND_INTEGRITY_CHECKS |
| review_kind | same-context source/dossier audit; no independent worker |
| exact_original_sources_preserved | 225 |
| custom_source_files_compared_to_current_mount | 217 |
| custom_source_missing_or_changed | 0 |
| main_agent_and_helper_dossiers | 9 |
| full_markdown_modules_included | 73 |
| saved_lesson_records_included | 97 |
| bounded_text_coverage_checks | 44 |
| bounded_text_coverage_checks_passed | 44 |
| previous_v2_main_dossiers_preserved | 9 |
| original_single_skill_archives_unchanged | 8 |
| new_runtime_records | 3 |
| generated_links_checked | 393 |
| unresolved_generated_links | 0 |
| json_parsed_at_validation_stage | 76 |
| python_syntax_checked | 71 |
| exported_font_files | 0 |
| original_software_regression_suites_rerun | False |
| live_scheduler_or_accounts_checked | False |
| installed_agents_changed | False |
| media_tests | 0 |
| writer_original_source_available | False |
| complete_chat_archive_available | False |

## What was tested
All 73 transformed full Markdown source bodies were matched against the built dossiers during the build, not just their filenames. The reusable verify_content.py checks source hashes, module anchors and the 44 specified content markers. The separate verify_export.py checks complete exported-file hashes and nested archive integrity. Exact original custom files also matched the currently mounted originals.

## What was not tested
No fresh independent agent reviewed this export. No actual model/API/account execution, scheduling, publication, imagery, audio or lip-sync test ran. Original software regression suites were not rerun; parser/structure tests do not establish behavioral correctness. Historical test outcomes in source ledgers remain historical records. Source Markdown headings/relative links were rebased for readability; original source files remain byte-exact.

AI Writer's original installed source and exhaustive raw chat/media history remain unavailable. The 100-preview collection was not recovered. See audit/AUDIT_REPORT.md for the substantive findings and audit/COVERAGE_MATRIX.md for the test boundaries.
