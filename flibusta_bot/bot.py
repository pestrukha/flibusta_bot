import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from bs4 import BeautifulSoup

# Замените на ваш токен
API_TOKEN = '7597437065:AAGQrQHsdnMuEeuvRlBAfwXwKS2lzxd_omc'

logging.basicConfig(level=logging.INFO)

# Создаем объект бота
bot = Bot(token=API_TOKEN)

# Создаем диспетчер (без передачи bot напрямую в Dispatcher)
dp = Dispatcher()

# Функция для поиска книги на Флибусте
async def search_book(query: str):
    search_url = f'https://flibusta.is/search/?q={query}'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(search_url) as response:
                if response.status != 200:
                    return "Не удалось найти книгу, попробуйте позже."
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Ищем ссылки на книги на странице поиска
                book_results = soup.find_all('div', class_='book')

                if not book_results:
                    return "Книги по запросу не найдены."

                books = []
                for book in book_results[:5]:  # Ограничиваем 5 первыми результатами
                    title = book.find('div', class_='bookTitle')
                    author = book.find('div', class_='bookAuthor')
                    link = book.find('a', href=True)['href']

                    if title and author:
                        book_info = f"Название: {title.get_text(strip=True)}\nАвтор: {author.get_text(strip=True)}\nСсылка: https://flibusta.is{link}"
                        books.append(book_info)

                return "\n\n".join(books) if books else "Не удалось найти книги."
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Ошибка подключения: {e}")
            return "Не удалось подключиться к сайту Флибусты. Попробуйте позже."
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            return "Произошла неизвестная ошибка. Попробуйте позже."


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска книг на Флибусте. Просто напиши название книги, и я найду ее для тебя.")


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Отправь мне название книги, и я найду ее на Флибусте.")


# Поиск книг по запросу
@dp.message()
async def search_books(message: types.Message):
    query = message.text
    if not query.strip():
        await message.answer("Пожалуйста, отправь название книги.")
        return

    await message.answer("Ищу книгу на Флибусте...")

    result = await search_book(query)
    await message.answer(result, parse_mode="Markdown")  # Используем строковое значение "Markdown"


# Основная асинхронная функция для запуска бота
async def main():
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Используем asyncio для запуска бота
    asyncio.run(main())
