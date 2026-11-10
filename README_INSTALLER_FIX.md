# Installer compatibility fix

The earlier installer expected one exact `session_id = st.session_state["session_id"]` line. Your existing `frontend/views/voice.py` uses a different form, so it stopped validation before changing any project code.

This update inserts the Santali route at the beginning of `show_voice_page()` and initializes `session_id` safely. It also removes the old optional checkbox UI when it can identify the block safely.

## Apply

1. Extract this ZIP into the existing project root and overwrite `scripts/install_santali_unified.py`.
2. Confirm the prior package's `santali_unified_payload` folder still exists.
3. Run `python scripts/install_santali_unified.py`.

This patch does not contain another project or replace application files by itself. The installer validates the project and then applies the integration with backups.
