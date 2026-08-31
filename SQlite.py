# ==========================================
# 1. ИМПОРТЫ
# ==========================================

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import sqlite3

# Bot — отправляет сообщения
# Dispatcher — обрабатывает команды
# types — типы данных (сообщения, кнопки)
# Command — ловит команды типа /start
# sqlite3 — работа с базой данных

# ==========================================
# 2. НАСТРОЙКИ
# ==========================================

TOKEN = "ТВОЙ_ТОКЕН"  # Токен бота от @BotFather

bot = Bot(token=TOKEN)  # Создаём бота
dp = Dispatcher()  # Создаём диспетчер

# ==========================================
# 3. ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
# ==========================================

conn = sqlite3.connect('notes.db')  # Создаём файл notes.db (или подключаемся)
cursor = conn.cursor()  # Создаём курсор — это как "ручка" для запросов

# Создаём таблицу notes, если её нет
# id — номер заметки (автоматически увеличивается)
# user_id — ID пользователя в Telegram
# text — текст заметки
# created_at — дата создания (автоматически)
cursor.execute('''
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()  # Сохраняем изменения


# ==========================================
# 4. КОМАНДА /start
# ==========================================

@dp.message(Command("start"))
async def start(message: types.Message):
    """
    Приветствие и список команд
    """
    await message.answer(
        "📝 Бот для заметок\n\n"
        "Команды:\n"
        "/add [текст] — добавить заметку\n"
        "/list — показать все заметки\n"
        "/del [номер] — удалить заметку\n"
        "/clear — удалить все заметки"
    )


# ==========================================
# 5. КОМАНДА /add
# ==========================================

@dp.message(Command("add"))
async def add_note(message: types.Message):
    """
    Добавляет новую заметку в базу данных
    """
    user_id = message.from_user.id  # Получаем ID пользователя

    # Получаем текст заметки (всё, что после /add)
    text = message.text.replace("/add", "").strip()

    # Если текст пустой — сообщаем об ошибке
    if not text:
        await message.answer("❌ Напиши текст заметки после /add")
        return

    # Сохраняем заметку в базу
    cursor.execute('''
    INSERT INTO notes (user_id, text) 
    VALUES (?, ?)
    ''', (user_id, text))
    conn.commit()  # Сохраняем изменения

    await message.answer(f"✅ Заметка добавлена!\n📝 {text}")


# ==========================================
# 6. КОМАНДА /list
# ==========================================

@dp.message(Command("list"))
async def list_notes(message: types.Message):
    """
    Показывает все заметки пользователя
    """
    user_id = message.from_user.id

    # Получаем все заметки пользователя
    cursor.execute('''
    SELECT id, text, created_at FROM notes 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()

    # Если заметок нет
    if not rows:
        await message.answer("📭 У тебя пока нет заметок.")
        return

    # Формируем сообщение со списком заметок
    text = "📋 **Твои заметки:**\n\n"
    for row in rows:
        note_id = row[0]  # ID заметки
        note_text = row[1]  # Текст заметки
        date = row[2][:10]  # Дата (первые 10 символов)
        text += f"{note_id}. {note_text}  _( {date} )_\n"

    await message.answer(text)


# ==========================================
# 7. КОМАНДА /del
# ==========================================

@dp.message(Command("del"))
async def delete_note(message: types.Message):
    """
    Удаляет заметку по номеру
    """
    user_id = message.from_user.id

    # Получаем номер заметки (всё, что после /del)
    parts = message.text.split()

    # Если нет номера
    if len(parts) < 2:
        await message.answer("❌ Укажи номер заметки: /del 1")
        return

    try:
        note_id = int(parts[1])  # Превращаем строку в число
    except ValueError:
        await message.answer("❌ Номер должен быть числом!")
        return

    # Проверяем, что заметка принадлежит пользователю
    cursor.execute('''
    SELECT id FROM notes 
    WHERE id = ? AND user_id = ?
    ''', (note_id, user_id))
    row = cursor.fetchone()

    if not row:
        await message.answer(f"❌ Заметка #{note_id} не найдена или не твоя!")
        return

    # Удаляем заметку
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()

    await message.answer(f"🗑️ Заметка #{note_id} удалена!")


# ==========================================
# 8. КОМАНДА /clear
# ==========================================

@dp.message(Command("clear"))
async def clear_notes(message: types.Message):
    """
    Удаляет все заметки пользователя
    """
    user_id = message.from_user.id

    # Удаляем все заметки пользователя
    cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
    conn.commit()

    await message.answer("🗑️ Все твои заметки удалены!")


# ==========================================
# 9. ЗАПУСК
# ==========================================

async def main():
    print("✅ Бот для заметок запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())