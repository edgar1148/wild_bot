import requests


async def get_product_info(product_sku):
    """Функция для получения информации о товаре из Wildberries API"""

    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={product_sku}"
    response = requests.get(url)
    data = response.json()

    if "data" in data and "products" in data["data"] and data["data"]["products"]:
        product_data = data["data"]["products"][0]
        
        product_info = {
            "Название": product_data["name"],
            "Артикул": product_sku,
            "Цена": f"{int(product_data["salePriceU"] / 100)}₽",
            "Цена без скидки": f"{int(product_data["priceU"] / 100)}₽",
            "Рейтинг": f"{product_data["reviewRating"]}⭐",
            "Количество на складах": sum(stock["qty"] for stock in product_data["sizes"][0]["stocks"])
        }
        return product_info
    else:
        return None
