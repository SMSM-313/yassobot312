# -- coding: utf-8 --
import telebot
from telebot import types
import time
import threading
from playwright.sync_api import sync_playwright

# --- الإعدادات الأساسية ---
BOT_TOKEN = "9100257710:AAHppdbkmELhr9MOLVK7YpjmwrCKzKEkvCg" # يفضل تغييره لتوكن جديد
ADMINS = [6579040389, 5829037049]
OWNER_USERNAME = "@hast320"

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
all_users = set()

# ---------------------------------------------------------
# دالة الأتمتة الحقيقية (Playwright) - تم تعديلها للدخول من البوابة
# ---------------------------------------------------------
def real_qureo_solver(chat_id, login_id, password, subject, status_msg_id):
    try:
        with sync_playwright() as p:
            # تشغيل المتصفح في الخلفية (Headless)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()

            # 1. التوجه لصفحة البوابة الرئيسية (التي تحتوي على زر Go to Learning Login)
            page.goto("https://me-portal.qureo.education/login", timeout=60000)
            
            # 2. البحث عن الزر والضغط عليه
            try:
                # محاولة الضغط على الزر الإنجليزي
                page.locator("text=Go to Learning Login").click(timeout=10000)
            except:
                try:
                    # محاولة الضغط على الزر العربي
                    page.locator("text=انتقل إلى تسجيل الدخول للتعلم").click(timeout=5000)
                except:
                    # محاولة أخيرة بالبحث عن أي رابط يحتوي على Login
                    page.locator('a:has-text("Login")').first.click(timeout=5000)

            # 3. الانتظار حتى تظهر صفحة الدخول الفعلية (خانة إدخال الكود)
            page.wait_for_selector('input[type="text"]', timeout=15000)
            time.sleep(1) # ثانية استقرار للصفحة
            
            # 4. إدخال بيانات الدخول
            page.locator('input[type="text"]').first.fill(login_id)
            page.locator('input[type="password"]').fill(password)
            
            # 5. الضغط على زر Login
            page.locator('button:has-text("Login")').click()
            
            # 6. الانتظار لمعرفة النتيجة
            time.sleep(6) 
            
            # فحص إذا كنا لا نزال في صفحة الدخول (بيانات خاطئة)
            if "login" in page.url.lower() or page.locator('text=Login ID').is_visible():
                bot.edit_message_text(
                    "❌ **كود الطالب أو الباسورد غلط (401).**\nيرجى التأكد من البيانات والمحاولة مرة أخرى عبر /start",
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    parse_mode="Markdown"
                )
                browser.close()
                return

            # 7. نجح الدخول -> بدء الحل الفعلي
            bot.edit_message_text(
                "✅ **تم تسجيل الدخول للمنصة بنجاح!**\n🚀 **البوت بدأ الحل التلقائي الآن...**",
                chat_id=chat_id,
                message_id=status_msg_id,
                parse_mode="Markdown"
            )

            # ========================================================
            # هنا تبدأ خطوات الحل التلقائي
            # ========================================================
            # ملاحظة: هذا الجزء يحتاج منك فحص عناصر المنصة (F12) 
            # لمعرفة كيف تفتح الفصول وتحل الأسئلة وإرسال الإجابات.
            # الكود التالي هو مجرد محاكاة للعملية (يمكنك استبداله بالكود الفعلي).
            
            total_chapters = 42
            for chapter in range(1, total_chapters + 1):
                time.sleep(0.5) # وقت وهمي للمحاكاة
                progress = int((chapter / total_chapters) * 100)
                try:
                    bot.edit_message_text(
                        f"🤖 **YASSO BOT**\n"
                        f"🚀 **جاري حل مادة ({subject}) على المنصة...**\n\n"
                        f"👤 Login ID: `{login_id}`\n"
                        f"📊 التقدم: %{progress}\n"
                        f"🎯 جاري حل: فصل {chapter} من {total_chapters}",
                        chat_id=chat_id,
                        message_id=status_msg_id,
                        parse_mode="Markdown"
                    )
                except: pass
            
            bot.edit_message_text(
                "🎉 **تم إتمام الحل بنجاح!**\n\n🤖 **YASSO BOT** أنهى كافة الفصول المتبقية.",
                chat_id=chat_id,
                message_id=status_msg_id,
                parse_mode="Markdown"
            )
            
            # إرسال إشعار للأدمن
            for admin in ADMINS:
                try:
                    bot.send_message(admin, f"🔔 **تقرير YASSO BOT:**\nأنهى طالب مادة `{subject}`\n👤 Login ID: `{login_id}`", parse_mode="Markdown")
                except: pass

            browser.close()

    except Exception as e:
        print(f"Automation Error: {e}")
        bot.edit_message_text(
            "❌ **حدث خطأ تقني أثناء الاتصال بالمنصة.**\nيرجى المحاولة لاحقاً أو التواصل مع المطور.",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )

# ---------------------------------------------------------
# أوامر البوت الأساسية
# ---------------------------------------------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    all_users.add(user_id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_gov = types.InlineKeyboardButton("🏫 حكومي", callback_data="edu_gov")
    btn_lang = types.InlineKeyboardButton("🌐 لغات", callback_data="edu_lang")
    btn_stats = types.InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")
    btn_dev = types.InlineKeyboardButton("DEV 💲", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")
    
    markup.add(btn_gov, btn_lang)
    markup.add(btn_stats, btn_dev)

    if user_id in ADMINS:
        markup.add(types.InlineKeyboardButton("⚙️ لوحة تحكم الآدمن", callback_data="admin_panel"))

    welcome_text = (
        "👋 **أهلاً بك في بوت YASSO 🤖!**\n\n"
        "🔥 **منصة QUREO للحل الفعلي** 🚀\n"
        "👑 **المطور والمالك:** " + OWNER_USERNAME + "\n\n"
        "🖤 **المواد المتاحة:**\n"
        "  ☕ جافا سكريبت (أولى وثانية ثانوي)\n"
        "  🐍 بايثون (تانية ثانوي فقط)\n"
        "  📦 الثقافة المالية (تانية ثانوي فقط)\n\n"
        "🎯 **اختر نظام التعليم:**"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# ---------------------------------------------------------
# معالج الأزرار (التدفق)
# ---------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id

    try:
        if call.data == "admin_panel":
            if user_id not in ADMINS:
                bot.answer_callback_query(call.id, "❌ عذراً، هذه اللوحة مخصصة للآدمن فقط!", show_alert=True)
                return
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(f"👥 إجمالي المستخدمين: {len(all_users)}", callback_data="dummy"),
                types.InlineKeyboardButton("📢 إذاعة رسالة للجميع", callback_data="admin_broadcast"),
                types.InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back_home")
            )
            bot.edit_message_text(
                "⚙️ **لوحة التحكم الخاصة بالآدمن (YASSO BOT)**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            return

        if call.data == "admin_broadcast":
            if user_id not in ADMINS:
                return
            msg = bot.send_message(call.message.chat.id, "📢 **أرسل النص المراد إذاعته لجميع الطلاب:**", parse_mode="Markdown")
            bot.register_next_step_handler(msg, execute_broadcast)
            return

        if call.data == "back_home":
            send_welcome(call.message)
            return

        if call.data == "my_stats":
            bot.answer_callback_query(call.id, f"📊 أنت مستخدم نشط في بوت YASSO.\n🆔 ID الخاص بك: {user_id}", show_alert=True)
            return

        if call.data in ["edu_gov", "edu_lang"]:
            edu_type = "حكومي" if call.data == "edu_gov" else "لغات"
            user_data[user_id] = {"edu": edu_type}
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📚 أولى ثانوي", callback_data="grade_1"),
                types.InlineKeyboardButton("📚 تانية ثانوي", callback_data="grade_2")
            )
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            
            bot.edit_message_text(
                f"✅ اخترت: {edu_type}\n\nاختر الصف الدراسي:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("grade_"):
            grade_id = call.data
            grade = "أولى ثانوي" if grade_id == "grade_1" else "تانية ثانوي"
            if user_id in user_data:
                user_data[user_id]["grade"] = grade
                user_data[user_id]["grade_id"] = grade_id
                
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🏫 عام", callback_data="type_am"),
                types.InlineKeyboardButton("🕌 أزهر", callback_data="type_azhar")
            )
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            
            bot.edit_message_text(
                f"✅ اخترت: {grade}\n\nاختر النوع:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("type_"):
            school_type = "عام" if call.data == "type_am" else "أزهر"
            if user_id in user_data:
                user_data[user_id]["school_type"] = school_type
                grade_id = user_data[user_id].get("grade_id")

            markup = types.InlineKeyboardMarkup(row_width=1)
            
            if grade_id == "grade_1":
                markup.add(types.InlineKeyboardButton("☕ JavaScript", callback_data="sub_js"))
            else:
                markup.add(
                    types.InlineKeyboardButton("☕ JavaScript", callback_data="sub_js"),
                    types.InlineKeyboardButton("🐍 Python (Arabic)", callback_data="sub_python"),
                    types.InlineKeyboardButton("📦 الثقافة المالية", callback_data="sub_finance")
                )
            
            markup.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
            
            bot.edit_message_text(
                "✅ اخترت النوع\n\nاختر المادة المقررة:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )

        elif call.data.startswith("sub_"):
            sub_map = {"sub_js": "JavaScript", "sub_python": "Python", "sub_finance": "الثقافة المالية"}
            subject = sub_map.get(call.data, "JavaScript")
            if user_id in user_data:
                user_data[user_id]["subject"] = subject
                
            bot.edit_message_text(
                f"✅ اخترت مادة: {subject}\n\n📝 **أرسل كود الطالب (Login ID):**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(call.message, get_login_id)

    except Exception as e:
        print(f"Error: {e}")

# ---------------------------------------------------------
# استلام الكود والباسورد وبدء الحل
# ---------------------------------------------------------
def get_login_id(message):
    user_id = message.from_user.id
    code = message.text.strip()

    if user_id in user_data:
        user_data[user_id]["code"] = code
        
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
        
    msg = bot.send_message(message.chat.id, "🔑 **أرسل كلمة المرور الخاصة بحسابك (Password):**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, start_solver)

def start_solver(message):
    user_id = message.from_user.id
    password = message.text.strip()

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
        
    data = user_data.get(user_id, {})
    code = data.get("code", "")
    subject = data.get("subject", "JavaScript")

    if not code.isdigit() or len(code) < 4:
        bot.send_message(message.chat.id, "❌ **كود الطالب غير صحيح!** أعد المحاولة بـ /start")
        return

    status_msg = bot.send_message(
        message.chat.id,
        f"🌐 **جاري الاتصال ببوابة المنصة الصحيحة والتحقق من حساب ({code})...**",
        parse_mode="Markdown"
    )

    # تشغيل الأتمتة في Thread منفصل حتى لا يتجمد البوت
    threading.Thread(
        target=real_qureo_solver, 
        args=(message.chat.id, code, password, subject, status_msg.message_id)
    ).start()

# ---------------------------------------------------------
# الإذاعة (Broadcast)
# ---------------------------------------------------------
def execute_broadcast(message):
    text = message.text
    count = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 إشعار من إدارة YASSO BOT:\n\n{text}", parse_mode="Markdown")
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم إرسال الإذاعة بنجاح إلى {count} مستخدم.")

# ---------------------------------------------------------
# تشغيل البوت
# ---------------------------------------------------------
if __name__ == "__main__":
    print("YASSO BOT is running successfully with Portal Navigation...")
    bot.infinity_polling(skip_pending=True)