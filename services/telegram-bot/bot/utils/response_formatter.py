from typing import Dict, Any, List


def format_classification_result(result: Dict[str, Any]) -> str:
    """
    Форматирование результата классификации для отправки пользователю
    
    Args:
        result: Результат от API
        
    Returns:
        Отформатированная строка
    """
    if not result or 'results' not in result:
        return "❌ Ошибка: неверный формат ответа от сервера"
    
    results = result['results']
    if not results:
        return "❌ Ошибка: нет результатов классификации"
    
    # Если одно изображение
    if len(results) == 1:
        return format_single_result(results[0])
    
    # Если несколько изображений
    return format_multiple_results(results)


def format_single_result(result: Dict[str, Any]) -> str:
    """Форматирование результата для одного изображения"""
    class_name = result.get('class_name', 'Unknown')
    probabilities = result.get('probabilities', [])
    image_name = result.get('image_name', 'Изображение')
    
    # Определяем эмодзи для класса
    class_emoji = get_class_emoji(class_name)
    
    # Форматируем вероятности
    prob_text = format_probabilities(probabilities, sorted_by_probability=True)
    
    text_lines = [
        f"🏠 <b>Результат классификации</b>\n",
        f"📸 <b>Файл:</b> {image_name}",
        f"{class_emoji} <b>Класс интерьера:</b> <code>{class_name}</code>\n\n",
        f"📊 <b>Распределение вероятностей:</b>",
        prob_text
    ]
    
    return "\n".join(text_lines)


def format_multiple_results(results: List[Dict[str, Any]]) -> str:
    """Форматирование результатов для нескольких изображений"""
    header = f"🏠 <b>Результаты классификации ({len(results)} изображений)</b>\n\n"
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        class_name = result.get('class_name', 'Unknown')
        image_name = result.get('image_name', f'Изображение {i}')
        class_emoji = get_class_emoji(class_name)
        
        formatted_results.append(
            f"{i}. {class_emoji} <b>{image_name}</b> → <code>{class_name}</code>"
        )
    
    return header + "\n".join(formatted_results)


def get_class_emoji(class_name: str) -> str:
    """Получение эмодзи для класса интерьера"""
    emoji_map = {
        'A0': '🧱',
        'A1': '🏚️',
        'B0': '◻️',
        'B1': '🎨',
        'C0': '☑️',
        'C1': '🏠',
        'D0': '✨',
        'D1': '💎',
    }
    return emoji_map.get(class_name, '🏠')


def format_probabilities(
        probabilities: List[float],
        sorted_by_probability: bool = False
    ) -> str:
    """Форматирование списка вероятностей"""
    class_names = ['A0', 'A1', 'B0', 'B1', 'C0', 'C1', 'D0', 'D1']
    
    if len(probabilities) != len(class_names):
        return "❌ Ошибка: неверное количество классов"
    
    # Создаем список кортежей (класс, вероятность) и сортируем по убыванию
    class_probs = list(zip(class_names, probabilities))
    if sorted_by_probability:
        class_probs.sort(key=lambda x: x[1], reverse=True)
    
    formatted_lines = []
    for class_name, prob in class_probs:
        emoji = get_class_emoji(class_name)
        percentage = prob * 100
        bar_length = int(percentage / 5)  # 5% = 1 символ
        bar = '█' * bar_length + '░' * (20 - bar_length)
        # Добавляем пробел перед процентом, если меньше 10 для выравнивания
        percent_str = f" {percentage:.1f}%" if percentage < 10 else f"{percentage:.1f}%"
        formatted_lines.append(
            f"{emoji} {class_name}: {percent_str} {bar}"
        )
    
    return "\n".join(formatted_lines) 