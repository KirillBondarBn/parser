from bs4 import BeautifulSoup
import requests

token = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI3ODY2MDc5MS00YjEwLTQwNzctOWJhZS1hNDE0ZjdlYTBjMGUiLCJpYXQiOjE3MTk0NjUxMzIsImV4cCI6MTcxOTQ4MzEzMn0.aoqe2PoId0k1UUDyQZc1MFHCfJILZn_-MTxDPD8i1Qg"

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
            print(f"Скачано изображение по адресу: {url}")
            print(f"Изображение сохранено в папку: {save_path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

def post_image():
    url = 'http://158.160.152.102:8080/image/upload'
    image_path = 'images/image.jpg'
    
    with open(image_path, 'rb') as image_file:
        files = {'image': ('image.png', image_file, 'application/octet-stream')}
        headers = {'Authorization': token}

        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        print(f"Изображение отправлено, получен его идентификатор: {response.text}")
        return response.text
    else:
        print(f'Ошибка при отправке изображения: {response.status_code}, {response.text}')

def post_dish(dish):
    print("Отправляем рецепт на сервер...")
    url = "http://158.160.152.102:8080/dish/create"

    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    response = requests.post(url, json=dish, headers=headers)

    if response.status_code == 200:
        print("Рецепт попал на сервер:)")
    else:
        print(f"Ошибка {response.status_code}: {response.text}")

def get_ingridient_id(name):
    url = f"http://158.160.152.102:8080/ingridient/findByName?name={name}"
    headers = {
        'Authorization': token
    }
    response = requests.get(url, headers=headers)
    return response.json()['id']


if __name__ == "__main__":
    recipe_url = lambda x: f"https://food.ru/{x}"
    page_url = lambda x: f"https://food.ru/recipes?page={x}"

    for page in range(1, 6172 + 1):
        response = requests.get(page_url(page))
        bs = BeautifulSoup(response.text, "lxml")
        receipts = bs.find_all('a', 'card_card__YG0I9')

        for receipt in receipts:
            try:
                dish = {}
                response = requests.get(recipe_url(receipt['href']))
                bs = BeautifulSoup(response.text, 'lxml')
                dish["name"] = bs.find("h1", "title_main__ok7t1").text
                dish["amountPortion"] = bs.find("input", "input yield default yield")["value"]

                cookingTime = bs.find("div", "properties_value__kAeD9 properties_valueWithIcon__WDXDm duration").text.split()
                if len(cookingTime) == 4:
                    cookingTime = int(cookingTime[0]) * 60 + int(cookingTime[2])
                else:
                    cookingTime = int(cookingTime[0])
                dish["cookingTime"] = cookingTime

                dish_image_source = bs.find("div", "image_outer__M09PO image_widescreen__I7uNl").find("link")["href"]
                download_image(dish_image_source, "images/image.jpg")
                dish["image"] = post_image().replace(".png", "")
                
                bs_ingridients = bs.find("table", "ingredientsTable_table__pamnR ingredientsCalculator_ingredientsTable__hwuQx").find_all("tr", "ingredient")
                ingridients = []

                for ingridient in bs_ingridients:
                    ingridient_name = ingridient.find("span", "name").text
                    ingridient_gramm = ingridient.find("span", "ingredientsTable_text__3ILFA").find("span", "value")
                    ingridient_gramm = float(ingridient_gramm.text.replace(",", ".")) if ingridient_gramm != None else 0
                    ingridient_amount = None
                    ingridient_units = None

                    temp = ingridient.find("span", "ingredientsTable_text__3ILFA").text.split()
                    if len(temp) == 5:
                        ingridient_amount = float(temp[0])
                        ingridient_units = temp[1]


                    ingridient_id = get_ingridient_id(ingridient_name)
                    ingridients.append({
                        "ingridient_id": ingridient_id,
                        "amount": ingridient_amount,
                        "unit": ingridient_units,
                        "gramm": ingridient_gramm
                    })
                dish['ingredient'] = ingridients

                bs_steps = bs.find_all("div", "stepByStepPhotoRecipe_step__ygqQw")
                steps = []
                
                step_number = 1
                for step in bs_steps:
                    step_title = step.find("h3", "stepByStepPhotoRecipe_subTitle__0Wp7B")
                    step_title = step_title.text if (step_title != None) else "Подготовиться" if step_number == 1 else "Произвести впечатление"
                    step_description = step.find("span", "markup_text__F9WKe").text

                    step_image_source = step.find("div", "image_outer__M09PO image_fullscreen__nGBN2").find("link")['href']
                    download_image(step_image_source, "images/image.jpg")
                    step_image_name = post_image().replace(".png", "")
                    steps.append({
                        "number": step_number,
                        "title": step_title,
                        "image": step_image_name.replace(".png", ""),
                        "description": step_description
                    })

                    step_number += 1
                dish["steps"] = steps
                post_dish(dish)
            except Exception as e:
                print(f"Ошибка при обработке рецепта {receipt['href']}: {e}")
                continue