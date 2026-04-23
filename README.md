# PlanCraft AI Architect

A comprehensive AI-powered Flutter & Python project for generating full spatial architectural designs, floor plans, 3D models, cost estimates, and interior specifications from natural language and image references.

---

## Table of Contents

- [Chapter 1: Getting Started](#chapter-1-getting-started)
- [Chapter 2: Features](#chapter-2-features)
- [Chapter 3: Architecture](#chapter-3-architecture)
- [Chapter 4: Quick Start](#chapter-4-quick-start)
- [Chapter 5: API Reference](#chapter-5-api-reference)
- [Chapter 6: Project Structure](#chapter-6-project-structure)
- [Chapter 7: Roadmap](#chapter-7-roadmap)
- [Chapter 8: Contributing](#chapter-8-contributing)
- [Chapter 9: Known Issues & Limitations](#chapter-9-known-issues--limitations)
- [Chapter 10: License & Acknowledgements](#chapter-10-license--acknowledgements)

---

## Chapter 1: Getting Started

This project is a starting point for the PlanCraft AI application.

A few resources to get you started if this is your first Flutter project:
- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the [online documentation](https://docs.flutter.dev/), which offers tutorials, samples, guidance on mobile development, and a full API reference.

---

## Chapter 2: Features

### AI-Powered Design Pipeline
- **Natural Language Input** — Describe your requirements in plain English (e.g., *"A modern 2-story house with 4 bedrooms, glass balcony, and flat roof"*)
- **Gemini 2.5 Flash Architect Agent** — World-class AI generates a complete, spatially-valid building specification with room-by-room coordinates.
- **Geometry Validation Engine** — Automatic overlap detection with AI self-correction (up to 2 fix cycles) before rendering.
- **Vision Agent** — Upload a site photo, style reference, or **2D floor plan sketch**. Gemini analyses terrain, aesthetic features, and extracts precise geometry from sketches to build 3D models with 100% architectural logic.
- **Surface Method 3D Generation** — Professional-grade 3D modeling that builds continuous wall meshes instead of simple box primitives, ensuring clean topology and no overlapping geometry.

### Completed AI Modules
| Article Feature | Status |
|---|---|
| 1. AI Building concept Generation | ✅ `ArchitectAgent` & `ConceptArtAgent` |
| 2. AI Floor Plan Generator | ✅ `FloorPlanRenderer` + `CadExporter` |
| 3. AI + CAD Automation | ✅ `cad_exporter.py` (ezdxf DXF) |
| 4. 3D Modeling with AI | ✅ `script_generator.py` + Blender runner |
| 5. Interior Design with AI | ✅ `InteriorDesignAgent` |
| 6. Construction Cost Estimation | ✅ `CostEstimator` |
| 7. AI Design Critique | ✅ `CritiqueAgent` |
| 8. AI Concept Art / Mood Boards | ✅ `ConceptArtAgent` |
| 9. Construction Material Optimization | ✅ `MaterialOptimizer` |
| 10. Merge conflicts in `architect_agent.py` | ✅ Fixed |

### Professional 2D Floor Plans
- **Per-floor PNG previews** — Clean, colour-coded floor plans at 1:100 scale with dimension annotations.
- **NanoCAD / AutoCAD DXF export** — Industry-standard CAD files generated with `ezdxf`; each floor is a separate DXF layer.
- Supports up to **10 floors** with independent room layouts.

### 3D Rendering & Export
- **Blender headless rendering** — Full 3D exterior renders produced by Blender (EEVEE) in PNG format.
- **Professional Archimesh Integration** — Automated placement of realistic doors and windows using the Archimesh Blender add-on.
- **GLB model export** — Import directly into Blender, Three.js, or any glTF-compatible viewer.
- **STL export** — Ready for 3D printing or further structural engineering workflows.
- Physically-based materials (walls, glass, doors, roofing, ground plane).

### Construction Cost Estimation
- Real-world cost ranges in **PKR and USD** per square foot based on 2026 South Asian construction data.
- Bill of Quantities: bricks, cement bags (50 kg), reinforcement steel (kg), paint (litres), sand (m³).
- Three cost tiers: low / mid / high.

### AI Design Critique
- **CritiqueAgent** powered by Gemini generates expert architectural feedback on every design.
- Evaluates spatial flow, biophilic design, wellness architecture, indoor-outdoor connectivity, and engineering standards.
- Returns structured critique points surfaced directly in the Flutter UI.

### Post-Generation Customisation
- Change **exterior colour**, **roof colour**, **roof type** (flat/gable/hip/shed/mansard), **facade material**, and **window type** without re-running the full pipeline.

### File Management & Frontend
- Upload site photos, style reference images, and sketch photos.
- All generated assets (PNGs, DXFs, GLBs, STLs) available for download via dedicated export endpoints.
- Beautiful dark-mode UI with gold accent colours.
- Fully responsive web app (`flutter build web`) served by the same FastAPI process.

---

## Chapter 3: Architecture

```text
AI Architect
├── Flutter Frontend (lib/)          # Cross-platform UI (web/Android/iOS)
│   ├── Onboarding & Input Screen
│   ├── Real-time Progress View
│   ├── 2D Floor Plan Viewer
│   ├── 3D GLB Model Viewer
│   └── Download Centre
│
└── Python Backend (backend/)
    ├── FastAPI (main.py)            # REST API + static file server
    │
    ├── Agents
    │   ├── ArchitectAgent           # Gemini 2.5 Flash → BuildingSpec JSON
    │   ├── VisionAgent              # Site & style photo analysis
    │   ├── ConceptArtAgent          # Mood board concepts
    │   ├── InteriorDesignAgent      # Room by room interiors
    │   └── CritiqueAgent            # Expert design review
    │
    ├── Services
    │   ├── JobService (Celery)      # Async task queue (Redis broker)
    │   ├── DesignerService          # Orchestrates 2D PNG + DXF output
    │   ├── CadExporter              # ezdxf DXF generation
    │   ├── CostEstimator            # PKR/USD cost + BoQ
    │   └── MaterialOptimizer        # Cost-saving sustainable material swaps
    │
    └── Blender Integration
        ├── GeometryValidator        # Shapely-based overlap detection
        ├── FloorPlanRenderer        # Matplotlib → PNG floor plans
        ├── ScriptGenerator          # Dynamic Blender Python scripts
        └── BlenderRunner            # Headless Blender subprocess
```

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Flutter 3.41+, Dart |
| Backend API | FastAPI, Uvicorn |
| AI / LLM | Google Gemini 2.5 Flash (`google-genai`) |
| Task Queue | Celery 5 + Redis |
| 3D Rendering | Blender 4.2+ (headless, EEVEE) |
| CAD Export | ezdxf 1.3+ |
| Geometry | Shapely, NumPy |
| Floor Plan Images | Matplotlib, Pillow |
| Data Validation | Pydantic v2 |

---

## Chapter 4: Quick Start

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Flutter SDK | 3.41+ |
| Blender | 4.2+ (must be accessible as `blender` or set `BLENDER_PATH`) |
| Redis | 7+ |

### 1. Clone the Repository

```bash
git clone https://github.com/ilyaskhan12/Plancraft-ai.git
cd Plancraft-ai
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env            # then edit .env with your keys
```

**`.env` configuration example:**
```env
GEMINI_API_KEY=your_google_gemini_api_key
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://localhost:8080
BLENDER_PATH=/usr/local/bin/blender
RENDERS_DIR=./renders
UPLOADS_DIR=./uploads
```

### 3. Start Redis

```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS (Homebrew)
brew services start redis
```

### 4. Start the Backend Services

Open **two terminal tabs** in `backend/`:

```bash
# Terminal 1 — FastAPI server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080

# Terminal 2 — Celery worker
source venv/bin/activate
celery -A app.services.job_service.celery_app worker --loglevel=info --concurrency=1
```

### 5. Flutter Frontend

```bash
# From project root
flutter pub get

# Run in Chrome
flutter run -d chrome

# Or build and serve via backend
flutter build web                # outputs to build/web/ (served by FastAPI automatically)
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## Chapter 5: API Reference

Base URL: `http://localhost:8080`

### Health Check
```
GET /api/health
```

### Generate a Design
```
POST /generate
Content-Type: application/json

{
  "plot": { "length": 15, "width": 10, "unit": "meters", "floors": 2, "orientation": "north" },
  "rooms": { "bedrooms": 4, "bathrooms": 3, "living_room": true, "kitchen": true, "dining": true, "garage": true },
  "preferred_style": "modern",
  "budget": "high",
  "region": "south_asian",
  "description": "A modern two-story house with glass balcony and flat roof"
}
```
Returns: `{ "job_id": "uuid" }`

### Concept & Interior Standalone Generation
- `POST /generate/concept`: Generate mood board concepts.
- `POST /generate/interior`: Generate interior floor design.

### Poll Job Status
```
GET /status/{job_id}
```
Returns real-time progress (`0.0–1.0`), stage label, and result URLs when complete.

### Export Assets
```text
GET /export/{job_id}/floorplan/{floor_index}   # PNG floor plan
GET /export/{job_id}/dxf/{floor_index}          # DXF CAD file
GET /export/{job_id}/render                     # 3D render PNG
GET /export/{job_id}/model                      # GLB 3D model
GET /export/{job_id}/stl                        # STL for 3D printing
GET /export/{job_id}/critique                   # JSON critique scoring
GET /export/{job_id}/cost-report                # JSON construction BoQ
GET /export/{job_id}/materials                  # JSON material optimization
GET /export/{job_id}/interior                   # JSON interior specs
```

### Upload Reference Photos
```text
POST /upload/site-photo
POST /upload/style-photo
POST /upload/sketch
```

### Customise an Existing Design
```
POST /customize/{job_id}
Content-Type: application/json

{
  "exterior_color": "#F5F5F0",
  "roof_type": "flat",
  "facade_material": "stone",
  "window_type": "bay"
}
```

---

## Chapter 6: Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── agents/              # AI agents (Architect, Vision, Critique, Concept, Interior)
│   │   ├── api/routes/          # FastAPI route handlers
│   │   ├── blender/             # 3D pipeline (validator, renderer, script gen, runner)
│   │   ├── models/schemas.py    # All Pydantic v2 data models
│   │   └── services/            # Job queue, designer, CAD exporter, cost, materials
│   ├── main.py                  # FastAPI app entry point
│   └── requirements.txt
├── lib/                         # Flutter source (Dart)
├── assets/                      # Icons, images
├── web/                         # Flutter web shell
└── pubspec.yaml
```

---

## Chapter 7: Roadmap

- [ ] **Structural Engineering Layer** — Beam/column sizing, slab thickness calculations.
- [ ] **AR Viewer** — Augmented reality preview on mobile.
- [ ] **Multi-variant Generation** — Generate 3 design alternatives simultaneously.
- [ ] **BIM Export** — IFC file output for professional BIM workflows.
- [ ] **Clouflare Tunnel Integration** — Persistent public URL with zero-config deployment.
- [ ] **User Accounts & Project History** — Save, reload, and iterate on previous designs.
- [ ] **Energy Simulation** — Passive solar analysis and HVAC load estimation.
- [ ] **Landscaping Layer** — AI-generated garden and driveway layout.

---

## Chapter 8: Contributing

We welcome contributions from architects, engineers, AI researchers, Flutter developers, and open-source enthusiasts!

### Ways to Contribute

| Area | How to Help |
|---|---|
| **New AI Agents** | Add specialised agents (structural, MEP) |
| **Regional Styles** | Add building specs for new regions/countries |
| **Frontend UX** | Improve Flutter screens, animations, accessibility |
| **CAD Export** | Enhance DXF layers, add IFC/BIM support |
| **Testing** | Write unit/integration tests for agents and services |
| **Documentation** | Improve docs, add tutorials, write code comments |
| **Bug Reports** | Open a detailed issue with reproduction steps |

### Getting Started as a Contributor

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and write meaningful commit messages
4. **Test** your changes locally (backend + Flutter)
5. **Open a Pull Request** with a clear description of what you changed and why

---

## Chapter 9: Known Issues & Limitations

### 2D Floor Plan Extraction
- **Curved Walls**: Vision agent may struggle with highly organic or curved wall segments.
- **Complex Stairs**: Multi-landing staircases are currently modeled as simplified volumes.
- **Text Heavy Sketches**: Overly cluttered hand-drawn sketches may lead to "ghost" walls or missed openings.

### 3D Rendering
- **Interior Furniture**: Auto-placement of internal furniture (sofas, tables) is currently in beta and may occasionally overlap.
- **Lighting**: Night-time renders require manual adjustment of light energy in the `.env` if defaults are too dim.
- **Non-Manifold Faces**: While the Surface Method drastically reduces these, complex overlapping room definitions in the prompt can still cause minor mesh artifacts.

### Platform Specifics
- **Web Browser Performance**: The 3D GLB viewer in the Flutter web app depends on hardware acceleration; low-end devices may experience lag.

---

## Chapter 10: License & Acknowledgements

### License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

### Acknowledgements
- [Google Gemini](https://ai.google.dev) — The AI brain powering all design generation.
- [Blender Foundation](https://www.blender.org) — Open source 3D rendering engine.
- [ezdxf](https://ezdxf.readthedocs.io) — Professional DXF generation library.
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework.
- [Flutter](https://flutter.dev) — Beautiful cross-platform UI toolkit.
- [Shapely](https://shapely.readthedocs.io) — Geometry validation engine.

<div align="center">

**Built with ❤️ for architects, engineers, and dreamers everywhere.**

If you find this project useful, please give it a star ⭐ it helps us grow!

</div>
