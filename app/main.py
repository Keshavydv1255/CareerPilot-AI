from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine
from app.models.activity import Activity
from app.models.resume import Resume
from app.models.report_snapshot import ReportSnapshot
from app.routes.chat import router as chat_router
from app.routes.cover_letter import router as cover_router
from app.routes.interview import router as interview_router
from app.routes.job_match import router as job_match_router
from app.routes.report import router as report_router
from app.routes.resume import router as resume_router
from app.routes.resume_improver import router as resume_improver_router
from app.services.analytics import get_activity_counts

app = FastAPI(title="CareerPilot AI", description="AI Career Mentor and Resume Analyzer", version="7.0.0")
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

for router in (resume_router, chat_router, cover_router, interview_router, job_match_router, resume_improver_router, report_router):
    app.include_router(router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"page": "home"})


@app.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html", context={"page": "upload"})


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"page": "dashboard", "stats": get_activity_counts()})
