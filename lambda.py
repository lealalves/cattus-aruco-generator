import io
import base64
from PIL import Image
from mangum import Mangum
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query

from aruco_generator import ArucoGenerator

class MarkerRequest(BaseModel):
    id: int = Field(..., ge=0, le=49, description="ID do marcador ArUco (0-49)")
    size: int = Field(200, ge=50, le=1000, description="Tamanho do marcador em pixels")
    margin_size: int = Field(10, ge=0, le=100, description="Margem do marcador")
    border_bits: int = Field(1, ge=1, le=4, description="Bits da borda do marcador")

class MarkerResponse(BaseModel):
    id: int
    image_base64: str

def create_app() -> FastAPI:
    app = FastAPI(title="ArUco Generator API")

    def image_to_base64(img) -> str:
        pil_img = Image.fromarray(img)
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    @app.get("/generate", response_model=MarkerResponse)
    def generate_marker_get(
        id: int = Query(..., ge=0, le=49, description="ID do marcador ArUco"),
        size: int = Query(200, ge=50, le=1000, description="Tamanho do marcador em pixels"),
        margin_size: int = Query(10, ge=0, le=100, description="Margem do marcador"),
        border_bits: int = Query(1, ge=1, le=4, description="Bits da borda do marcador")
    ):
        try:
            aruco_generator = ArucoGenerator()
            marker_img = aruco_generator.generate_single_marker(
                id=id, size=size, margin_size=margin_size, border_bits=border_bits
            )
            base64_img = image_to_base64(marker_img)
            return MarkerResponse(id=id, image_base64=base64_img)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/")
    def root():
        return {"message": "ArUco Generator API - Use /generate endpoint to get markers."}

    return app

app = create_app()
handler = Mangum(app)
