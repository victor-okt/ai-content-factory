# Pixel Office + VO1995: one VPS deployment

**Current state:** This is a **safe, runnable worker foundation**, NOT an autonomous video factory. The existing Pixel Office and VO1995 already live in the same GitHub repository `victor-okt/ai-content-factory`; no repository merge is necessary.

## Setup on a VPS
Prerequisites: Linux VPS with Docker Engine and Compose plugin installed, a GitHub clone of this repository. Suggested first trial: 2 vCPU, 2 GB RAM, 20 GB disk; choose 4 GB RAM if running more than this minimal worker. No GPU is needed for this heartbeat service or simple SVG/FFmpeg work.

```sh
git clone https://github.com/victor-okt/ai-content-factory.git
cd ai-content-factory
docker compose -f deploy/vps/docker-compose.yml up -d --build
docker compose -f deploy/vps/docker-compose.yml logs -f
```

The worker writes `status.json` every five minutes into a persistent Docker volume. It does not call paid APIs, post social media content, or pretend to render finished videos. It uses no exposed ports.

## Integration roadmap
1. Connect Nova/Kai/Mira/Rio/Sora/Dex to a durable SQLite task queue with retries and budgets.
2. Feed story bank and motion library to a genuine 2D puppet renderer.
3. Supply transparent approved Kitsune/Wukong/Tengu art and tested body-part anchors.
4. Add ElevenLabs TTS only after user configures an API key in VPS secrets; never commit keys.
5. Render FFmpeg MP4 and verify dimensions, duration, audio, and subtitle safe area.
6. Require human approval before publishing; implement cost limits and alerts.

## Important
A low-cost CPU VPS cannot run large generative video models like Wan/Seedance at usable speeds. A GPU service would be a separate optional expense requiring explicit approval. The worker is not a substitute for an AI reasoning model; model inference requires a configured local or external provider.

## Safety
- Do not expose Docker or a dashboard port publicly without authentication and HTTPS.
- Never put API keys into GitHub commits or chat.
- No auto-publishing and no paid API use by default.
- Do not buy a VPS without reviewing the provider and monthly price.
