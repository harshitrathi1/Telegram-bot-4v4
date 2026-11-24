from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from database.db import Session
from database.models import User, Transaction
from config import SIGNUP_BONUS, REFERRAL_BONUS

router=Router()

def menu():
    kb=InlineKeyboardBuilder()
    for label, data in [("📋 Tasks","tasks"),("🪙 Wallet","wallet"),("🎁 Daily bonus","daily"),("🔗 Referral","ref"),("ℹ️ Help","help")]:
        kb.button(text=label, callback_data=data)
    kb.adjust(2,2,1)
    return kb.as_markup()

@router.message(CommandStart())
async def start(m: Message):
    args=m.text.split(maxsplit=1)
    ref=None
    if len(args)>1 and args[1].isdigit() and int(args[1])!=m.from_user.id:
        ref=int(args[1])
    async with Session() as s:
        u=await s.get(User,m.from_user.id)
        if not u:
            u=User(id=m.from_user.id, username=m.from_user.username or "", balance=SIGNUP_BONUS, referred_by=ref)
            s.add(u)
            s.add(Transaction(user_id=u.id,amount=SIGNUP_BONUS,reason="Signup bonus"))
            if ref:
                parent=await s.get(User,ref)
                if parent:
                    parent.balance += REFERRAL_BONUS
                    s.add(Transaction(user_id=ref,amount=REFERRAL_BONUS,reason="Referral bonus"))
            await s.commit()
        elif u.is_banned:
            await m.answer("Aapka account access restricted hai. Admin se contact karein.")
            return
    await m.answer("Namaste! 👋\nFollow Task Hub mein welcome.\nYahan simple tasks aur virtual coins explore karein.", reply_markup=menu())

@router.message(Command("menu"))
async def cmd_menu(m: Message): await m.answer("Main menu:", reply_markup=menu())

@router.callback_query(F.data=="help")
async def help_cb(c: CallbackQuery):
    await c.message.answer("Help:\n• Tasks mein listed activities dekhein.\n• Task complete hone par Done dabayein.\n• Coins sirf virtual points hain; cash value nahi hai.\n• Referral link share karke naye users invite karein.")
    await c.answer()

@router.callback_query(F.data=="ref")
async def ref_cb(c: CallbackQuery):
    me=await c.bot.get_me()
    await c.message.answer(f"Apna invite link:\nhttps://t.me/{me.username}?start={c.from_user.id}\nInvite bonus virtual points hai.")
    await c.answer()

@router.callback_query(F.data=="daily")
async def daily_cb(c: CallbackQuery):
    from config import DAILY_BONUS
    from datetime import date
    async with Session() as s:
        u=await s.get(User,c.from_user.id)
        if not u or u.is_banned:
            await c.answer("Access nahi hai.",show_alert=True); return
        if u.last_daily==date.today():
            await c.answer("Aaj ka bonus already claim ho chuka hai.",show_alert=True); return
        u.balance+=DAILY_BONUS; u.last_daily=date.today()
        s.add(Transaction(user_id=u.id,amount=DAILY_BONUS,reason="Daily bonus"))
        await s.commit()
    await c.message.answer(f"🎁 Aaj ke {DAILY_BONUS} virtual coins mil gaye!")
    await c.answer()

@router.callback_query(F.data=="wallet")
async def wallet_cb(c: CallbackQuery):
    async with Session() as s:
        u=await s.get(User,c.from_user.id)
        if not u: await c.answer("Pehle /start karein.",show_alert=True); return
        res=await s.execute(select(Transaction).where(Transaction.user_id==u.id).order_by(Transaction.id.desc()).limit(8))
        tx=res.scalars().all()
    lines=[f"🪙 Balance: {u.balance} coins","Recent transactions:"]
    lines += [f"{'+' if t.amount>=0 else ''}{t.amount} — {t.reason}" for t in tx] or ["No transactions yet."]
    await c.message.answer("\n".join(lines)); await c.answer()
