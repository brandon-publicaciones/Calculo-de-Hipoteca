# 🏠 Hipoteca Panamá 2026 (HipotecaAPK)

Calculadora de préstamos hipotecarios con interés preferencial (Leyes 468 y 481 de 2025).
PWA con **React + TypeScript (Vite)** en el frontend y **Python + FastAPI** en el backend.

```
HipotecaAPK/
├── backend/            # API (FastAPI) y generación de PDF (ReportLab)
│   ├── app/
│   │   ├── main.py     # endpoints /api/calculate y /api/pdf
│   │   ├── calc.py     # amortización francesa, dos fases
│   │   ├── rules.py    # tramos y subsidios por región (editable)
│   │   ├── schemas.py  # validaciones
│   │   └── pdf.py      # tabla de amortización en PDF
│   └── requirements.txt
└── frontend/           # React + TypeScript + PWA
    ├── src/
    ├── public/         # manifest y service worker
    └── package.json
```

---

## 1. Requisitos (una sola vez)

| Programa | Versión | Descarga |
|---|---|---|
| Python | 3.10 o superior (recomendado 3.12 o 3.13) | https://www.python.org/downloads/ |
| Node.js | 18 o superior (LTS) | https://nodejs.org |

Al instalar Python en Windows, marca **"Add Python to PATH"**.

Comprueba en PowerShell:
```powershell
python --version
node --version
npm --version
```

> **Consejo:** si el proyecto está dentro de OneDrive, `npm install` puede tardar o fallar.
> Pausa la sincronización mientras instalas, o muévelo a una carpeta como `C:\proyectos\HipotecaAPK`.

---

## 2. Instalar y arrancar el backend

Abre PowerShell en la carpeta del proyecto:

```powershell
cd HipotecaAPK\backend
python -m venv .venv
.venv\Scripts\activate
```

El prompt debe mostrar `(.venv)` al inicio. Si PowerShell bloquea la activación, ejecuta una vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Contenido recomendado de `backend\requirements.txt` (versiones sin fijar, para que funcione con Python 3.13/3.14):
```
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.12
reportlab>=4.2
```

Instala y arranca:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Debe aparecer `Uvicorn running on http://127.0.0.1:8000`.
Para comprobarlo, abre http://127.0.0.1:8000/docs. **Deja esta terminal abierta.**

---

## 3. Instalar y arrancar el frontend (modo desarrollo)

Abre una **segunda terminal**:

```powershell
cd HipotecaAPK\frontend
npm install
npm run dev
```

Abre http://localhost:5173. Con el backend corriendo ya puedes calcular.

---

## 4. Compilar para producción

```powershell
cd HipotecaAPK\frontend
npm run build
```

Esto revisa los tipos de TypeScript y genera la carpeta `frontend\dist`.

Probar el build (el service worker y la opción "Instalar app" solo funcionan aquí):
```powershell
npm run preview
```
Abre http://localhost:4173. El backend debe estar en el puerto 8000.

---

## 5. Un solo servidor (opcional)

Para servir el frontend compilado desde FastAPI y usar una sola terminal, agrega **al final** de `backend/app/main.py`:

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
```

Luego, con el `.venv` activado en `backend`:
```powershell
uvicorn app.main:app --port 8000
```
Abre http://localhost:8000. Cada vez que cambies el frontend, repite `npm run build`.

---

## 6. Uso diario (sin reinstalar)

| Terminal | Comandos |
|---|---|
| Backend | `cd HipotecaAPK\backend` → `.venv\Scripts\activate` → `uvicorn app.main:app --reload --port 8000` |
| Frontend | `cd HipotecaAPK\frontend` → `npm run dev` |

---

## 7. Reglas de negocio implementadas

- **Vivienda usada:** sin interés preferencial; tasa comercial todo el plazo.
- **Vivienda nueva de hasta $120,000:** subsidio sobre la tasa según tramo y región (tabla `TRAMOS` en `backend/app/rules.py`).
- **Más de $120,000:** no aplica subsidio.
- **Tasa preferencial** = tasa nominal comercial − puntos de subsidio (mínimo 0%).
- **Dos fases:** durante los años promocionales se paga la letra preferencial; al terminar, la letra se recalcula con el saldo pendiente y los meses restantes a la tasa comercial.
- **Edición manual:** se puede escribir una tasa y unos años promocionales propios, que sustituyen al subsidio de la ley.
- **TNA y TEA:** el cálculo usa siempre la tasa nominal anual ÷ 12. La tasa efectiva (TEA = (1 + TNA/12)¹² − 1) es solo informativa.

---

## 8. Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| `Could not read package.json` | Estás en la carpeta equivocada. Entra a `frontend` antes de `npm install` o `npm run dev`. |
| `ECONNREFUSED 127.0.0.1:8000` en Vite | El backend no está corriendo. Arranca uvicorn en otra terminal. |
| `did not find executable at ...python.exe` | El `.venv` apunta a un Python que ya no existe. Bórralo (`deactivate`, `Remove-Item -Recurse -Force .venv`) y créalo de nuevo. |
| `Failed building wheel for pydantic-core` / `link.exe not found` | Versiones fijas antiguas en `requirements.txt`. Usa las versiones con `>=` de la sección 2. Si persiste, instala Python 3.12 y crea el entorno con `py -3.12 -m venv .venv`. |
| `Cache entry deserialization failed` | Aviso inofensivo. Se limpia con `pip cache purge`. |
| `No module named 'app'` | Ejecuta uvicorn desde la carpeta `backend`, donde está la carpeta `app`. |
| `uvicorn no se reconoce` | El `.venv` no está activado o faltan dependencias: `pip install -r requirements.txt`. |
| `Property 'env' does not exist on type 'ImportMeta'` | Crea `frontend/src/vite-env.d.ts` con `/// <reference types="vite/client" />`. |
| Error 422 al calcular | Datos inválidos: región vacía en vivienda nueva, abono mayor al valor, o tasa y años promocionales incompletos. |
| Puerto 8000 ocupado | Usa `--port 8001` y cambia el destino en `frontend/vite.config.ts` (`"/api": "http://127.0.0.1:8001"`). |

---

## 9. Sobre un APK de Android

Esta carpeta genera una **PWA**, no un APK. Para Android hay dos caminos:

- **PWABuilder** (https://www.pwabuilder.com): requiere frontend y backend publicados con HTTPS.
- **Capacitor**: empaqueta el frontend en una app Android con Android Studio; el backend debe estar en un servidor accesible, porque el teléfono no ve tu `localhost`.

---

> Simulación referencial. Confirma tasas, tramos y condiciones con el banco o un asesor legal antes de usarla con clientes.
