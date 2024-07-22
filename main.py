from bs4 import BeautifulSoup
import requests
import os

token = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI3ODY2MDc5MS00YjEwLTQwNzctOWJhZS1hNDE0ZjdlYTBjMGUiLCJpYXQiOjE3MTk0MTg4ODIsImV4cCI6MTcxOTQzNjg4Mn0.HS6GE_1-gkPWU83qmbUtrldWHXTv9jUQ6AaEqMeg6aw"

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
    authorization_token = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI3ODY2MDc5MS00YjEwLTQwNzctOWJhZS1hNDE0ZjdlYTBjMGUiLCJpYXQiOjE3MTk0MTg4ODIsImV4cCI6MTcxOTQzNjg4Mn0.HS6GE_1-gkPWU83qmbUtrldWHXTv9jUQ6AaEqMeg6aw'  # Замените на ваш токен

    with open(image_path, 'rb') as image_file:
        files = {'image': ('image.png', image_file, 'application/octet-stream')}
        headers = {'Authorization': authorization_token}

        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f'Ошибка при отправке изображения: {response.status_code}, {response.text}')

def post_ingidient(ingridient):
    url = "http://158.160.152.102:8080/ingridient/create"

    data = {
        "name": ingridient[0],
        "protein": float(ingridient[1]),
        "fat": float(ingridient[2]),
        "carbohydrates": float(ingridient[3]),
        "user_id": "dab557d4-0c3d-47eb-a19a-b6f414a67830",
        "image": ingridient[4]
    }

    print("Тело запроса:\n{")
    for key in data:
        print(f"    {key}: {data[key]},")
    print("}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Ингридиент попал на сервер:)")
    else:
        print(f"Ошибка {response.status_code}: {response.text}")



if __name__ == "__main__":
    save_directory = "./images"
    image_name = "image.jpg"
    save_path = os.path.join(save_directory, image_name)

    url = lambda x : f'https://food.ru/products?page={x}'
    product_url = lambda x : f'https://food.ru/{x}'

    i = -1

    for page in range(1, 57 + 1):
        response = requests.get(url(page))
        bs = BeautifulSoup(response.text, "lxml")
        dishes = bs.find_all('a', 'productCard_productCard__Z57rS')
        for dish in dishes:
            i+= 1
            if i > 249:
                response = requests.get(product_url(dish['href']))
                bs = BeautifulSoup(response.text, 'lxml')
                title = bs.find('h1', 'title_title__OHmf9')

                print(f"Ингридиент: {title.text}")
                
                macronutrients = bs.find_all('div', 'nutrient_wrapper__dmvnx nutritionInformation_nutrient__2gz6A')
                
                protein = macronutrients[1].find('span', 'nutrient_value__dd48k').text
                fat = macronutrients[2].find('span', 'nutrient_value__dd48k').text
                carbohydrate = macronutrients[3].find('span', 'nutrient_value__dd48k').text
                image_source = bs.find('picture').find('img')['srcset']

                
                download_image(image_source, save_path)
                if image_source != "https://cdn.food.ru/unsigned/fit/100/75/ce/0/czM6Ly9tZWRpYS9waWN0dXJlcy8yMDIzMTIyMi9pZ3FqUHQuanBlZw.jpg":
                    image_name = post_image()
                else:
                    image_name = "e2a6914a-9ed1-4a34-83a4-583ac0733236"
                
                print(f"Получен идентификатор изображения: {image_name[:-4]}")
                print(f"Отправка ингридиента на сервер")
                post_ingidient([title.text, protein.replace(',', '.'), fat.replace(',', '.'), carbohydrate.replace(',', '.'), image_name.replace(".png", "")])
                print("\n")