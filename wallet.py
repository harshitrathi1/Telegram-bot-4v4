from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import Session
from database.models import User
router=Router()

@router.message(Command("wallet"))
async def wallet_cmd(m: Message):
    async with Session() as s:
        u=await s.get(User,m.from_user.id)
    if not u: await m.answer("Pehle /start karein."); return
    await m.answer(f"🪙 Aapka balance: {u.balance} virtual coins")
