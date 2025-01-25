import requests
from logging import getLogger
from utils.logging import setup_logger

logger = setup_logger()

def get_food_info(product_name):
    """
    Поиск информации о продукте и его калорийности с использованием OpenFoodFacts API.

    :param product_name: Название продукта для поиска.
    :return: Словарь с информацией о продукте (название, калорийность на 100 г).
    """
    if not product_name or not isinstance(product_name, str):
        logger.error("Название продукта должно быть непустой строкой.")
        return None

    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    logger.info(f"Поиск информации для продукта: {product_name}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info("Запрос к OpenFoodFacts API выполнен успешно.")
        
        data = response.json()
        products = data.get('products', [])
        
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            product_info = {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0),
                'brand': first_product.get('brands', 'Неизвестно'),
                'categories': first_product.get('categories', 'Неизвестно')
            }
            logger.debug(f"Информация о продукте: {product_info}")
            return product_info
        else:
            logger.warning(f"Продукт '{product_name}' не найден.")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Превышено время ожидания запроса для продукта '{product_name}'.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса: {e}", exc_info=True)
        return None
