# 🤖 OpenCode Agent Guidelines (AGENTS.md)

Welcome, AI Agent! You are operating within the **Smart Home Project** repository. This project integrates Face Recognition, Voice Control, Security Cameras, and a Mobile App into a cohesive, secure, and robust system.

---

## 🎯 1. Project Context & Core Functions

This smart home system relies on four foundational pillars:
1. **Face Recognition**: Owner identification under varied conditions (lighting, motion blur, masks). Unlocks secondary functions and alerts on unknown faces.
2. **Voice Control**: Speech-to-text engine routing commands for lights, blinds, and locks. Requires local processing capabilities with cloud fallback.
3. **Security Camera**: Multi-camera feed ingestion, fusion, low-light enhancement, and live mobile streaming.
4. **Mobile App**: Centralized hub for camera viewing, manual device control, access log viewing, and real-time push alerts.

### Operational Scenarios
- **No one home**: Standby mode (low power consumption, high security alert threshold).
- **Only host**: Owner recognized -> full automated interaction suite available.
- **Host + guests**: Temporary access granted via app. Guests can use limited voice controls post-unlock.
- **Unknown face/mask**: Immediate push alert sent to owner; system locks down until owner decides action via app.

---

## 🏗️ 2. Architecture & Design Guidance

- **Modular Architecture**: Strictly separate domains into modules: `capture`, `face-recognition`, `voice`, and `app-backend`. Ensure loose coupling.
- **Robustness**: Implement multi-camera fusion, adaptive lighting algorithms (auto-exposure tuning), and mask-aware ML models.
- **Security (CRITICAL)**: End-to-end encryption (E2EE) for video streams (WebRTC/RTSP over TLS). Store facial templates locally on edge devices (never in the cloud).
- **UX**: Keep voice confirmations concise ("Door locked"). Allow customizable voice trigger phrases.

---

## 🛠️ 3. Build, Lint, and Test Commands

*Note: The project utilizes Python for ML/Vision and Node.js/TypeScript for App/Backend. Use the appropriate tools.*

### Python (ML / Voice / Vision)
- **Install Dependencies**: `pip install -r requirements.txt` or `poetry install`
- **Linting & Formatting**: 
  - `black . --check` (Formatting)
  - `flake8 . --max-line-length=88` (Linting)
  - `mypy . --strict` (Type checking)
- **Running All Tests**: `pytest`
- **Running a Single Test**: `pytest path/to/test_file.py::test_function_name -v`
- **Testing Scenarios**: Use `scripts/test_low_light.sh` and `scripts/test_masked_faces.sh`.

### TypeScript/Node (Backend / Mobile App)
- **Install Dependencies**: `npm install`
- **Linting & Formatting**: 
  - `npm run lint` (ESLint)
  - `npm run format` (Prettier)
- **Running All Tests**: `npm test`
- **Running a Single Test**: `npx jest path/to/test.ts -t "Test Name"`
- **Type Checking**: `npx tsc --noEmit`

---

## ✍️ 4. Code Style & Development Guidelines

### 4.1. Typing & Signatures
- **Python**: Strict typing is mandatory. Use `typing` module extensively (`List`, `Dict`, `Optional`, `Union`).
- **TypeScript**: `strict: true` in `tsconfig.json`. Avoid `any`; use `unknown` if the type is truly dynamic, then narrow it.

### 4.2. Error Handling
- Never use silent `catch` blocks or empty `except:` clauses.
- Always log errors with context (`logger.error("Camera feed failed", exc_info=True)`).
- For hardware failures (e.g., camera disconnect, mic failure), implement graceful degradation, exponential backoff, and retry logic.

### 4.3. Naming Conventions
- **Python**: `snake_case` for variables/functions, `PascalCase` for classes. Constant variables should be `UPPER_SNAKE_CASE`.
- **TypeScript**: `camelCase` for variables/functions, `PascalCase` for classes/interfaces.
- **Descriptive Names**: `recognize_face_with_mask()` is required over `process_face()`.

### 4.4. Imports & Modules
- Group imports: Standard Library -> Third Party -> Local Application.
- In Python, use `isort`. No wildcard imports (`from module import *`).

### 4.5. Security First
- Never hardcode credentials, API keys, or stream URLs in the source code.
- Use `.env` files and environment variables. Provide `.env.example` for local setup.
- Validate all incoming data from the mobile app to prevent injection attacks.

---

## 🧠 5. Machine Learning & Computer Vision Rules

- **Resource Management**: Always explicitly release camera resources (`cap.release()`) and destroy OpenCV windows in `finally` blocks.
- **Tensor Operations**: Prefer batched tensor operations over loops when processing frames.
- **Model Checkpoints**: Store model weights in `models/weights/`. Do not commit `.pt`, `.onnx`, or `.h5` files to Git. Use Git LFS if necessary.
- **Inference**: Prioritize latency. Target < 200ms for face recognition inference.

---

## 🗣️ 6. Agent Interaction Style & Instructions

When assisting the user in this repository, you **MUST** adhere to the following interaction rules:

1. **Ask Clarifying Questions**: Before writing massive implementations or making architectural assumptions, stop and ask the user to clarify specifics.
2. **Step-by-Step Guidance**: Provide instructions and implementation steps clearly, sequentially, and logically.
3. **Code Snippets**: Always provide functional, robust code snippets. Prefer Linux bash commands for infrastructure, setups, and execution.
4. **Summarization**: Use tables or bullet points to summarize decisions, trade-offs, architectures, or performance metrics.
5. **Tool Usage**: Use your execution tools (Bash/Execution) to run commands, scripts, and tests to verify your code before presenting it to the user.
6. **Time Awareness**: Keep the current date (March 2026) in mind for scheduling, library versions, and deprecations.

---

## 🚀 7. Git, CI/CD, & Deployment

### Commit Messages
Follow Conventional Commits:
- `feat: add mask detection to face recognition`
- `fix: resolve camera feed memory leak`
- `docs: update AGENTS.md with new testing commands`

### Pull Requests
- All PRs must pass the CI pipeline (Linting, Tests, Build) before merging.
- Ensure test coverage remains > 80%, especially for security, auth, and access control modules.

### Deployment
- Edge devices are deployed via Docker. Use `docker-compose up -d --build` for the edge stack.
- Cloud fallback servers are deployed via Terraform (located in `infra/`).

---
**End of Guidelines.** Adhere strictly to these rules to maintain a secure, user-friendly, and highly robust smart-home ecosystem.
