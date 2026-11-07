# Pixel Office — Windows offline worker prototype

This is **not yet a one-click autonomous AI factory**. It is a small SQLite-backed persistent job queue with Kiro (offline story outline template) and Zek (quality gate template). No ElevenLabs integration, autonomous reasoning, or video rendering yet.

## Windows
1. Install Python 3.10+ if missing.
2. Download repository ZIP and extract.
3. Open `office/runtime/START_WINDOWS.bat`.
4. It initializes the database, enqueues one Kiro story-outline task, processes it, and prints status. It does **not** install an always-on service or run at startup.

## Tests
`cd office/runtime && python -m unittest test_queue.py`

## Next steps
- Replace offline templates with reviewed model-provider integration and a strict budget guard.
- Add real asset-based puppet renderer, narration, subtitle compositor and FFmpeg verification.
- Add a user-approved Windows Task Scheduler installation after worker reliability is tested.
- Store credentials in OS secrets or environment variables, never in repository.
- Human approval required for publishing; paid API calls disabled by default.
