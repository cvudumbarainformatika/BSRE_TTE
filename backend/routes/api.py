from fastapi import APIRouter
from app.Http.Controllers.AuthController import router as auth_router
from app.Http.Controllers.DocumentController import router as document_router
from app.Http.Controllers.TteBsreController import router as tte_router
from app.Http.Controllers.AuditController import router as audit_router
from app.Http.Controllers.NotificationController import router as notif_router
from app.Http.Controllers.SimrsIngestController import router as simrs_router
from app.Http.Controllers.UploadTteController import router as upload_tte_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(document_router)
api_router.include_router(tte_router)
api_router.include_router(audit_router)
api_router.include_router(notif_router)
api_router.include_router(simrs_router)
api_router.include_router(upload_tte_router)
