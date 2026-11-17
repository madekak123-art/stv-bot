import os, random, string, sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

db = sqlite3.connect("arsip.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS files (kode TEXT PRIMARY KEY, file_id TEXT, type TEXT, caption TEXT)")
db.commit()

def bikin_kode():
    acak = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"STVD002Bot_pic_1_{acak}_O"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Halo! Kirim kode arsip buat bongkar file.")
        return
    kode = context.args[0]
    data = db.execute("SELECT file_id, type FROM files WHERE kode=?", (kode,)).fetchone()
    if not data:
        await update.message.reply_text("❌ Kode gak ketemu / udah dihapus.")
        return
    file_id, ftype = data
    await update.message.reply_text(f"📦 BONGKAR ARSIP\nMenampilkan Arsip Halaman 1 dari 1...\nKode Unik: {kode}\n\n⚙️ SHARING RULES:\n├ Restrict Mode: Tidak\n└ Sekali Lihat: Tidak\n\nPowered by @STVD002Bot")
    if ftype == "photo":
        await update.message.reply_photo(file_id, caption=f"File ke-1/1\nKode: {kode}")
    elif ftype == "video":
        await update.message.reply_video(file_id, caption=f"File ke-1/1\nKode: {kode}")
    else:
        await update.message.reply_document(file_id, caption=f"File ke-1/1\nKode: {kode}")

async def simpan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    file_id = None
    ftype = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        ftype = "photo"
    elif update.message.video:
        file_id = update.message.video.file_id
        ftype = "video"
    elif update.message.document:
        file_id = update.message.document.file_id
        ftype = "document"
    if not file_id:
        return
    kode = bikin_kode()
    db.execute("INSERT INTO files VALUES (?,?,?,?)", (kode, file_id, ftype, ""))
    db.commit()
    bot_username = (await context.bot.get_me()).username
    await update.message.reply_text(f"✅ Tersimpan!\nKode Unik: {kode}\nLink: https://t.me/{bot_username}?start={kode}")

async def id_saya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID lu: {update.effective_user.id}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", id_saya))
app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, simpan))
app.run_polling()
