import logging
from pathlib import Path
from fastapi import UploadFile, File, HTTPException, Depends
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
import torch
from torchvision import transforms
from PIL import Image
import io
from pydantic_models import ClassificationResult, ClassificationResponse
from models.interior_classifier_EfficientNet_B3 import InteriorClassifier

logger = logging.getLogger(f"uvicorn.{__file__}")
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

# Dependency для получения модели
def get_model():
    try:
        current_dir = Path(__file__).parent
        models_dir = current_dir.parent / "models"
        
        # Ищем файл по шаблону ckpt*
        checkpoint_files = list(models_dir.glob("ckpt*"))
        if not checkpoint_files:
            raise FileNotFoundError(f"No checkpoint files found in {models_dir}")
        
        # Берем первый найденный файл (можно добавить логику выбора конкретного файла)
        checkpoint_path = checkpoint_files[0]
        logger.info(f"Using checkpoint file: {checkpoint_path}")
        
        model = load_model(checkpoint_path=checkpoint_path)
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError("Failed to initialize model")

# Инициализация глобальных переменных
try:
    MODEL = get_model()
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
            "class_name": CLASS_NAMES[predicted.item()],
            "confidence": round(confidence.item(), 4)
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise


@router.post("/classify_batch", response_model=ClassificationResponse)
async def classify_batch(
    images: List[UploadFile] = File(...),
    model: InteriorClassifier = Depends(get_model)
):
    """
    Classify a batch of apartment images.
    
    Args:
        images: List of image files to classify
        model: Model instance injected via dependency
    
    Returns:
        ClassificationResponse with classification results for each image
    """
    start_time = datetime.now()
    
    try:
        results = []
        
        for image_file in images:
            try:
                # Читаем изображение
                image_data = await image_file.read()
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
                
                # Предсказываем класс
                prediction = predict_image(image, model)
                
                results.append(
                    ClassificationResult(
                        class_name=prediction["class_name"],
                        confidence=prediction["confidence"],
                        image_name=image_file.filename
                    )
                )
                
            except Exception as e:
                logger.error(f"Error processing image {image_file.filename}: {str(e)}")
                results.append(
                    ClassificationResult(
                        class_name="error",
                        confidence=0.0,
                        image_name=image_file.filename
                    )
                )
        
        response = ClassificationResponse(results=results)
        
        # Логирование запроса и ответа
        logger.info(f"Request processed in {(datetime.now() - start_time).total_seconds()} seconds")
        logger.info(f"Processed {len(images)} images")
        logger.info(f"Response: {response}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error in classify_batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
