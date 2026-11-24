from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import Session
from database.models import User, Task, TaskClaim, Transaction

router=Router()

@router.callback_query(F.data=="tasks")
async def list_tasks(c: CallbackQuery):
    async with Session() as s:
        res=await s.execute(select(Task).where(Task.active==True).order_by(Task.id.desc()))
        tasks=res.scalars().all()
        claims=await s.execute(select(TaskClaim.task_id).where(TaskClaim.user_id==c.from_user.id))
        done=set(claims.scalars().all())
    if not tasks:
        await c.message.answer("Abhi koi task available nahi hai. Baad mein check karein.")
    for t in tasks:
        kb=InlineKeyboardBuilder()
        if t.id in done: kb.button(text="✅ Completed",callback_data="noop")
        else: kb.button(text="Done",callback_data=f"claim:{t.id}")
        kb.adjust(1)
        await c.message.answer(f"<b>{t.title}</b>\n{t.description}\nReward: {t.reward} virtual coins",reply_markup=kb.as_markup())
    await c.answer()

@router.callback_query(F.data.startswith("claim:"))
async def claim(c: CallbackQuery):
    tid=int(c.data.split(":")[1])
    async with Session() as s:
        u=await s.get(User,c.from_user.id)
        t=await s.get(Task,tid)
        if not u or u.is_banned or not t or not t.active:
            await c.answer("Task available nahi hai.",show_alert=True); return
        existing=await s.execute(select(TaskClaim).where(TaskClaim.task_id==tid,TaskClaim.user_id==u.id))
        if existing.scalar_one_or_none():
            await c.answer("Ye task pehle complete kiya hai.",show_alert=True); return
        s.add(TaskClaim(task_id=tid,user_id=u.id))
        u.balance+=t.reward
        s.add(Transaction(user_id=u.id,amount=t.reward,reason=f"Task #{tid} reward"))
        await s.commit()
    await c.message.answer(f"Task complete! {t.reward} virtual coins add hue.")
    await c.answer("Done!")

@router.callback_query(F.data=="noop")
async def noop(c: CallbackQuery): await c.answer()
