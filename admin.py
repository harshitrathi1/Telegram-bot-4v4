from datetime import datetime, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from database.db import Session
from database.models import User, Task, Transaction, AdminSession
from config import ADMIN_PASSWORD, ADMIN_IDS
router=Router()

def is_admin(u): return u.id in ADMIN_IDS

@router.message(Command("admin"))
async def admin(m: Message):
    if is_admin(m.from_user):
        async with Session() as s:
            user=await s.get(User,m.from_user.id)
            if user: user.is_admin=True; await s.commit()
        await m.answer("Admin access granted (ADMIN_IDS allowlist). Commands: /stats, /addcoins ID AMOUNT, /taskadd REWARD | TITLE | DESCRIPTION, /broadcast MESSAGE")
        return
    await m.answer("Admin login ke liye /admin ke baad password bhejein. (Prototype: password message delete karne ki koshish karega.)")
    # password is handled by next message in prototype; recommend ADMIN_IDS for deployment.

@router.message(Command("stats"))
async def stats(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    async with Session() as s:
        users=(await s.execute(select(func.count(User.id)))).scalar() or 0
        tasks=(await s.execute(select(func.count(Task.id)).where(Task.active==True))).scalar() or 0
        coins=(await s.execute(select(func.sum(User.balance)))).scalar() or 0
    await m.answer(f"📊 Stats\nUsers: {users}\nActive tasks: {tasks}\nCoins in balances: {coins}")

@router.message(Command("addcoins"))
async def addcoins(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    try: _, uid, amount=m.text.split(); uid=int(uid); amount=int(amount)
    except Exception: await m.answer("Usage: /addcoins USER_ID AMOUNT"); return
    async with Session() as s:
        u=await s.get(User,uid)
        if not u: await m.answer("User not found."); return
        u.balance+=amount
        s.add(Transaction(user_id=uid,amount=amount,reason="Admin adjustment"))
        await s.commit()
    await m.answer("Balance updated.")

@router.message(Command("taskadd"))
async def taskadd(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    try:
        _, rest=m.text.split(maxsplit=1)
        reward,title,description=[x.strip() for x in rest.split("|",2)]
        reward=int(reward)
        if reward<0: raise ValueError()
    except Exception:
        await m.answer("Format: /taskadd REWARD | TITLE | DESCRIPTION"); return
    async with Session() as s:
        s.add(Task(title=title,description=description,reward=reward,created_by=m.from_user.id))
        await s.commit()
    await m.answer("Task created.")

@router.message(Command("broadcast"))
async def broadcast(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    text=m.text.partition(" ")[2].strip()
    if not text: await m.answer("Usage: /broadcast MESSAGE"); return
    async with Session() as s:
        ids=(await s.execute(select(User.id))).scalars().all()
    sent=0
    for uid in ids:
        try: await m.bot.send_message(uid,text); sent+=1
        except Exception: pass
    await m.answer(f"Broadcast complete. Sent: {sent}")

@router.message(Command("ban"))
async def ban(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    try: uid=int(m.text.split()[1])
    except Exception: await m.answer("Usage: /ban USER_ID"); return
    async with Session() as s:
        u=await s.get(User,uid)
        if not u: await m.answer("User not found."); return
        u.is_banned=True; await s.commit()
    await m.answer("User banned.")

@router.message(Command("unban"))
async def unban(m: Message):
    if not is_admin(m.from_user): await m.answer("Access denied."); return
    try: uid=int(m.text.split()[1])
    except Exception: await m.answer("Usage: /unban USER_ID"); return
    async with Session() as s:
        u=await s.get(User,uid)
        if not u: await m.answer("User not found."); return
        u.is_banned=False; await s.commit()
    await m.answer("User unbanned.")
