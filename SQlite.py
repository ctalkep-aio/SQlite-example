
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import sqlite3

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()  

conn = sqlite3.connect('notes.db')
cursor = conn.cursor() 
cursor.execute('''
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit() 
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
@dp.message(Command("add"))
async def add_note(message: types.Message):
    """
    Добавляет новую заметку в базу данных
    """
    user_id = message.from_user.id  
    text = message.text.replace("/add", "").strip()
    if not text:
        await message.answer("❌ Напиши текст заметки после /add")
        return
    cursor.execute('''
    INSERT INTO notes (user_id, text) 
    VALUES (?, ?)
    ''', (user_id, text))
    conn.commit()  
    await message.answer(f"✅ Заметка добавлена!\n📝 {text}")
@dp.message(Command("list"))
async def list_notes(message: types.Message):
    """
    Показывает все заметки пользователя
    """
    user_id = message.from_user.id
    cursor.execute('''
    SELECT id, text, created_at FROM notes 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    if not rows:
        await message.answer("📭 У тебя пока нет заметок.")
        return
    text = "📋 **Твои заметки:**\n\n"
    for row in rows:
        note_id = row[0]  # ID заметки
        note_text = row[1]  # Текст заметки
        date = row[2][:10]  # Дата (первые 10 символов)
        text += f"{note_id}. {note_text}  _( {date} )_\n"

    await message.answer(text)
@dp.message(Command("del"))
async def delete_note(message: types.Message):
    """
    Удаляет заметку по номеру
    """
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажи номер заметки: /del 1")
        return

    try:
        note_id = int(parts[1])  # Превращаем строку в число
    except ValueError:
        await message.answer("❌ Номер должен быть числом!")
        return
    cursor.execute('''
    SELECT id FROM notes 
    WHERE id = ? AND user_id = ?
    ''', (note_id, user_id))
    row = cursor.fetchone()

    if not row:
        await message.answer(f"❌ Заметка #{note_id} не найдена или не твоя!")
        return
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()

    await message.answer(f"🗑️ Заметка #{note_id} удалена!")
@dp.message(Command("clear"))
async def clear_notes(message: types.Message):
    """
    Удаляет все заметки пользователя
    """
    user_id = message.from_user.id
    cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
    conn.commit()

    await message.answer("🗑️ Все твои заметки удалены!")

async def main():
    print("✅ Бот для заметок запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
