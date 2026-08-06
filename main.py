import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

# ==================== الإعدادات ====================
BOT_TOKEN = os.getenv("8967781339:AAGkMaJVDOMjLXmySGt1HoQXP-9iyq0GC9A")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing")
CHANNELS_TO_CHECK = ["@ddev8"]
YOUTUBE_URL = "https://youtube.com/@devinstagram?si=e9YNvnDylP2wC4XL"
TELEGRAM_URL = "https://t.me/ddev8"
SUPPORT_URL = "https://t.me/dvve1"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== حالات FSM لمولّد الاستئناف الذكي ====================
class AppealForm(StatesGroup):
    waiting_username = State()
    waiting_fullname = State()
    waiting_email = State()
    waiting_reason = State()
    waiting_years = State()
    waiting_purpose = State()

# ==================== دالة التحقق من الاشتراك ====================
async def is_subscribed(user_id: int) -> bool:
    for channel in CHANNELS_TO_CHECK:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ("member", "administrator", "creator"):
                return True
            return False
        except Exception as e:
            logging.error(f"خطأ في التحقق من الاشتراك للمستخدم {user_id}: {e}")
            return False
    return False

# ==================== لوحات المفاتيح ====================
def get_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 اشترك في قناة التيليجرام", url=TELEGRAM_URL))
    builder.row(InlineKeyboardButton(text="▶️ اشترك في قناة اليوتيوب", url=YOUTUBE_URL))
    builder.row(InlineKeyboardButton(text="✅ تحقق من الاشتراك الآن", callback_data="verify_sub"))
    return builder.as_markup()

def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔗 قسم الروابط الرسمية", callback_data="section_links"))
    builder.row(InlineKeyboardButton(text="📝 قسم صيغ الاستئناف", callback_data="section_templates"))
    builder.row(InlineKeyboardButton(text="🤖 مولّد الاستئناف الذكي (AI)", callback_data="section_ai"))
    builder.row(InlineKeyboardButton(text="📧 قسم الإيميلات الرسمية", callback_data="section_emails"))
    builder.row(InlineKeyboardButton(text="🔄 روابط إعادة التعيين", callback_data="section_reset"))
    builder.row(InlineKeyboardButton(text="💡 نصائح ذهبية للنجاح", callback_data="section_tips"))
    builder.row(InlineKeyboardButton(text="❓ أسئلة شائعة", callback_data="section_faq"))
    builder.row(InlineKeyboardButton(text="💰 الاشتراك في البوت المدفوع", callback_data="section_paid"))
    return builder.as_markup()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main"))
    return builder.as_markup()

def get_links_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="رابط 1 • استئناف عبر Meta Support", callback_data="link1"))
    builder.row(InlineKeyboardButton(text="رابط 2 • استئناف عبر Instagram Help", callback_data="link2"))
    builder.row(InlineKeyboardButton(text="رابط 3 • نموذج الاستئناف الهندي", callback_data="link3"))
    builder.row(InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_main"))
    return builder.as_markup()

def get_templates_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="صيغة 1 • استئناف مهني قوي", callback_data="template1"))
    builder.row(InlineKeyboardButton(text="صيغة 2 • استئناف شخصي عاطفي", callback_data="template2"))
    builder.row(InlineKeyboardButton(text="صيغة 3 • استئناف شامل ومفصل", callback_data="template3"))
    builder.row(InlineKeyboardButton(text="صيغة 4 • استئناف مختصر ومباشر", callback_data="template4"))
    builder.row(InlineKeyboardButton(text="صيغة 5 • استئناف بعد اختراق", callback_data="template5"))
    builder.row(InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_main"))
    return builder.as_markup()

def get_emails_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="support@instagram.com", callback_data="email1"),
        InlineKeyboardButton(text="appeals@instagram.com", callback_data="email2")
    )
    builder.row(
        InlineKeyboardButton(text="security@mail.instagram.com", callback_data="email3"),
        InlineKeyboardButton(text="feedback@instagram.com", callback_data="email4")
    )
    builder.row(
        InlineKeyboardButton(text="help@instagram.com", callback_data="email5"),
        InlineKeyboardButton(text="appeals@meta.com", callback_data="email6")
    )
    builder.row(InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_main"))
    return builder.as_markup()

def get_reset_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🔗 إعادة تعيين كلمة المرور العادية",
        url="https://www.instagram.com/accounts/password/reset/?source=fxcal"
    ))
    builder.row(InlineKeyboardButton(
        text="🔗 استرجاع الحساب المخترق / المبند",
        url="https://www.instagram.com/hacked/"
    ))
    builder.row(InlineKeyboardButton(
        text="🔗 صفحة الدعم الرسمي",
        url="https://help.meta.com/"
    ))
    builder.row(InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_main"))
    return builder.as_markup()

def get_paid_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💬 تواصل للاشتراك @dvve1", url=SUPPORT_URL))
    builder.row(InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_main"))
    return builder.as_markup()

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ إلغاء العملية", callback_data="cancel_ai"))
    return builder.as_markup()

# ==================== Handlers الأساسية ====================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    if await is_subscribed(message.from_user.id):
        await message.answer(
            "✅ <b>تم التحقق من اشتراكك بنجاح</b>\n\n"
            "مرحباً بك في <b>أقوى بوت لاسترجاع حسابات إنستقرام</b>\n"
            "اختر القسم المطلوب من القائمة أدناه:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "⚠️ <b>يجب الاشتراك في قنواتنا أولاً</b>\n\n"
            "اشترك في قناة التيليجرام وقناة اليوتيوب، ثم اضغط على زر التحقق.",
            reply_markup=get_subscription_keyboard(),
            parse_mode="HTML"
        )

@dp.callback_query(F.data == "verify_sub")
async def verify_sub_handler(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text(
            "✅ <b>تم التحقق بنجاح</b>\n\n"
            "مرحباً بك! اختر القسم الذي تريده:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ لم تشترك بعد. اشترك في القنوات ثم اضغط تحقق مرة أخرى.", show_alert=True)

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "اختر القسم الذي تريده من القائمة:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "cancel_ai")
async def cancel_ai(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "تم إلغاء العملية.\nاختر القسم الذي تريده:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

# --- قسم الروابط ---
@dp.callback_query(F.data == "section_links")
async def section_links(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔗 <b>قسم الروابط الرسمية</b>\n\n"
        "اختر الرابط المناسب ثم انسخ الصيغة المرفقة معه واستخدمها في النموذج:",
        reply_markup=get_links_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "link1")
async def link1_handler(callback: types.CallbackQuery):
    text = (
        "🔗 <b>الرابط:</b>\n"
        "https://www.meta.com/help/work/contact/599317765457601\n\n"
        "────────────────────────\n"
        "<b>الصيغة المقترحة:</b>\n\n"
        "Hello Instagram Support Team,\n\n"
        "I am writing to formally appeal the disabling of my Instagram account associated with the username [ضع اسم المستخدم هنا].\n\n"
        "I fully understand that my account was disabled due to a violation of Instagram’s Community Guidelines. I sincerely apologize for this unintentional mistake. At the time, I was not completely aware of the specific policies, and I take full responsibility for not reviewing them thoroughly beforehand.\n\n"
        "Since receiving the disablement notice, I have carefully and thoroughly reviewed Instagram’s Community Guidelines and Terms of Use multiple times. I now have a clear and complete understanding of all the rules and expectations. I am genuinely committed to following every policy strictly and without exception moving forward. This experience has been an important lesson, and I assure you that I will never repeat any action that could violate the platform’s standards.\n\n"
        "My Instagram account is extremely important to me. It is my primary way of staying connected with family, friends, and my community. I deeply value the positive environment Instagram provides and I am eager to return as a responsible and respectful member of the platform.\n\n"
        "I kindly and respectfully request that you review my account and consider reactivating it. I am confident that I will uphold all Instagram policies with complete respect and responsibility.\n\n"
        "Thank you very much for your time, understanding, and for giving me the opportunity to appeal. I truly appreciate your support and look forward to your positive response.\n\n"
        "Best regards,\n"
        "[ضع اسمك الكامل هنا]\n"
        "[ضع بريدك الإلكتروني المرتبط بالحساب هنا]\n"
        "Username: [ضع اسم المستخدم هنا]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer("✅ تم إرسال الرابط والصيغة")

@dp.callback_query(F.data == "link2")
async def link2_handler(callback: types.CallbackQuery):
    text = (
        "🔗 <b>الرابط:</b>\n"
        "https://help.instagram.com/contact/814820110107093\n\n"
        "────────────────────────\n"
        "<b>الصيغة المقترحة:</b>\n\n"
        "Dear Instagram Support Team,\n\n"
        "I am writing to formally appeal the disabling of my Instagram account @[اسم المستخدم]. The account was disabled without any prior warning or clear explanation, and I strongly believe this action was taken in error.\n\n"
        "I have always strictly complied with Instagram’s Community Guidelines and Terms of Use. I have never engaged in any prohibited activity, including:\n"
        "• Spam, mass following/unfollowing, or automated behavior\n"
        "• Impersonation or misrepresentation of any individual or brand\n"
        "• Posting or sharing inappropriate, violent, hateful, or misleading content\n"
        "• Using any unauthorized third-party tools, bots, or services\n"
        "• Any other violation of your policies\n\n"
        "My account is extremely important to me both personally and professionally. It is my primary platform for [اكتب هنا سبب أهميته باختصار]. The sudden disabling has caused me significant emotional distress and professional inconvenience, as I can no longer access my content, messages, or community.\n\n"
        "I respectfully request that you conduct a thorough and expedited review of my account and restore it immediately. I am fully prepared to provide any additional information, identity verification, or documentation you may require to resolve this matter quickly.\n\n"
        "I have been a long-time, responsible user of Instagram and greatly value the platform. I trust that this situation can be resolved promptly and fairly.\n\n"
        "Thank you in advance for your urgent attention and support. I look forward to your positive response at the earliest possible time.\n\n"
        "Best regards,\n"
        "[اسمك الكامل]\n"
        "Instagram Username: @[اسم المستخدم]\n"
        "Email: [بريدك الإلكتروني المرتبط بالحساب]\n"
        "Phone: [رقم هاتفك - اختياري]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer("✅ تم إرسال الرابط والصيغة")

@dp.callback_query(F.data == "link3")
async def link3_handler(callback: types.CallbackQuery):
    text = (
        "🔗 <b>الرابط:</b>\n"
        "https://help.meta.com/requests/1371776380779082\n\n"
        "────────────────────────\n"
        "<b>الصيغة المقترحة (مختصرة وقوية):</b>\n\n"
        "Subject: Request for Account Review and Reinstatement – @[Username]\n\n"
        "Dear Instagram Support Team,\n\n"
        "I am the rightful owner of the Instagram account @[Username]. My account was recently disabled, and I believe this action was taken in error.\n\n"
        "I have carefully reviewed Instagram’s Community Guidelines and Terms of Use and can confirm that I have not intentionally violated any policies. I have always used the platform responsibly and respectfully.\n\n"
        "This account is very important to me for personal and professional reasons. I kindly request a thorough manual review of my account and its reinstatement at the earliest opportunity.\n\n"
        "I am ready to provide any verification documents you may require (government ID, selfie verification, etc.).\n\n"
        "Thank you for your time and support.\n\n"
        "Best regards,\n"
        "[Full Name]\n"
        "Email: [Associated Email]\n"
        "Username: @[Username]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer("✅ تم إرسال الرابط والصيغة")

# --- قسم الصيغ الجديدة ---
@dp.callback_query(F.data == "section_templates")
async def section_templates(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 <b>قسم صيغ الاستئناف الاحترافية</b>\n\n"
        "اختر الصيغة المناسبة، انسخها، وعدّل البيانات الشخصية حسب حالتك:",
        reply_markup=get_templates_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "template1")
async def template1_handler(callback: types.CallbackQuery):
    text = (
        "📝 <b>صيغة 1 • استئناف مهني قوي</b>\n"
        "────────────────────────\n\n"
        "Dear Instagram Support Team,\n\n"
        "My name is [Your Full Name], and I am the owner of the Instagram account @[Your Username]. I am writing this formal appeal to request the reinstatement of my account, which I firmly believe was disabled in error.\n\n"
        "My account has been active for over [Number] years and has served as a professional platform for [Describe purpose: growing my business / sharing educational content / building a professional community / promoting my brand]. I have consistently maintained high content standards and have never posted material that violates Instagram’s Community Standards or Terms of Service.\n\n"
        "I have invested substantial time and resources into developing this account. It currently has approximately [Number] followers and generates meaningful engagement through valuable content. The sudden disablement has caused serious disruption to my professional activities, including loss of communication with clients and partners, as well as a negative impact on my business operations.\n\n"
        "I have always used Instagram responsibly. I regularly review platform updates to ensure full compliance. There has never been any intentional violation on my part. I suspect the disablement may have resulted from [Customize: coordinated false reports / automated system error / previous security incident that has since been resolved].\n\n"
        "I am fully committed to Instagram’s mission of maintaining a safe environment. I am prepared to provide government-issued identification, a verification video, or any other documentation required to confirm my identity and the legitimacy of my account.\n\n"
        "I respectfully request that your team conduct a thorough manual review and reinstate my account as soon as possible. This account is a vital part of my professional identity and livelihood.\n\n"
        "Thank you for your time and commitment to fairness. I look forward to your positive response.\n\n"
        "Best regards,\n"
        "[Your Full Name]\n"
        "@[Your Username]\n"
        "[Your Email Address]\n"
        "[Your Phone Number]\n"
        "[Your Country]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "template2")
async def template2_handler(callback: types.CallbackQuery):
    text = (
        "📝 <b>صيغة 2 • استئناف شخصي وعاطفي</b>\n"
        "────────────────────────\n\n"
        "Hello Instagram Support Team,\n\n"
        "My name is [Your Full Name] and my Instagram account is @[Your Username]. I am writing with a sincere appeal to have my disabled account reinstated.\n\n"
        "Instagram has been far more than an application to me. For more than [Number] years it has been an essential part of my daily life. Through this account I have maintained genuine connections with family members living far away, close friends, and a community of [Number] followers who have become like an extended family. We share support, celebrate moments, and exchange positive energy every day.\n\n"
        "I have always used my account with care and responsibility. I post content that spreads positivity and helps others feel less alone. I have never posted anything harmful, hateful, or against Instagram’s rules. My content has always been respectful, authentic, and uplifting.\n\n"
        "The sudden disablement has left me feeling disconnected and distressed. I miss the daily interaction with people I care about. This account has supported me through difficult periods in my life, and losing it has created a real sense of isolation.\n\n"
        "I believe this disablement occurred by mistake — possibly due to [Customize: false mass reporting / technical issue / unusual activity from a previous security incident]. I take Instagram’s guidelines very seriously and will continue to be a responsible user.\n\n"
        "I am fully prepared to verify my identity in any way required: a clear photo of my government ID, a verification selfie holding a handwritten note with my name and username, or any other proof you need.\n\n"
        "Please review my case with understanding and restore my account. It means a great deal to me and to the people who follow and support me.\n\n"
        "Thank you from the bottom of my heart for your time and for the work you do to keep Instagram a safe place.\n\n"
        "With sincere gratitude,\n"
        "[Your Full Name]\n"
        "@[Your Username]\n"
        "[Your Email Address]\n"
        "[Your Phone Number]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "template3")
async def template3_handler(callback: types.CallbackQuery):
    text = (
        "📝 <b>صيغة 3 • استئناف شامل ومفصل</b>\n"
        "────────────────────────\n\n"
        "Dear Instagram Support Team,\n\n"
        "I hope this message finds you well. My name is [Your Full Name], and I am the rightful owner of the Instagram account @[Your Username]. I am submitting this comprehensive appeal because I am confident that the disabling of my account was an error that deserves careful reconsideration.\n\n"
        "My account has been active and in good standing for over [Number] years. Throughout this period I have used Instagram as a positive space to [Describe in detail: connect with loved ones / share educational content / run my small business / document personal growth / support charitable causes]. I have built a loyal and engaged community of followers who interact with my content in a healthy and respectful manner.\n\n"
        "I have always made it a priority to stay informed about Instagram’s Community Standards and have strictly followed every rule. I have never posted content involving hate speech, harassment, nudity, spam, misinformation, copyright infringement, or any other prohibited material. My posting history clearly demonstrates consistent, positive, and rule-abiding behavior.\n\n"
        "I was shocked when I discovered that my account had been disabled. After careful reflection I believe this may have occurred due to one of the following: [Customize: sudden wave of false reports / automated detection triggered by temporary unusual login activity / system error]. In any case, I have already taken strong security measures, including changing my password, enabling two-factor authentication, and reviewing all connected devices.\n\n"
        "The impact of losing this account has been significant. It has affected my personal relationships, my professional work, and my ability to stay connected with people who rely on my content. This platform has been an important part of my life, and I remain committed to using it responsibly and positively.\n\n"
        "To demonstrate my good faith and identity, I am fully prepared to provide:\n"
        "• A clear photograph of my government-issued ID\n"
        "• A verification selfie holding a handwritten paper showing my full name, Instagram username, and today’s date\n"
        "• Any additional supporting evidence you may request\n\n"
        "I respectfully request that your team perform a thorough manual review of my account’s history and activity. I am confident that upon review you will see that this account has always been a valuable and compliant member of the Instagram community.\n\n"
        "Thank you sincerely for your time and consideration. I look forward to your favorable response and to having my account reinstated.\n\n"
        "Kind regards,\n"
        "[Your Full Name]\n"
        "@[Your Username]\n"
        "[Your Email Address]\n"
        "[Your Phone Number]\n"
        "[Your Country of Residence]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "template4")
async def template4_handler(callback: types.CallbackQuery):
    text = (
        "📝 <b>صيغة 4 • استئناف مختصر ومباشر</b>\n"
        "────────────────────────\n\n"
        "Subject: Account Reinstatement Request – @[Username]\n\n"
        "Dear Instagram Support Team,\n\n"
        "I am [Full Name], the owner of Instagram account @[Username]. My account was recently disabled, and I believe this decision was made in error.\n\n"
        "I have carefully reviewed the Community Guidelines and Terms of Use. I have never intentionally violated any Instagram policies. My account has always been used in a responsible and respectful manner.\n\n"
        "This account is important to me for both personal and professional reasons. I kindly request a thorough review of my account and its prompt reinstatement.\n\n"
        "I am ready to provide any identity verification or additional information you require.\n\n"
        "Thank you for your attention and support.\n\n"
        "Best regards,\n"
        "[Full Name]\n"
        "Email: [Associated Email]\n"
        "Username: @[Username]\n"
        "Phone: [Optional]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "template5")
async def template5_handler(callback: types.CallbackQuery):
    text = (
        "📝 <b>صيغة 5 • استئناف بعد اختراق أو نشاط مشبوه</b>\n"
        "────────────────────────\n\n"
        "Dear Instagram Support Team,\n\n"
        "My name is [Your Full Name] and I am the legitimate owner of the Instagram account @[Your Username]. I am writing to appeal the disablement of my account, which I believe occurred as a result of unauthorized access or suspicious activity that was not initiated by me.\n\n"
        "Recently my account experienced unusual behavior that I did not authorize. Immediately after noticing the issue I took the following actions:\n"
        "• Changed my password from a secure device\n"
        "• Enabled two-factor authentication\n"
        "• Reviewed and removed any unrecognized devices or sessions\n"
        "• Secured the associated email address\n\n"
        "I have always complied with Instagram’s Community Guidelines and have never used the account for spam, harassment, or any prohibited activity. Any actions that may have triggered the disablement were performed by an unauthorized third party without my knowledge or consent.\n\n"
        "This account is very important to me. It contains years of personal memories, professional connections, and content that I created myself. Losing access has caused significant inconvenience and distress.\n\n"
        "I respectfully request that you review the account activity logs and reinstate my access. I am fully prepared to complete any identity verification process you require, including government ID and selfie verification.\n\n"
        "Thank you for your assistance in resolving this matter. I look forward to regaining access to my account and continuing to use Instagram responsibly.\n\n"
        "Best regards,\n"
        "[Your Full Name]\n"
        "@[Your Username]\n"
        "[Your Email Address]\n"
        "[Your Phone Number]"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

# --- نسخة محسّنة - مولّد الاستئناف الذكي (AI) ---
@dp.callback_query(F.data == "section_ai")
async def section_ai(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    if callback.message is None:
        return

    await state.clear()
    await state.set_state(AppealForm.waiting_username)

    await callback.message.edit_text(
        "🤖 <b>مولّد الاستئناف الذكي</b>\n\n"
        "سأقوم بإنشاء صيغة استئناف مخصصة بناءً على بياناتك.\n\n"
        "أرسل الآن <b>اسم المستخدم</b> بدون علامة @:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@dp.message(AppealForm.waiting_username)
async def process_username(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل اسم المستخدم كنص فقط:",
            reply_markup=get_cancel_keyboard()
        )
        return

    username = message.text.strip().lstrip("@").replace(" ", "")

    if (
        len(username) < 2
        or len(username) > 30
        or not all(
            char.isalnum() or char in "._"
            for char in username
        )
        or username.startswith(".")
        or username.endswith(".")
        or ".." in username
    ):
        await message.answer(
            "⚠️ <b>اسم المستخدم غير صالح.</b>\n\n"
            "استخدم الحروف الإنجليزية والأرقام والنقطة والشرطة السفلية فقط.\n"
            "أرسله مرة أخرى بدون @:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    await state.update_data(username=username)
    await state.set_state(AppealForm.waiting_fullname)

    await message.answer(
        f"✅ تم حفظ: <b>@{username}</b>\n\n"
        "الآن أرسل <b>اسمك الكامل</b>، بالإنجليزية إن أمكن:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@dp.message(AppealForm.waiting_fullname)
async def process_fullname(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل اسمك الكامل كنص فقط:",
            reply_markup=get_cancel_keyboard()
        )
        return

    fullname = " ".join(message.text.strip().split())

    if len(fullname) < 2 or len(fullname) > 80:
        await message.answer(
            "⚠️ الاسم غير صالح، أرسله مرة أخرى:",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(fullname=fullname)
    await state.set_state(AppealForm.waiting_email)

    await message.answer(
        "✅ تم حفظ الاسم.\n\n"
        "الآن أرسل <b>البريد الإلكتروني</b> المرتبط بالحساب:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@dp.message(AppealForm.waiting_email)
async def process_email(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل البريد الإلكتروني كنص فقط:",
            reply_markup=get_cancel_keyboard()
        )
        return

    email = message.text.strip().lower().replace(" ", "")

    if (
        len(email) > 254
        or "@" not in email
        or email.count("@") != 1
        or "." not in email.split("@")[1]
        or email.startswith("@")
        or email.endswith("@")
        or email.endswith(".")
    ):
        await message.answer(
            "⚠️ البريد الإلكتروني غير صالح.\n\n"
            "مثال: name@example.com",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(email=email)
    await state.set_state(AppealForm.waiting_years)

    await message.answer(
        "✅ تم حفظ البريد.\n\n"
        "كم سنة تقريباً لديك الحساب؟\n"
        "مثال: 3 سنوات",
        reply_markup=get_cancel_keyboard()
    )


@dp.message(AppealForm.waiting_years)
async def process_years(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل مدة امتلاك الحساب كنص:",
            reply_markup=get_cancel_keyboard()
        )
        return

    years = " ".join(message.text.strip().split())

    if len(years) < 1 or len(years) > 40:
        await message.answer(
            "⚠️ أرسل مدة مختصرة.\n"
            "مثال: 3 سنوات",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(years=years)
    await state.set_state(AppealForm.waiting_purpose)

    await message.answer(
        "✅ تم.\n\n"
        "اكتب باختصار <b>سبب أهمية الحساب</b> لك:\n\n"
        "مثال: التواصل مع العائلة أو إدارة عملي.",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@dp.message(AppealForm.waiting_purpose)
async def process_purpose(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل سبب أهمية الحساب كنص:",
            reply_markup=get_cancel_keyboard()
        )
        return

    purpose = " ".join(message.text.strip().split())

    if len(purpose) < 3:
        await message.answer(
            "⚠️ وضّح أهمية الحساب بشكل أكبر:",
            reply_markup=get_cancel_keyboard()
        )
        return

    if len(purpose) > 300:
        await message.answer(
            "⚠️ النص طويل جداً، اختصره إلى أقل من 300 حرف:",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(purpose=purpose)
    await state.set_state(AppealForm.waiting_reason)

    await message.answer(
        "✅ تم.\n\n"
        "آخر سؤال:\n"
        "اكتب ما تعتقد أنه <b>سبب تعطيل الحساب</b>:\n\n"
        "مثال: بلاغات كاذبة أو خطأ في النظام أو اختراق سابق.",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@dp.message(AppealForm.waiting_reason)
async def process_reason(
    message: types.Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "⚠️ أرسل سبب التعطيل كنص:",
            reply_markup=get_cancel_keyboard()
        )
        return

    reason = " ".join(message.text.strip().split())

    if len(reason) < 3:
        await message.answer(
            "⚠️ وضّح سبب تعطيل الحساب بشكل أكبر:",
            reply_markup=get_cancel_keyboard()
        )
        return

    if len(reason) > 300:
        await message.answer(
            "⚠️ النص طويل جداً، اختصره إلى أقل من 300 حرف:",
            reply_markup=get_cancel_keyboard()
        )
        return

    data = await state.get_data()

    fullname = data.get("fullname", "User")
    username = data.get("username", "username")
    email = data.get("email", "email@example.com")
    years = data.get("years", "several years")
    purpose = data.get("purpose", "connect with others")

    # حماية رموز HTML التي قد يرسلها المستخدم
    fullname = (
        fullname.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    username = (
        username.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    email = (
        email.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    years = (
        years.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    purpose = (
        purpose.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    reason = (
        reason.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    generated = (
        "🤖 <b>تم إنشاء صيغتك المخصصة بنجاح</b>\n"
        "────────────────────────\n\n"
        "Dear Instagram Support Team,\n\n"
        f"My name is {fullname}, and I am the rightful owner of the "
        f"Instagram account @{username}. I am writing this formal appeal "
        "to request the reinstatement of my account, which I believe was "
        "disabled in error.\n\n"
        f"My account has been active for approximately {years}. During this "
        f"time, it has been an important platform for me to {purpose}.\n\n"
        "I have always used Instagram responsibly and have never intentionally "
        "violated the Community Guidelines or Terms of Use.\n\n"
        f"I believe the disablement may have resulted from {reason}. "
        "I have already taken the necessary steps to secure my account.\n\n"
        "This account is very important to me. Losing access has caused "
        "significant inconvenience. I am fully prepared to provide any "
        "identity verification or additional information required.\n\n"
        "I respectfully request that your team conduct a thorough manual "
        "review of my account and reinstate it if no intentional violation "
        "is found.\n\n"
        "Thank you for your time and support.\n\n"
        "Best regards,\n"
        f"{fullname}\n"
        f"@{username}\n"
        f"{email}"
    )

    try:
        await message.answer(
            generated,
            parse_mode="HTML"
        )

        await message.answer(
            "✅ تم إنشاء الصيغة بنجاح.\n"
            "انسخها واستخدمها في أحد الروابط الرسمية من القائمة.",
            reply_markup=get_main_menu_keyboard()
        )

        await state.clear()

    except Exception as error:
        print(f"Appeal generator error: {error}")

        await message.answer(
            "❌ حدث خطأ أثناء إنشاء الصيغة، حاول مرة أخرى.",
            reply_markup=get_main_menu_keyboard()
        )

# --- قسم الإيميلات ---
@dp.callback_query(F.data == "section_emails")
async def section_emails(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📧 <b>قسم الإيميلات الرسمية لإنستقرام</b>\n\n"
        "اضغط على أي إيميل لعرضه، ثم انسخه وأرسل استئنافك إليه:",
        reply_markup=get_emails_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("email"))
async def email_handler(callback: types.CallbackQuery):
    email_map = {
        "email1": "support@instagram.com",
        "email2": "appeals@instagram.com",
        "email3": "security@mail.instagram.com",
        "email4": "feedback@instagram.com",
        "email5": "help@instagram.com",
        "email6": "appeals@meta.com"
    }
    email = email_map.get(callback.data, "غير معروف")
    await callback.message.answer(
        f"📧 <b>الإيميل:</b> <code>{email}</code>\n\n"
        "انسخه وأرسل صيغة الاستئناف إليه من بريدك المرتبط بالحساب.",
        parse_mode="HTML"
    )
    await callback.answer("تم عرض الإيميل")

# --- قسم إعادة التعيين ---
@dp.callback_query(F.data == "section_reset")
async def section_reset(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔄 <b>روابط إعادة التعيين واسترجاع الحساب</b>\n\n"
        "اختر الرابط المناسب حسب حالتك:",
        reply_markup=get_reset_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- قسم النصائح ---
@dp.callback_query(F.data == "section_tips")
async def section_tips(callback: types.CallbackQuery):
    tips_text = (
        "💡 <b>نصائح ذهبية لزيادة فرص نجاح الاستئناف</b>\n\n"
        "1️⃣ <b>استخدم بريداً مرتبطاً بالحساب</b>\n"
        "أرسل الاستئناف دائماً من البريد الإلكتروني المسجل في الحساب.\n\n"
        "2️⃣ <b>كن صادقاً ومهذباً</b>\n"
        "لا تستخدم لغة عدائية أو تهديدات. كن محترماً وواضحاً.\n\n"
        "3️⃣ <b>خصص الصيغة</b>\n"
        "لا ترسل صيغة عامة بدون تعديل. أضف بياناتك الحقيقية وسبب أهمية الحساب.\n\n"
        "4️⃣ <b>أرسل من عدة قنوات</b>\n"
        "استخدم النماذج الرسمية + الإيميلات + صفحة الدعم.\n\n"
        "5️⃣ <b>لا تكرر الإرسال بشكل مفرط</b>\n"
        "انتظر 48–72 ساعة بين المحاولات لتجنب اعتبار الطلب سباماً.\n\n"
        "6️⃣ <b>فعّل الأمان بعد الاسترجاع</b>\n"
        "غيّر كلمة المرور فوراً وفعّل التحقق بخطوتين.\n\n"
        "7️⃣ <b>احتفظ بنسخ من الرسائل</b>\n"
        "احفظ أرقام التذاكر والردود للمتابعة.\n\n"
        "8️⃣ <b>تجنب التطبيقات الخارجية</b>\n"
        "لا تعتمد على أدوات أو مواقع تدّعي الاسترجاع الفوري مقابل مال."
    )
    await callback.message.edit_text(
        tips_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- قسم الأسئلة الشائعة ---
@dp.callback_query(F.data == "section_faq")
async def section_faq(callback: types.CallbackQuery):
    faq_text = (
        "❓ <b>أسئلة شائعة حول استرجاع حسابات إنستقرام</b>\n\n"
        "<b>س1: كم يستغرق الرد على الاستئناف؟</b>\n"
        "عادة من يومين إلى أسبوعين. في بعض الحالات قد يستغرق وقتاً أطول.\n\n"
        "<b>س2: هل الصيغ الإنجليزية أفضل؟</b>\n"
        "نعم، يُفضل استخدام الإنجليزية لأنها اللغة الرسمية لفريق الدعم.\n\n"
        "<b>س3: ماذا أفعل إذا لم يصل رد؟</b>\n"
        "أعد الإرسال بعد عدة أيام باستخدام صيغة مختلفة أو رابط مختلف.\n\n"
        "<b>س4: هل يمكن استرجاع الحساب بعد الحذف النهائي؟</b>\n"
        "إذا تم حذف الحساب نهائياً من قبل إنستقرام، تكون الفرص ضعيفة جداً.\n\n"
        "<b>س5: هل البوت المدفوع يضمن الاسترجاع؟</b>\n"
        "لا يوجد ضمان مطلق من أي جهة. النجاح يعتمد على حالة الحساب وسياسات إنستقرام.\n\n"
        "<b>س6: هل أحتاج إلى صورة هوية؟</b>\n"
        "في كثير من الحالات يطلب فريق الدعم التحقق من الهوية. كن مستعداً لذلك."
    )
    await callback.message.edit_text(
        faq_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- قسم الاشتراك المدفوع ---
@dp.callback_query(F.data == "section_paid")
async def section_paid(callback: types.CallbackQuery):
    paid_text = (
        "💰 <b>الاشتراك في البوت المدفوع</b>\n\n"
        "نوفر بوتاً متقدماً لاسترجاع الحسابات (المعطلة، المبندة، والمخترقة).\n\n"
        "• نسبة نجاح مرتفعة حسب الحالات\n"
        "• متابعة مباشرة مع فريق الدعم\n"
        "• خصوصية وسرية تامة\n"
        "• السعر: 100$ شهرياً\n\n"
        "للتفاصيل والاشتراك تواصل معنا:\n"
        "@dvve1"
    )
    await callback.message.edit_text(
        paid_text,
        reply_markup=get_paid_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# ==================== خادم الصحة ====================
async def health_handler(request):
    return web.Response(text="OK", status=200)

async def run_health_server():
    port = int(os.environ.get("PORT", "8000"))
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health server running on port {port}")

# ==================== التشغيل ====================
async def main():
    logging.basicConfig(level=logging.INFO)

    print("🚀 Bot is running")

    await run_health_server()
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
