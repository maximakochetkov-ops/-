# Импортируем библиотеку для отправки HTTP-запросов, парсинга HTML и XML и модуль для работы со временем
import requests
from bs4 import BeautifulSoup
import time

# Парсим HTML-код страницы, извлекаем все ссылки на другие статьи Википедии с исключениями и возвращаем набор полных URL-адресов статей
def get_wikipedia_links(url, base_url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()

        # Находит все ссылки в основном содержимом статьи
        for a in soup.select('div.mw-parser-output a[href^="/wiki/"]'):
            href = a.get('href')
            if ":" not in href:
                full_url = base_url + href
                links.add(full_url)

        return links

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении {url}: {e}")
        return []


# Проверяем, является ли URL допустимым адресом статьи в Википедии
def is_valid_wikipedia_url(url, base_url):
    parsed_url = urlparse(url)
    parsed_base_url = urlparse(base_url)

    # Проверка домена
    if parsed_url.netloc != parsed_base_url.netloc:
        return False

    # Проверка языка
    if parsed_url.netloc[:2] != parsed_base_url.netloc[:2]:
        return False

    # Проверка пути
    return parsed_url.path.startswith('/wiki/') and ':' not in parsed_url.path


# Ищем путь от начальной статьи к конечной, используя алгоритм поиска в глубину
def find_first_path(start_url, end_url, rate_limit):

    visited = set()
    stack = [(start_url, [start_url])]
    requests_made = 0

    while stack:
        current_url, path = stack.pop()

        if current_url == end_url:
            return path

        if len(path) > 5:
            continue

        if current_url not in visited:
            visited.add(current_url)
            links = get_wikipedia_links(current_url, base_url="https://en.wikipedia.org")
            requests_made += 1

            if requests_made >= rate_limit:
                # Добавляем задержку, чтобы соблюсти ограничение скорости
                time.sleep(1)  # Ограничение количества запросов

                requests_made = 0

            for link in links:
                if link not in visited:
                    stack.append((link, path + [link]))

    return None


# Сохраняем найденный путь в текстовый файл, если путь существует
def save_path_to_file(path, filename):
    if path:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(" -> ".join(path))
        print(f"Путь сохранен в файл: {filename}")
    else:
        print(f"Путь не найден, файл {filename} не создан.")


# Запускаем поиск пути в обоих направлениях
def main(start_url, end_url, rate_limit):
    print("Поиск пути от url1 к url2")
    path_start_to_end = find_first_path(start_url, end_url, rate_limit)

    if path_start_to_end:
        print(f"Путь от {start_url} к {end_url}:")
        print(" -> ".join(path_start_to_end))
    else:
        print(f"Путь от {start_url} к {end_url} не найден за {5} переходов.")

    print("Поиск пути от url2 к url1")
    path_end_to_start = find_first_path(end_url, start_url, rate_limit)

    if path_end_to_start:
        print(f"Путь от {end_url} к {start_url}:")
        print(" -> ".join(path_end_to_start))

    else:
        print(f"Путь от {end_url} к {start_url} не найден за {5} переходов.")


# Входные данные
start_url = "https://en.wikipedia.org/wiki/Six_degrees_of_separation"  # url1
end_url = "https://en.wikipedia.org/wiki/American_Broadcasting_Company"  # url2
rate_limit = 10

# Запуск скрипта
main(start_url, end_url, rate_limit)