import logging
from pathlib import Path
from fastapi import UploadFile, File, Form, HTTPException
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
import json
from datetime import datetime
import torch
from torchvision import transforms
from PIL import Image
import io
from models.interior_classifier_EfficientNet_B3 import InteriorClassifier

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Загрузка модели (замените на свою реализацию)
def load_model(checkpoint_path: Path):
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Model file {checkpoint_path} not found")
    
    checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
    model = InteriorClassifier(num_classes=8)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model

# Инициализация модели
try:
    current_dir = Path(__file__).parent
    models_dir = current_dir.parent / "models"
    checkpoint_path = models_dir / "ckpt_epoch08.pth"
    MODEL = load_model(checkpoint_path=checkpoint_path)
    CLASS_NAMES = ["A0", "A1", "B0", "B1", "C0", "C1", "D0", "D1"]
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise RuntimeError("Failed to initialize model")

# Трансформации для изображения (адаптируйте под вашу модель)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def predict_image(image: Image.Image, model) -> dict:
    """Функция для предсказания класса изображения"""
    try:
        # Применяем трансформации
        image_tensor = transform(image).unsqueeze(0)
        
        # Предсказание
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
        return {
            "class": CLASS_NAMES[predicted.item()],
            "confidence": round(confidence.item(), 4)
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise


@router.post("/classify_batch", response_model=dict)
async def classify_batch(
    images: List[UploadFile] = File(...),
    meta: str = Form(...)
):
    """
    Classify a batch of apartment images.
    
    Args:
        images: List of image files to classify
        meta: JSON string with metadata (apartment_id, address)
    
    Returns:
        JSON with classification results for each image
    """
    start_time = datetime.now()
    
    try:
        # Парсим метаданные
        try:
            meta_data = json.loads(meta)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in meta field")
        
        if not all(key in meta_data for key in ["apartment_id", "address"]):
            raise HTTPException(status_code=400, detail="Meta must contain apartment_id and address")
        
        results = []
        
        for image_file in images:
            try:
                # Читаем изображение
                image_data = await image_file.read()
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
                
                # Предсказываем класс
                prediction = predict_image(image, MODEL)
                
                results.append({
                    "class": prediction["class"],
                    "confidence": prediction["confidence"],
                    "image_name": image_file.filename,
                    "meta": meta_data
                })
                
            except Exception as e:
                logger.error(f"Error processing image {image_file.filename}: {str(e)}")
                results.append({
                    "class": "error",
                    "confidence": 0.0,
                    "image_name": image_file.filename,
                    "meta": meta_data,
                    "error": str(e)
                })
        
        response = {"results": results}
        
        # Логирование запроса и ответа
        logger.info(f"Request processed in {(datetime.now() - start_time).total_seconds()} seconds")
        logger.info(f"Request meta: {meta_data}")
        logger.info(f"Response: {response}")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error in classify_batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
