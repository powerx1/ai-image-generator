<!-- Copilot instructions for AI coding agents -->

# Copilot instructions — AI-Image-Web workspace

Summary
- Purpose: small static front-end (`AI-Image-Web`) + lightweight FastAPI proxy (`AI-Image-Web/api.py`) that forwards requests to a third-party `stable-diffusion-webui` service in this workspace.

Quick architecture
- Frontend: `AI-Image-Web/index.html` + `AI-Image-Web/control.js` (static UI). The browser sends a POST to the local API at `http://127.0.0.1:8000/generate`.
- Backend: `AI-Image-Web/api.py` (FastAPI). It accepts form data, optionally an `init_image`, and forwards to the Stable Diffusion WebUI JSON API endpoints: `/sdapi/v1/txt2img` or `/sdapi/v1/img2img`.
- Stable Diffusion: provided by the `stable-diffusion-webui` directory. The FastAPI app expects that service at `STABLE_URL` (env var), default `http://127.0.0.1:7861`.

What an agent should know when editing code
- Changing front-end request behavior: update `AI-Image-Web/control.js` (fetch URL, form fields, `mode` flag).
- Changing backend payload or behavior: edit `AI-Image-Web/api.py`. Note: img2img expects `init_images` as a data URI (`data:image/png;base64,...`). The backend saves returned image bytes into `output/`.
- Ports/conventions: static server `AI-Image-Web/serve.py` defaults to port `5500`; the FastAPI app is expected on `8000`; webui defaults to `7861` here. Use `STABLE_URL` env var to override.

Developer workflows (how to run things)
- Serve the static frontend (quick):
```bash
python AI-Image-Web/serve.py 5500
# open http://localhost:5500/index.html
```
- Run the API (FastAPI/uvicorn):
```bash
# from workspace root
uvicorn AI-Image-Web.api:app --host 0.0.0.0 --port 8000 --reload
```
- Run Stable Diffusion WebUI: use the provided launcher in `stable-diffusion-webui` (e.g. `webui-user.bat` on Windows or `webui.sh` on Unix). Ensure it exposes the `sdapi` endpoints (default port shown in that component's README).

Important patterns & gotchas
- The frontend posts form-encoded data (FormData) and expects JSON with an `image` base64 string in the response. See `AI-Image-Web/control.js` and `AI-Image-Web/api.py`.
- The API sets permissive CORS in `api.py` (allow_origins=["*"]). If you tighten CORS, update the front-end host accordingly.
- Timeouts: `api.py` uses `requests.post(..., timeout=120)`. Long generations can hit this — increase if adding longer-running flows.
- File saving: generated images go to `output/` relative to the working directory. Keep this in mind for CI or containerized runs.

Integration points to inspect when changing behavior
- Frontend ↔ API: `AI-Image-Web/control.js` → `AI-Image-Web/api.py` (`/generate`).
- API ↔ SD WebUI: `AI-Image-Web/api.py` forwards to `{STABLE_URL}/sdapi/v1/txt2img` or `.../img2img`.
- Stable WebUI runner: `stable-diffusion-webui/webui-user.bat` and `webui.sh` are the usual launchers; configuration and third-party extensions live under `stable-diffusion-webui/configs`, `extensions`, and `scripts`.

Sample requests (useful for tests & quick edits)
- curl example (text2img):
```bash
curl -X POST "http://127.0.0.1:8000/generate" \
  -F "prompt=An astronaut riding a horse" \
  -F "steps=30" -F "cfg_scale=7"
```
- img2img requires an `init_image` file in the multipart form; `api.py` converts it to a base64 data URI before forwarding.

Where to look first when debugging
- UI issues: [AI-Image-Web/index.html](AI-Image-Web/index.html) and [AI-Image-Web/control.js](AI-Image-Web/control.js).
- API issues: [AI-Image-Web/api.py](AI-Image-Web/api.py) (payload mapping, STABLE_URL env var, saving `output/`).
- SD WebUI issues: [stable-diffusion-webui/README.md](stable-diffusion-webui/README.md) and `webui-user.bat` / `webui.sh`.

If you change endpoints or payload shapes
- Update both the front-end `fetch()` in `AI-Image-Web/control.js` and the FastAPI `generate` signature in `AI-Image-Web/api.py` together. Include an integration test (curl or small script) that POSTs a sample prompt and verifies a base64 `image` key exists in the JSON response.

Questions for maintainers (ask before major changes)
- Do you expect `AI-Image-Web` to remain a static demo, or should we add server-side rendering, authentication, or queueing for long jobs?
- Preferred default ports and deployment target (container vs local Windows runner)?

---
If anything here is unclear or you want more examples (unit tests, CI steps, or a minimal integration test), say which area to expand and I will iterate.
