#!/usr/bin/env python3
"""
API FastAPI para Gerador de Etiquetas ArUco
===========================================

Esta API permite gerar etiquetas ArUco via HTTP e retorna as imagens em base64.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import cv2
import numpy as np
import base64
import io
from PIL import Image
import uvicorn


class ArucoGenerator:
    """Classe para gerar etiquetas ArUco personalizáveis."""
    
    def __init__(self):
        """Inicializa o gerador ArUco."""
        # Dicionário ArUco padrão (4x4)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        
    def generate_single_marker(self, marker_id: int, size: int = 200, margin: int = 10, 
                              border_bits: int = 1) -> np.ndarray:
        """
        Gera uma única etiqueta ArUco.
        
        Args:
            marker_id (int): ID da etiqueta (0-49 para DICT_4X4_50)
            size (int): Tamanho da imagem em pixels
            margin (int): Margem ao redor da etiqueta
            border_bits (int): Bits de borda
            
        Returns:
            numpy.ndarray: Imagem da etiqueta ArUco
        """
        # Gera a etiqueta
        marker_img = cv2.aruco.generateImageMarker(
            self.aruco_dict, 
            marker_id, 
            size, 
            borderBits=border_bits
        )
        
        # Adiciona margem
        if margin > 0:
            marker_img = cv2.copyMakeBorder(
                marker_img, 
                margin, margin, margin, margin, 
                cv2.BORDER_CONSTANT, 
                value=255
            )
        
        return marker_img
    
    def set_dictionary(self, dict_type: str):
        """
        Define o tipo de dicionário ArUco.
        
        Args:
            dict_type (str): Tipo de dicionário ('4x4', '5x5', '6x6', '7x7')
        """
        dict_mapping = {
            '4x4': cv2.aruco.DICT_4X4_50,
            '5x5': cv2.aruco.DICT_5X5_50,
            '6x6': cv2.aruco.DICT_6X6_50,
            '7x7': cv2.aruco.DICT_7X7_50
        }
        
        if dict_type in dict_mapping:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(dict_mapping[dict_type])
            return True
        else:
            return False


# Modelos Pydantic para validação de dados
class MarkerRequest(BaseModel):
    marker_id: int = Field(..., ge=0, le=49, description="ID da etiqueta (0-49)")
    size: int = Field(200, ge=50, le=1000, description="Tamanho da etiqueta em pixels")
    margin: int = Field(10, ge=0, le=100, description="Margem ao redor da etiqueta")
    border_bits: int = Field(1, ge=1, le=3, description="Bits de borda")
    dictionary: str = Field("4x4", description="Tipo de dicionário (4x4, 5x5, 6x6, 7x7)")


class MarkerResponse(BaseModel):
    success: bool
    marker_id: int
    image_base64: str
    size: int
    margin: int
    dictionary: str
    message: str


class MultipleMarkersRequest(BaseModel):
    start_id: int = Field(0, ge=0, le=49, description="ID inicial")
    count: int = Field(5, ge=1, le=20, description="Número de etiquetas")
    size: int = Field(200, ge=50, le=1000, description="Tamanho da etiqueta em pixels")
    margin: int = Field(10, ge=0, le=100, description="Margem ao redor da etiqueta")
    border_bits: int = Field(1, ge=1, le=3, description="Bits de borda")
    dictionary: str = Field("4x4", description="Tipo de dicionário")


class MultipleMarkersResponse(BaseModel):
    success: bool
    markers: List[dict]
    total_generated: int
    message: str


# Criação da aplicação FastAPI
from mangum import Mangum

app = FastAPI(
    title="Gerador de Etiquetas ArUco API",
    description="API para gerar etiquetas ArUco personalizáveis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Instância global do gerador
generator = ArucoGenerator()


def image_to_base64(image: np.ndarray) -> str:
    """
    Converte uma imagem numpy para base64.
    
    Args:
        image (np.ndarray): Imagem numpy
        
    Returns:
        str: String base64 da imagem
    """
    # Converte para PIL Image
    pil_image = Image.fromarray(image)
    
    # Salva em buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    
    # Converte para base64
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str


@app.get("/")
async def root():
    """Rota raiz com informações da API."""
    return {
        "message": "Gerador de Etiquetas ArUco API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate_single": "/generate",
            "generate_multiple": "/generate-multiple",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "healthy", "message": "API funcionando corretamente"}


@app.post("/generate", response_model=MarkerResponse)
async def generate_single_marker(request: MarkerRequest):
    """
    Gera uma única etiqueta ArUco.
    
    Args:
        request: Parâmetros da etiqueta
        
    Returns:
        MarkerResponse: Resposta com a imagem em base64
    """
    try:
        # Define o dicionário
        if not generator.set_dictionary(request.dictionary):
            raise HTTPException(
                status_code=400, 
                detail=f"Dicionário '{request.dictionary}' não suportado"
            )
        
        # Gera a etiqueta
        marker_image = generator.generate_single_marker(
            request.marker_id,
            request.size,
            request.margin,
            request.border_bits
        )
        
        # Converte para base64
        image_base64 = image_to_base64(marker_image)
        
        return MarkerResponse(
            success=True,
            marker_id=request.marker_id,
            image_base64=image_base64,
            size=request.size,
            margin=request.margin,
            dictionary=request.dictionary,
            message=f"Etiqueta {request.marker_id} gerada com sucesso"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar etiqueta: {str(e)}")


@app.post("/generate-multiple", response_model=MultipleMarkersResponse)
async def generate_multiple_markers(request: MultipleMarkersRequest):
    """
    Gera múltiplas etiquetas ArUco.
    
    Args:
        request: Parâmetros das etiquetas
        
    Returns:
        MultipleMarkersResponse: Resposta com as imagens em base64
    """
    try:
        # Define o dicionário
        if not generator.set_dictionary(request.dictionary):
            raise HTTPException(
                status_code=400, 
                detail=f"Dicionário '{request.dictionary}' não suportado"
            )
        
        markers = []
        generated_count = 0
        
        for i in range(request.count):
            marker_id = request.start_id + i
            
            # Verifica se o ID é válido
            if marker_id > 49:
                continue
            
            # Gera a etiqueta
            marker_image = generator.generate_single_marker(
                marker_id,
                request.size,
                request.margin,
                request.border_bits
            )
            
            # Converte para base64
            image_base64 = image_to_base64(marker_image)
            
            markers.append({
                "marker_id": marker_id,
                "image_base64": image_base64,
                "size": request.size,
                "margin": request.margin
            })
            
            generated_count += 1
        
        return MultipleMarkersResponse(
            success=True,
            markers=markers,
            total_generated=generated_count,
            message=f"Geradas {generated_count} etiquetas com sucesso"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar etiquetas: {str(e)}")


@app.get("/generate")
async def generate_marker_get(
    marker_id: int = Query(..., ge=0, le=49, description="ID da etiqueta (0-49)"),
    size: int = Query(200, ge=50, le=1000, description="Tamanho da etiqueta em pixels"),
    margin: int = Query(10, ge=0, le=100, description="Margem ao redor da etiqueta"),
    border_bits: int = Query(1, ge=1, le=3, description="Bits de borda"),
    dictionary: str = Query("4x4", description="Tipo de dicionário (4x4, 5x5, 6x6, 7x7)")
):
    """
    Gera uma única etiqueta ArUco via GET.
    
    Args:
        marker_id: ID da etiqueta
        size: Tamanho da etiqueta
        margin: Margem ao redor da etiqueta
        border_bits: Bits de borda
        dictionary: Tipo de dicionário
        
    Returns:
        JSON com a imagem em base64
    """
    try:
        # Define o dicionário
        if not generator.set_dictionary(dictionary):
            raise HTTPException(
                status_code=400, 
                detail=f"Dicionário '{dictionary}' não suportado"
            )
        
        # Gera a etiqueta
        marker_image = generator.generate_single_marker(
            marker_id, size, margin, border_bits
        )
        
        # Converte para base64
        image_base64 = image_to_base64(marker_image)
        
        return {
            "success": True,
            "marker_id": marker_id,
            "image_base64": image_base64,
            "size": size,
            "margin": margin,
            "dictionary": dictionary,
            "message": f"Etiqueta {marker_id} gerada com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar etiqueta: {str(e)}")


@app.get("/info")
async def get_info():
    """Retorna informações sobre os dicionários disponíveis."""
    return {
        "dictionaries": {
            "4x4": {
                "description": "Detecção rápida, menor precisão",
                "max_id": 49,
                "recommended_use": "Detecção em tempo real"
            },
            "5x5": {
                "description": "Maior precisão, detecção média",
                "max_id": 49,
                "recommended_use": "Aplicações gerais"
            },
            "6x6": {
                "description": "Alta precisão, detecção mais lenta",
                "max_id": 49,
                "recommended_use": "Aplicações de alta precisão"
            },
            "7x7": {
                "description": "Máxima precisão, detecção mais lenta",
                "max_id": 49,
                "recommended_use": "Aplicações críticas"
            }
        },
        "parameters": {
            "marker_id": "0-49 (dependendo do dicionário)",
            "size": "50-1000 pixels",
            "margin": "0-100 pixels",
            "border_bits": "1-3 bits"
        }
    }



# Handler para AWS Lambda
handler = Mangum(app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
