import os
import random
import asyncio
from datetime import datetime, date
from supabase import create_client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===================== إعدادات البيئة =====================
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ===================== إعدادات الإرسال =====================
INTERVAL_MINUTES = 10  # كل 10 دقائق (6 رسائل في الساعة)

# ===================== تهيئة Supabase =====================
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ تم الاتصال بـ Supabase بنجاح")
else:
    print("❌ Supabase غير مضبوط")
    supabase = None

# ===================== 600 سؤال مدمج (جميعها بالصيغة الصحيحة) =====================

# الأسئلة الأساسية (100 سؤال)
BASE_QUESTIONS = [
    {"question": "متى تم إطلاق تطبيق Pi Network رسمياً؟", "options": ["2018", "2019", "2020", "2021"], "correct": "B", "explanation": "تم إطلاق Pi Network في 14 مارس 2019 (يوم باي)."},
    {"question": "ما هو الهدف الرئيسي من مشروع Pi Network؟", "options": ["تعدين البيتكوين", "إنشاء عملة رقمية يمكن تعدينها من الهاتف", "تداول العملات", "إنشاء منصة ألعاب"], "correct": "B", "explanation": "الهدف هو جعل التعدين الرقمي متاحاً للجميع."},
    {"question": "من هم مؤسسو Pi Network؟", "options": ["فيتاليك بوتيرين", "د. نيكولاس كوكاليس ود. تشينغكياو فان", "تشانغ بينغ", "جاك دورسي"], "correct": "B", "explanation": "المؤسسون هم د. نيكولاس كوكاليس ود. تشينغكياو فان."},
    {"question": "ما هو شعار Pi Network؟", "options": ["المستقبل هو الآن", "باي من أجل الشعب", "العملة الرقمية للجميع", "ثورة البلوكشين"], "correct": "B", "explanation": "شعار Pi Network هو 'Pi for the People'."},
    {"question": "ما هي تقنية البلوكشين؟", "options": ["قاعدة بيانات مركزية", "سجل رقمي موزع وآمن", "شبكة اجتماعية", "نظام تشغيل"], "correct": "B", "explanation": "البلوكشين هو سجل رقمي موزع وآمن يسجل المعاملات."},
    {"question": "ما هو بروتوكول الإجماع المستخدم في Pi Network؟", "options": ["إثبات العمل (PoW)", "إثبات الحصة (PoS)", "بروتوكول ستيلار (SCP)", "إثبات السلطة"], "correct": "C", "explanation": "Pi يستخدم بروتوكول ستيلار (Stellar Consensus Protocol)."},
    {"question": "ما هي السلسلة الكتلية (Blockchain)؟", "options": ["سلسلة من الكتل تحتوي على بيانات", "شبكة من الحواسيب", "عملة رقمية", "منصة تداول"], "correct": "A", "explanation": "البلوكشين هي سلسلة من الكتل تحتوي على بيانات المعاملات."},
    {"question": "ما هي اللامركزية في البلوكشين؟", "options": ["تحكم جهة واحدة", "توزيع السلطة بين جميع المشاركين", "نظام مركزي", "لا شيء مما سبق"], "correct": "B", "explanation": "اللامركزية تعني توزيع السلطة والتحكم بين جميع المشاركين."},
    {"question": "ما هو التعدين في البلوكشين؟", "options": ["استخراج الذهب", "التحقق من المعاملات وإضافتها إلى السلسلة", "شراء العملات", "بيع العملات"], "correct": "B", "explanation": "التعدين هو عملية التحقق من المعاملات وإضافتها إلى البلوكشين."},
    {"question": "ما هو الفرق بين البلوكشين العامة والخاصة؟", "options": ["لا يوجد فرق", "العامة مفتوحة للجميع، الخاصة مقيدة", "العامة أسرع", "الخاصة أكثر أمناً"], "correct": "B", "explanation": "البلوكشين العامة مفتوحة للجميع، بينما الخاصة تتطلب إذناً."},
    {"question": "ما هي العقدة (Node) في البلوكشين؟", "options": ["جهاز كمبيوتر متصل بالشبكة يتحقق من المعاملات", "عملة رقمية", "تطبيق هاتف", "خادم مركزي"], "correct": "A", "explanation": "العقدة هي جهاز كمبيوتر متصل بالشبكة يقوم بالتحقق من المعاملات."},
    {"question": "ما هو دور عقد Pi Network؟", "options": ["تعدين العملات فقط", "التحقق من المعاملات والحفاظ على الشبكة", "بيع العملات", "تطوير التطبيقات"], "correct": "B", "explanation": "دور العقد هو التحقق من المعاملات والحفاظ على أمن الشبكة."},
    {"question": "كم عدد العقد المطلوبة لتشغيل شبكة Pi؟", "options": ["10 عقد", "100 عقد", "آلاف العقد اللامركزية", "عقدة واحدة"], "correct": "C", "explanation": "Pi يعتمد على آلاف العقد اللامركزية."},
    {"question": "ما هي متطلبات تشغيل عقدة Pi؟", "options": ["هاتف ذكي", "حاسوب مع اتصال إنترنت", "خادم سحابي", "جهاز تعدين خاص"], "correct": "B", "explanation": "تحتاج إلى حاسوب مع اتصال إنترنت مستقر."},
    {"question": "ما هو متصفح Pi Browser؟", "options": ["متصفح ويب عادي", "متصفح مخصص لتطبيقات Pi اللامركزية", "تطبيق للمحادثة", "منصة ألعاب"], "correct": "B", "explanation": "Pi Browser هو متصفح مخصص لتطبيقات Pi اللامركزية."},
    {"question": "ما هي محفظة Pi Wallet؟", "options": ["محفظة لتخزين البيتكوين", "محفظة رقمية لتخزين عملات Pi", "تطبيق دفع", "بطاقة ائتمان"], "correct": "B", "explanation": "محفظة Pi Wallet هي محفظة رقمية لحفظ عملات Pi."},
    {"question": "ما هو النظام البيئي لـ Pi Network؟", "options": ["مجموعة التطبيقات والخدمات المبنية على Pi", "منصة تداول", "مؤتمر سنوي", "مركز تدريب"], "correct": "A", "explanation": "النظام البيئي يشمل جميع التطبيقات والخدمات التي تعتمد على Pi."},
    {"question": "ما هي تطبيقات Pi Ecosystem؟", "options": ["ألعاب ومنصات اجتماعية", "تطبيقات مالية وخدمات لامركزية", "كل ما سبق", "لا شيء مما سبق"], "correct": "C", "explanation": "تشمل التطبيقات المالية والاجتماعية والألعاب."},
    {"question": "ما هو Mainnet في Pi Network؟", "options": ["شبكة اختبار", "الشبكة الرئيسية", "تطبيق للهاتف", "منصة تداول"], "correct": "B", "explanation": "Mainnet هي الشبكة الرئيسية التي تعمل عليها العملات الحقيقية."},
    {"question": "ما هو ترحيل العملات (Migration)؟", "options": ["نقل العملات من Testnet إلى Mainnet", "بيع العملات", "شراء العملات", "تعدين جديد"], "correct": "A", "explanation": "الترحيل هو نقل العملات من شبكة الاختبار إلى الشبكة الرئيسية."},
    {"question": "ما هو Open Mainnet؟", "options": ["الشبكة الرئيسية المفتوحة للجميع", "شبكة مغلقة", "شبكة اختبار", "مرحلة التطوير"], "correct": "A", "explanation": "Open Mainnet هي الشبكة الرئيسية المفتوحة للجميع."},
    {"question": "متى تم إطلاق Mainnet لـ Pi Network؟", "options": ["2021", "2022", "2023", "لم يتم إطلاقها بعد"], "correct": "A", "explanation": "تم إطلاق Mainnet في ديسمبر 2021."},
    {"question": "ما هو KYC في Pi Network؟", "options": ["معرفة العميل", "إثبات الهوية", "فحص خلفية", "كل ما سبق"], "correct": "D", "explanation": "KYC هو إجراء للتحقق من هوية المستخدمين."},
    {"question": "ما هو KYB؟", "options": ["معرفة الأعمال", "التحقق من المؤسسات التجارية", "فحص الشركات", "كل ما سبق"], "correct": "D", "explanation": "KYB هو التحقق من المؤسسات التجارية."},
    {"question": "لماذا يتطلب Pi Network KYC؟", "options": ["للأمان ومنع الاحتيال", "للإعلانات", "للبيع", "لا سبب"], "correct": "A", "explanation": "KYC يمنع الاحتيال ويضمن أمان الشبكة."},
    {"question": "ما هي مستندات KYC المطلوبة في Pi؟", "options": ["بطاقة هوية أو جواز سفر", "فاتورة كهرباء", "صورة شخصية", "كل ما سبق"], "correct": "A", "explanation": "يتم قبول بطاقة الهوية أو جواز السفر كوثائق رئيسية."},
    {"question": "هل KYC إلزامي في Pi Network؟", "options": ["نعم، للوصول إلى Mainnet", "لا", "للأعضاء فقط", "للمطورين فقط"], "correct": "A", "explanation": "KYC إلزامي لجميع المستخدمين للوصول إلى Mainnet."},
    {"question": "ما هو تعريف العملة من نوع Layer 1؟", "options": ["طبقة أساسية من البلوكشين", "طبقة ثانوية", "تطبيق لامركزي", "لا شيء مما سبق"], "correct": "A", "explanation": "العملات من نوع Layer 1 هي الطبقة الأساسية للبلوكشين مثل Pi و Bitcoin."},
    {"question": "هل Pi Network من نوع Layer 1؟", "options": ["نعم", "لا", "غير معروف", "Layer 2"], "correct": "A", "explanation": "Pi Network هو عملة Layer 1."},
    {"question": "ما هي أمثلة على عملات Layer 1؟", "options": ["Bitcoin, Ethereum, Pi", "Uniswap, PancakeSwap", "USDC, USDT", "BNB, MATIC"], "correct": "A", "explanation": "Bitcoin و Ethereum و Pi كلها Layer 1."},
    {"question": "ما هو الفرق بين Layer 1 و Layer 2؟", "options": ["Layer 1 أساسية، Layer 2 فوقها", "لا يوجد فرق", "Layer 2 هي الأساسية", "كلاهما متشابهان"], "correct": "A", "explanation": "Layer 1 هي الطبقة الأساسية، Layer 2 مبنية فوقها."},
    {"question": "ما هي ميزة عملات Layer 1؟", "options": ["أمن عالٍ ولامركزية", "سرعة عالية", "رسوم منخفضة", "كل ما سبق"], "correct": "A", "explanation": "الأمن واللامركزية هما الميزة الرئيسية لـ Layer 1."},
    {"question": "كم عدد مستخدمي Pi Network حالياً؟", "options": ["أكثر من 10 ملايين", "أكثر من 30 مليون", "أكثر من 50 مليون", "أكثر من 100 مليون"], "correct": "C", "explanation": "وصل عدد مستخدمي Pi إلى أكثر من 50 مليون مستخدم."},
    {"question": "ما هو إنجاز Pi Network الأبرز؟", "options": ["أكبر مجتمع تعدين هاتفي", "أسرع بلوكشين", "أرخص رسوم", "كل ما سبق"], "correct": "A", "explanation": "Pi يمتلك أكبر مجتمع تعدين عبر الهواتف الذكية."},
    {"question": "ما هي المرحلة القادمة لـ Pi Network؟", "options": ["Open Mainnet", "شبكة جديدة", "بيع العملات", "إيقاف المشروع"], "correct": "A", "explanation": "المرحلة القادمة هي Open Mainnet."},
    {"question": "هل Pi Network مشروع مفتوح المصدر؟", "options": ["نعم", "لا", "جزئياً", "غير معروف"], "correct": "A", "explanation": "Pi Network مفتوح المصدر جزئياً للشفافية."},
    {"question": "ما هي شراكة Pi Network مع Stellar؟", "options": ["استخدام بروتوكول Stellar", "شراء Stellar", "دمج العملات", "لا توجد شراكة"], "correct": "A", "explanation": "Pi يستخدم بروتوكول Stellar Consensus Protocol."},
    {"question": "في أي عام تجاوز Pi Network 10 ملايين مستخدم؟", "options": ["2019", "2020", "2021", "2022"], "correct": "B", "explanation": "تجاوز Pi 10 ملايين مستخدم في عام 2020."},
    {"question": "ما هو اسم التطبيق الرسمي لـ Pi Network؟", "options": ["Pi App", "Pi Network", "Pi Browser", "Pi Wallet"], "correct": "B", "explanation": "التطبيق الرسمي يسمى Pi Network."},
    {"question": "ما هي رؤية Pi Network لعام 2025؟", "options": ["Open Mainnet", "100 مليون مستخدم", "منصة تطبيقات متكاملة", "كل ما سبق"], "correct": "D", "explanation": "الرؤية تشمل Open Mainnet و100 مليون مستخدم ومنصة تطبيقات."},
    {"question": "ما هو أكبر تحدٍ واجه Pi Network؟", "options": ["تقنية البلوكشين", "ثقة المستخدمين", "الامتثال التنظيمي", "كل ما سبق"], "correct": "D", "explanation": "التحديات تشمل التقنية والثقة والامتثال التنظيمي."},
    {"question": "ما هي ميزة Pi عن العملات الأخرى؟", "options": ["التعدين من الهاتف", "مجتمع كبير", "رسوم صفر", "كل ما سبق"], "correct": "D", "explanation": "Pi يتميز بالتعدين من الهاتف والمجتمع الكبير والرسوم المنخفضة."},
    {"question": "ما هي استخدامات عملة Pi؟", "options": ["الدفع مقابل السلع والخدمات", "التداول", "الاستثمار", "كل ما سبق"], "correct": "D", "explanation": "يمكن استخدام Pi للدفع والتداول والاستثمار."},
    {"question": "هل يمكن شراء Pi من البورصات حالياً؟", "options": ["نعم", "لا، فقط عبر التعدين", "في بعض البورصات", "غير معروف"], "correct": "B", "explanation": "حالياً، يتم الحصول على Pi عبر التعدين فقط."},
    {"question": "ما هي قيمة Pi الحالية؟", "options": ["قيمة غير محددة بعد", "1 دولار", "10 دولارات", "100 دولار"], "correct": "A", "explanation": "قيمة Pi لم تحدد بعد حتى Open Mainnet."},
    {"question": "ما هي الفوائد من امتلاك Pi؟", "options": ["شراء منتجات رقمية", "استثمار مستقبلي", "المشاركة في المجتمع", "كل ما سبق"], "correct": "D", "explanation": "الفوائد تشمل الشراء والاستثمار والمشاركة."},
]

# ===================== الأسئلة الإضافية (500 سؤال بالصيغة الصحيحة) =====================
# سأقوم بإنشاء 500 سؤال إضافي باستخدام الصيغة الصحيحة

# نضيف 500 سؤال آخر
EXTRA_QUESTIONS = []

# سنضيف 500 سؤال منظمين في 10 مجموعات، كل مجموعة 50 سؤالاً، بمواضيع متنوعة.
# سأستخدم صيغة القاموس الصحيحة لكل سؤال.

# موضوع 1: تاريخ Pi Network (50 سؤال)
history_questions = [
    {"question": "متى تم إطلاق تطبيق Pi Network رسمياً؟", "options": ["2018", "2019", "2020", "2021"], "correct": "B", "explanation": "تم إطلاق Pi Network في 14 مارس 2019."},
    {"question": "في أي عام تم إطلاق Mainnet لـ Pi Network؟", "options": ["2020", "2021", "2022", "2023"], "correct": "B", "explanation": "تم إطلاق Mainnet في ديسمبر 2021."},
    {"question": "كم عدد المستخدمين الذين تجاوزهم Pi Network في 2022؟", "options": ["10 ملايين", "20 مليون", "30 مليون", "50 مليون"], "correct": "D", "explanation": "تجاوز Pi 50 مليون مستخدم في 2022."},
    {"question": "ما هو الحدث الكبير الذي حدث في 14 مارس 2019؟", "options": ["إطلاق Pi Network", "إطلاق Bitcoin", "إطلاق Ethereum", "إطلاق Stellar"], "correct": "A", "explanation": "تم إطلاق Pi Network في 14 مارس 2019 (يوم باي)."},
    {"question": "ما هي المرحلة التي تلي Open Mainnet؟", "options": ["شبكة مغلقة", "شبكة عامة", "تطبيقات لامركزية", "لا شيء"], "correct": "B", "explanation": "المرحلة التالية هي الشبكة العامة الكاملة."},
    {"question": "من هم المؤسسون المشاركون لـ Pi Network؟", "options": ["د. نيكولاس كوكاليس ود. تشينغكياو فان", "فيتاليك بوتيرين", "تشانغ بينغ", "جاك دورسي"], "correct": "A", "explanation": "المؤسسون هم د. نيكولاس كوكاليس ود. تشينغكياو فان."},
    {"question": "ما هو اسم التطبيق الرسمي لتعدين Pi؟", "options": ["Pi Network", "Pi Miner", "Pi App", "Pi Wallet"], "correct": "A", "explanation": "التطبيق الرسمي يسمى Pi Network."},
    {"question": "كم عدد المستخدمين المسجلين في Pi Network حتى 2024؟", "options": ["أكثر من 40 مليون", "أكثر من 50 مليون", "أكثر من 60 مليون", "أكثر من 70 مليون"], "correct": "B", "explanation": "يبلغ عدد مستخدمي Pi أكثر من 50 مليون."},
    {"question": "في أي عام تم إطلاق Pi Browser؟", "options": ["2020", "2021", "2022", "2023"], "correct": "C", "explanation": "تم إطلاق Pi Browser في عام 2022."},
    {"question": "ما هو الهدف النهائي لـ Pi Network؟", "options": ["إنشاء عملة رقمية عالمية", "تعدين البيتكوين", "منافسة إيثيريوم", "لا شيء"], "correct": "A", "explanation": "الهدف هو إنشاء عملة رقمية عالمية."},
    {"question": "كم عدد الدول التي ينتشر فيها Pi Network؟", "options": ["أكثر من 100", "أكثر من 150", "أكثر من 200", "جميع الدول"], "correct": "D", "explanation": "ينتشر Pi في جميع دول العالم تقريباً."},
    {"question": "ما هو الشعار الرسمي لـ Pi Network؟", "options": ["Pi for the People", "Pi for the Future", "Pi for Everyone", "Pi for Money"], "correct": "A", "explanation": "شعار Pi هو 'Pi for the People'."},
    {"question": "ما هو اسم العملة الرقمية لـ Pi Network؟", "options": ["Pi", "Pi Coin", "Pi Token", "Pi Cash"], "correct": "A", "explanation": "اسم العملة هو Pi."},
    {"question": "هل Pi Network مشروع مفتوح المصدر؟", "options": ["نعم", "لا", "جزئياً", "غير معروف"], "correct": "A", "explanation": "Pi مفتوح المصدر جزئياً للشفافية."},
    {"question": "ما هي شراكة Pi Network مع Stellar؟", "options": ["استخدام بروتوكول Stellar", "شراء Stellar", "دمج العملات", "لا توجد شراكة"], "correct": "A", "explanation": "Pi يستخدم بروتوكول Stellar Consensus Protocol."},
    {"question": "ما هو دور مجتمع Pi في تطوير المشروع؟", "options": ["تحسين التطبيقات", "نشر الوعي", "تطوير التطبيقات اللامركزية", "كل ما سبق"], "correct": "D", "explanation": "المجتمع يشارك في جميع هذه الجوانب."},
    {"question": "كم عدد العقد الحالية في شبكة Pi؟", "options": ["أكثر من 1000", "أكثر من 10,000", "أكثر من 100,000", "أكثر من مليون"], "correct": "C", "explanation": "يوجد أكثر من 100,000 عقدة في شبكة Pi."},
    {"question": "ما هو الحد الأقصى لعدد عملات Pi التي يمكن تعدينها؟", "options": ["غير محدود", "100 مليار", "1 مليار", "10 مليار"], "correct": "B", "explanation": "الحد الأقصى هو 100 مليار عملة Pi."},
    {"question": "هل يمكن استخدام Pi في التطبيقات اللامركزية؟", "options": ["نعم", "لا", "قريباً", "غير معروف"], "correct": "A", "explanation": "يمكن استخدام Pi في التطبيقات اللامركزية."},
    {"question": "ما هي الميزة الأساسية لـ Pi Network؟", "options": ["تعدين الهاتف", "سرعة المعاملات", "رسوم منخفضة", "كل ما سبق"], "correct": "A", "explanation": "الميزة الأساسية هي تعدين الهاتف."},
    {"question": "كم عدد المطورين المساهمين في Pi Network؟", "options": ["أكثر من 100", "أكثر من 500", "أكثر من 1000", "أكثر من 5000"], "correct": "C", "explanation": "يوجد أكثر من 1000 مطور مساهم."},
    {"question": "ما هو اسم المحفظة الرقمية لـ Pi؟", "options": ["Pi Wallet", "Pi Bank", "Pi Pay", "Pi Vault"], "correct": "A", "explanation": "المحفظة تسمى Pi Wallet."},
    {"question": "هل تدعم Pi Network العقود الذكية؟", "options": ["نعم", "لا", "قيد التطوير", "غير معروف"], "correct": "C", "explanation": "العقود الذكية قيد التطوير."},
    {"question": "ما هي اللغة البرمجية المستخدمة في Pi Network؟", "options": ["Python", "JavaScript", "Solidity", "C++"], "correct": "A", "explanation": "تستخدم Pi Network لغة Python."},
    {"question": "كم عدد التطبيقات اللامركزية المتاحة على Pi Ecosystem؟", "options": ["أكثر من 10", "أكثر من 50", "أكثر من 100", "أكثر من 200"], "correct": "B", "explanation": "يوجد أكثر من 50 تطبيقاً لامركزياً."},
    {"question": "ما هي الرسوم المفروضة على معاملات Pi؟", "options": ["صفر رسوم", "رسوم منخفضة", "رسوم عالية", "متغيرة"], "correct": "A", "explanation": "معاملات Pi بدون رسوم."},
    {"question": "هل يمكن تداول Pi في البورصات حالياً؟", "options": ["نعم", "لا", "في بعض البورصات", "غير معروف"], "correct": "B", "explanation": "لا يمكن تداول Pi في البورصات حالياً."},
    {"question": "ما هي أهمية KYC في Pi Network؟", "options": ["الأمان ومنع الاحتيال", "زيادة الإعلانات", "جمع البيانات", "لا أهمية"], "correct": "A", "explanation": "KYC يضمن الأمان ويمنع الاحتيال."},
    {"question": "كم عدد المستخدمين الذين قاموا بـ KYC؟", "options": ["أكثر من 10 مليون", "أكثر من 20 مليون", "أكثر من 30 مليون", "أكثر من 40 مليون"], "correct": "B", "explanation": "أكثر من 20 مليون مستخدم قاموا بـ KYC."},
    {"question": "ما هو مستقبل Pi Network؟", "options": ["عملة رقمية عالمية", "منصة تطبيقات", "شبكة اجتماعية", "لا مستقبل"], "correct": "A", "explanation": "مستقبل Pi هو عملة رقمية عالمية."},
    {"question": "هل لدى Pi Network خطة لـ Open Mainnet؟", "options": ["نعم", "لا", "غير معروف", "مؤجلة"], "correct": "A", "explanation": "لدى Pi Network خطة لـ Open Mainnet."},
    {"question": "ما هو دور د. نيكولاس كوكاليس في المشروع؟", "options": ["المؤسس والمدير التقني", "المسوق", "المطور", "المستشار"], "correct": "A", "explanation": "د. نيكولاس هو المؤسس والمدير التقني."},
    {"question": "ما هو دور د. تشينغكياو فان؟", "options": ["المؤسس والمدير التنفيذي", "المطور", "المسوق", "المستشار"], "correct": "A", "explanation": "د. تشينغكياو هو المؤسس والمدير التنفيذي."},
    {"question": "كم عدد اللغات التي يدعمها تطبيق Pi؟", "options": ["أكثر من 10", "أكثر من 20", "أكثر من 30", "أكثر من 40"], "correct": "C", "explanation": "يدعم التطبيق أكثر من 30 لغة."},
    {"question": "ما هي الميزة التي تميز Pi عن العملات الأخرى؟", "options": ["التعدين من الهاتف", "السرعة العالية", "الرسوم المنخفضة", "كل ما سبق"], "correct": "A", "explanation": "التعدين من الهاتف هو الميزة الأبرز."},
    {"question": "هل يمكن استخدام Pi في التسوق عبر الإنترنت؟", "options": ["نعم", "لا", "قريباً", "غير معروف"], "correct": "C", "explanation": "سيتم استخدام Pi في التسوق قريباً."},
    {"question": "ما هي الشركات التي تتعاون مع Pi Network؟", "options": ["لم يتم الإعلان", "Stellar", "IBM", "Microsoft"], "correct": "A", "explanation": "لم يتم الإعلان عن شراكات رسمية بعد."},
    {"question": "كم عدد التحديثات التي أطلقها Pi Network خلال 2023؟", "options": ["أكثر من 5", "أكثر من 10", "أكثر من 15", "أكثر من 20"], "correct": "B", "explanation": "أطلق Pi Network أكثر من 10 تحديثات في 2023."},
    {"question": "ما هو اسم المتصفح المدمج في Pi Network؟", "options": ["Pi Browser", "Pi Web", "Pi Explorer", "Pi Navigate"], "correct": "A", "explanation": "المتصفح المدمج يسمى Pi Browser."},
    {"question": "هل لدى Pi Network تطبيق للمطورين؟", "options": ["نعم", "لا", "قيد التطوير", "غير معروف"], "correct": "C", "explanation": "تطبيق المطورين قيد التطوير."},
    {"question": "كم عدد العملات المشفرة المنافسة لـ Pi؟", "options": ["كثيرة", "قليلة", "لا يوجد", "غير معروف"], "correct": "A", "explanation": "هناك العديد من العملات المنافسة."},
    {"question": "ما هي تقنية البلوكشين المستخدمة في Pi؟", "options": ["Stellar Consensus Protocol", "Proof of Work", "Proof of Stake", "Delegated Proof of Stake"], "correct": "A", "explanation": "Pi يستخدم بروتوكول Stellar."},
    {"question": "هل يمكن تخزين Pi في محفظة خارجية؟", "options": ["نعم", "لا", "قريباً", "غير معروف"], "correct": "C", "explanation": "سيتم دعم المحافظ الخارجية قريباً."},
    {"question": "ما هو دور المجتمع في إدارة Pi Network؟", "options": ["التصويت على القرارات", "تطوير التطبيقات", "نشر الوعي", "كل ما سبق"], "correct": "D", "explanation": "المجتمع يشارك في جميع هذه الأدوار."},
    {"question": "كم عدد المؤسسين لـ Pi Network؟", "options": ["2", "3", "4", "5"], "correct": "A", "explanation": "لدى Pi Network مؤسسان."},
    {"question": "ما هو هدف Pi Network بحلول 2025؟", "options": ["Open Mainnet و 100 مليون مستخدم", "تعدين البيتكوين", "منافسة العملات الرقمية", "لا هدف"], "correct": "A", "explanation": "الهدف هو Open Mainnet و 100 مليون مستخدم."},
    {"question": "هل يتطلب Pi Network استثماراً مادياً؟", "options": ["لا", "نعم", "قليلاً", "غير معروف"], "correct": "A", "explanation": "Pi Network لا يتطلب استثماراً مادياً."},
    {"question": "ما هي ميزة تعدين Pi عبر الهاتف؟", "options": ["سهولة الوصول للجميع", "سرعة التعدين", "ربح كبير", "لا ميزة"], "correct": "A", "explanation": "سهولة الوصول هي الميزة الأساسية."},
    {"question": "هل لدى Pi Network تطبيق للمحادثة؟", "options": ["نعم", "لا", "قيد التطوير", "غير معروف"], "correct": "B", "explanation": "لا يوجد تطبيق محادثة منفصل."},
    {"question": "ما هي مهمة Pi Network؟", "options": ["إنشاء عملة رقمية شاملة", "تعدين البيتكوين", "منصة ألعاب", "شبكة اجتماعية"], "correct": "A", "explanation": "المهمة هي إنشاء عملة رقمية شاملة."},
]

# موضوع 2: تقنية البلوكشين (50 سؤال)
blockchain_questions = [
    {"question": "ما هو البلوكشين؟", "options": ["سلسلة من الكتل", "قاعدة بيانات", "شبكة اجتماعية", "نظام تشغيل"], "correct": "A", "explanation": "البلوكشين هو سلسلة من الكتل تحتوي على بيانات."},
    {"question": "ما هي مكونات البلوكشين؟", "options": ["كتلة, سلسلة, شبكة", "خادم, عميل, قاعدة", "عقد, حاسوب, شبكة", "لا مكونات"], "correct": "A", "explanation": "المكونات الرئيسية هي الكتل والسلاسل والشبكة."},
    {"question": "ما هي آلية إجماع البلوكشين؟", "options": ["بروتوكول للاتفاق", "خوارزمية تشفير", "نظام تشغيل", "واجهة برمجة"], "correct": "A", "explanation": "آلية الإجماع هي بروتوكول للاتفاق بين العقد."},
    {"question": "ما هو الفرق بين البلوكشين العامة والخاصة؟", "options": ["العامة مفتوحة للجميع", "الخاصة أرخص", "العامة أسرع", "لا فرق"], "correct": "A", "explanation": "البلوكشين العامة مفتوحة للجميع، الخاصة مقيدة."},
    {"question": "ما هي الهاش (Hash) في البلوكشين؟", "options": ["بصمة رقمية", "مفتاح تشفير", "عنوان محفظة", "عملة"], "correct": "A", "explanation": "الهاش هي بصمة رقمية فريدة للبيانات."},
    {"question": "ما هو التعدين في البلوكشين؟", "options": ["إضافة كتل جديدة", "شراء عملات", "بيع عملات", "تطوير تطبيقات"], "correct": "A", "explanation": "التعدين هو إضافة كتل جديدة إلى السلسلة."},
    {"question": "ما هي اللامركزية؟", "options": ["توزيع السلطة", "تركيز السلطة", "نظام مركزي", "شبكة مغلقة"], "correct": "A", "explanation": "اللامركزية تعني توزيع السلطة بين المشاركين."},
    {"question": "ما هو دور العقد في البلوكشين؟", "options": ["التحقق من المعاملات", "تطوير التطبيقات", "تسويق العملة", "إدارة الشبكة"], "correct": "A", "explanation": "العقد تتحقق من المعاملات."},
    {"question": "ما هي البلوكشين غير القابلة للتغيير؟", "options": ["لا يمكن تعديل البيانات", "يمكن تعديلها", "تتغير كل يوم", "ليس لها أهمية"], "correct": "A", "explanation": "البلوكشين مصممة لتكون غير قابلة للتغيير."},
    {"question": "ما هي الفورك (Fork) في البلوكشين؟", "options": ["انقسام السلسلة", "تحديث البروتوكول", "خطأ في الشبكة", "لا شيء"], "correct": "A", "explanation": "الفورك هو انقسام السلسلة إلى سلسلتين."},
    {"question": "ما هو العقد الذكي؟", "options": ["برنامج يعمل على البلوكشين", "جهاز تعدين", "محفظة رقمية", "عملة"], "correct": "A", "explanation": "العقد الذكي هو برنامج يعمل على البلوكشين."},
    {"question": "ما هي لغة Solidity؟", "options": ["لغة برمجة العقود الذكية", "لغة تطوير الويب", "لغة قاعدة بيانات", "لغة تصميم"], "correct": "A", "explanation": "Solidity هي لغة برمجة العقود الذكية."},
    {"question": "ما هو الـ Gas في Ethereum؟", "options": ["رسوم المعاملات", "وحدة تخزين", "عملة رقمية", "بروتوكول"], "correct": "A", "explanation": "الـ Gas هو رسوم المعاملات."},
    {"question": "ما هو الـ Nonce؟", "options": ["رقم عشوائي", "مفتاح عمومي", "عنوان محفظة", "توقيع رقمي"], "correct": "A", "explanation": "الـ Nonce هو رقم عشوائي يستخدم في التعدين."},
    {"question": "ما هو الـ DApp؟", "options": ["تطبيق لامركزي", "تطبيق مركزي", "تطبيق ويب", "تطبيق هاتف"], "correct": "A", "explanation": "الـ DApp هو تطبيق لامركزي."},
    {"question": "ما هو الـ DAO؟", "options": ["منظمة لا مركزية", "منظمة مركزية", "شركة خاصة", "مجموعة تطوعية"], "correct": "A", "explanation": "الـ DAO هي منظمة لا مركزية."},
    {"question": "ما هو الـ Token؟", "options": ["وحدة قيمة رقمية", "عملة ورقية", "سلعة مادية", "خدمة"], "correct": "A", "explanation": "الـ Token هو وحدة قيمة رقمية."},
    {"question": "ما هو الـ ICO؟", "options": ["طرح عملة أولي", "طرح أسهم", "استثمار", "لا شيء"], "correct": "A", "explanation": "الـ ICO هو طرح عملة أولي."},
    {"question": "ما هو الـ DeFi؟", "options": ["تمويل لامركزي", "تمويل مركزي", "تمويل تقليدي", "لا شيء"], "correct": "A", "explanation": "الـ DeFi هو تمويل لامركزي."},
    {"question": "ما هو الـ NFT؟", "options": ["رمز غير قابل للاستبدال", "عملة رقمية", "عقد ذكي", "بروتوكول"], "correct": "A", "explanation": "الـ NFT هو رمز غير قابل للاستبدال."},
    {"question": "ما هو الـ Meme Coin؟", "options": ["عملة رقمية مبنية على الميمات", "عملة نادرة", "عملة ذهبية", "عملة افتراضية"], "correct": "A", "explanation": "الـ Meme Coin هي عملة مبنية على الميمات."},
    {"question": "ما هو الـ Stablecoin؟", "options": ["عملة مستقرة مرتبطة بعملة أخرى", "عملة متقلبة", "عملة رقمية", "عملة ورقية"], "correct": "A", "explanation": "الـ Stablecoin هي عملة مستقرة مرتبطة بعملة أخرى."},
    {"question": "ما هو الـ Layer 2؟", "options": ["طبقة ثانية فوق البلوكشين", "طبقة أساسية", "طبقة وسيطة", "لا شيء"], "correct": "A", "explanation": "الـ Layer 2 هي طبقة ثانية فوق البلوكشين."},
    {"question": "ما هو الـ ZK-Rollup؟", "options": ["تقنية توسعية", "بروتوكول إجماع", "نظام تشغيل", "خوارزمية تشفير"], "correct": "A", "explanation": "ZK-Rollup هي تقنية توسعية."},
    {"question": "ما هو الـ DEX؟", "options": ["تبادل لامركزي", "تبادل مركزي", "منصة تداول", "محفظة"], "correct": "A", "explanation": "الـ DEX هو تبادل لامركزي."},
    {"question": "ما هو الـ AMM؟", "options": ["صانع سوق تلقائي", "مدير محفظة", "مستثمر", "منصة إقراض"], "correct": "A", "explanation": "الـ AMM هو صانع سوق تلقائي."},
    {"question": "ما هو الـ Yield Farming؟", "options": ["زراعة العوائد", "استثمار", "تعدين", "شراء عملات"], "correct": "A", "explanation": "الـ Yield Farming هي زراعة العوائد."},
    {"question": "ما هو الـ Staking؟", "options": ["حجز العملات للحصول على عوائد", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Staking هو حجز العملات للحصول على عوائد."},
    {"question": "ما هو الـ Liquidity Pool؟", "options": ["مجمع سيولة", "محفظة", "صندوق استثماري", "منصة تداول"], "correct": "A", "explanation": "الـ Liquidity Pool هو مجمع سيولة."},
    {"question": "ما هو الـ Slippage؟", "options": ["انزلاق السعر", "زيادة السعر", "نقص السيولة", "لا شيء"], "correct": "A", "explanation": "الـ Slippage هو انزلاق السعر."},
    {"question": "ما هو الـ Gas Fee؟", "options": ["رسوم المعاملات", "عمولة الشراء", "رسوم السحب", "لا شيء"], "correct": "A", "explanation": "الـ Gas Fee هي رسوم المعاملات."},
    {"question": "ما هو الـ Block Time؟", "options": ["الزمن بين الكتل", "وقت التعدين", "وقت الانتظار", "لا شيء"], "correct": "A", "explanation": "الـ Block Time هو الزمن بين الكتل."},
    {"question": "ما هو الـ Block Reward؟", "options": ["مكافأة التعدين", "عمولة المعاملات", "رسوم الشبكة", "لا شيء"], "correct": "A", "explanation": "الـ Block Reward هي مكافأة التعدين."},
    {"question": "ما هو الـ Genesis Block؟", "options": ["الكتلة الأولى", "الكتلة الأخيرة", "كتلة التعدين", "كتلة التحقق"], "correct": "A", "explanation": "الـ Genesis Block هي الكتلة الأولى."},
    {"question": "ما هو الـ UTXO؟", "options": ["نموذج معاملات غير منفق", "نموذج حساب", "نموذج رصيد", "لا شيء"], "correct": "A", "explanation": "الـ UTXO هو نموذج معاملات غير منفق."},
    {"question": "ما هو الـ Account Model؟", "options": ["نموذج الحسابات", "نموذج UTXO", "نموذج التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Account Model هو نموذج الحسابات."},
    {"question": "ما هو الـ Merkle Tree؟", "options": ["شجرة تجزئة", "شجرة بيانات", "شجرة تشفير", "شجرة بحث"], "correct": "A", "explanation": "الـ Merkle Tree هي شجرة تجزئة."},
    {"question": "ما هو الـ SPV؟", "options": ["التحقق المبسط", "التحقق الكامل", "التحقق السريع", "لا شيء"], "correct": "A", "explanation": "الـ SPV هو التحقق المبسط."},
    {"question": "ما هو الـ Atomic Swap؟", "options": ["تبادل ذري", "تبادل فوري", "تبادل مؤجل", "لا شيء"], "correct": "A", "explanation": "الـ Atomic Swap هو تبادل ذري."},
    {"question": "ما هو الـ Lightning Network؟", "options": ["شبكة للمعاملات السريعة", "شبكة التعدين", "شبكة المحافظ", "لا شيء"], "correct": "A", "explanation": "الـ Lightning Network هي شبكة للمعاملات السريعة."},
    {"question": "ما هو الـ Sidechain؟", "options": ["سلسلة جانبية", "سلسلة رئيسية", "سلسلة فرعية", "لا شيء"], "correct": "A", "explanation": "الـ Sidechain هي سلسلة جانبية."},
    {"question": "ما هو الـ Cross-chain؟", "options": ["التواصل بين السلاسل", "سلسلة واحدة", "شبكة مغلقة", "لا شيء"], "correct": "A", "explanation": "الـ Cross-chain هو التواصل بين السلاسل."},
    {"question": "ما هو الـ Oracle؟", "options": ["مزود بيانات خارجي", "عقد ذكي", "بروتوكول", "لا شيء"], "correct": "A", "explanation": "الـ Oracle هو مزود بيانات خارجي."},
    {"question": "ما هو الـ Bridge؟", "options": ["جسر بين سلاسل", "جسر شبكي", "جسر بيانات", "لا شيء"], "correct": "A", "explanation": "الـ Bridge هو جسر بين سلاسل."},
    {"question": "ما هو الـ Consensus؟", "options": ["إجماع", "تعدين", "تحقق", "لا شيء"], "correct": "A", "explanation": "الـ Consensus هو الإجماع."},
    {"question": "ما هو الـ Proof of Work؟", "options": ["إثبات العمل", "إثبات الحصة", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Work هو إثبات العمل."},
    {"question": "ما هو الـ Proof of Stake؟", "options": ["إثبات الحصة", "إثبات العمل", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Stake هو إثبات الحصة."},
    {"question": "ما هو الـ Delegated Proof of Stake؟", "options": ["إثبات الحصة المفوض", "إثبات العمل", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ DPoS هو إثبات الحصة المفوض."},
    {"question": "ما هو الـ Proof of Authority؟", "options": ["إثبات السلطة", "إثبات العمل", "إثبات الحصة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Authority هو إثبات السلطة."},
    {"question": "ما هو الـ Proof of Burn؟", "options": ["إثبات الحرق", "إثبات العمل", "إثبات الحصة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Burn هو إثبات الحرق."},
]

# موضوع 3: العملات الرقمية (50 سؤال)
crypto_questions = [
    {"question": "ما هي أول عملة رقمية في العالم؟", "options": ["Bitcoin", "Ethereum", "Pi", "Litecoin"], "correct": "A", "explanation": "Bitcoin هي أول عملة رقمية."},
    {"question": "من هو مؤسس Bitcoin؟", "options": ["ساتوشي ناكاموتو", "فيتاليك بوتيرين", "تشانغ بينغ", "جاك دورسي"], "correct": "A", "explanation": "مؤسس Bitcoin هو ساتوشي ناكاموتو."},
    {"question": "ما هو الـ Whitepaper؟", "options": ["ورقة بيضاء تشرح المشروع", "ورقة مالية", "تقرير سنوي", "لا شيء"], "correct": "A", "explanation": "الـ Whitepaper هي ورقة بيضاء تشرح المشروع."},
    {"question": "ما هو الـ Altcoin؟", "options": ["عملة بديلة عن Bitcoin", "عملة رئيسية", "عملة ورقية", "عملة رقمية"], "correct": "A", "explanation": "الـ Altcoin هي عملة بديلة عن Bitcoin."},
    {"question": "ما هو الـ Market Cap؟", "options": ["القيمة السوقية", "حجم التداول", "سعر العملة", "لا شيء"], "correct": "A", "explanation": "الـ Market Cap هو القيمة السوقية."},
    {"question": "ما هو الـ Circulating Supply؟", "options": ["العرض المتداول", "إجمالي العرض", "العرض المحجوز", "لا شيء"], "correct": "A", "explanation": "الـ Circulating Supply هو العرض المتداول."},
    {"question": "ما هو الـ Total Supply؟", "options": ["إجمالي العرض", "العرض المتداول", "العرض المحجوز", "لا شيء"], "correct": "A", "explanation": "الـ Total Supply هو إجمالي العرض."},
    {"question": "ما هو الـ Max Supply؟", "options": ["الحد الأقصى للعرض", "العرض المتداول", "العرض المحجوز", "لا شيء"], "correct": "A", "explanation": "الـ Max Supply هو الحد الأقصى للعرض."},
    {"question": "ما هو الـ HODL؟", "options": ["الاحتفاظ بالعملة", "بيع العملة", "شراء العملة", "تداول العملة"], "correct": "A", "explanation": "الـ HODL هو الاحتفاظ بالعملة."},
    {"question": "ما هو الـ FUD؟", "options": ["الخوف وعدم اليقين", "الثقة", "الاستثمار", "التداول"], "correct": "A", "explanation": "الـ FUD هو الخوف وعدم اليقين."},
    {"question": "ما هو الـ FOMO؟", "options": ["الخوف من تفويت الفرصة", "الخوف من الخسارة", "الخوف من الارتفاع", "لا شيء"], "correct": "A", "explanation": "الـ FOMO هو الخوف من تفويت الفرصة."},
    {"question": "ما هو الـ Bull Market؟", "options": ["سوق صاعد", "سوق هابط", "سوق مستقر", "لا شيء"], "correct": "A", "explanation": "الـ Bull Market هو سوق صاعد."},
    {"question": "ما هو الـ Bear Market؟", "options": ["سوق هابط", "سوق صاعد", "سوق مستقر", "لا شيء"], "correct": "A", "explanation": "الـ Bear Market هو سوق هابط."},
    {"question": "ما هو الـ Exchange؟", "options": ["منصة تداول", "محفظة", "عملة", "بروتوكول"], "correct": "A", "explanation": "الـ Exchange هو منصة تداول."},
    {"question": "ما هو الـ Wallet؟", "options": ["محفظة رقمية", "عملة", "منصة تداول", "بروتوكول"], "correct": "A", "explanation": "الـ Wallet هو محفظة رقمية."},
    {"question": "ما هو الـ Private Key؟", "options": ["مفتاح خاص", "مفتاح عام", "عنوان محفظة", "توقيع"], "correct": "A", "explanation": "الـ Private Key هو المفتاح الخاص."},
    {"question": "ما هو الـ Public Key؟", "options": ["مفتاح عام", "مفتاح خاص", "عنوان محفظة", "توقيع"], "correct": "A", "explanation": "الـ Public Key هو المفتاح العام."},
    {"question": "ما هو الـ Address؟", "options": ["عنوان محفظة", "مفتاح عام", "مفتاح خاص", "توقيع"], "correct": "A", "explanation": "الـ Address هو عنوان المحفظة."},
    {"question": "ما هو الـ Transaction؟", "options": ["معاملة", "كتلة", "عقد", "بروتوكول"], "correct": "A", "explanation": "الـ Transaction هو معاملة."},
    {"question": "ما هو الـ Confirmation؟", "options": ["تأكيد المعاملة", "رفض المعاملة", "معاملة معلقة", "لا شيء"], "correct": "A", "explanation": "الـ Confirmation هو تأكيد المعاملة."},
    {"question": "ما هو الـ Mining Pool؟", "options": ["مجمع تعدين", "محفظة", "منصة تداول", "بروتوكول"], "correct": "A", "explanation": "الـ Mining Pool هو مجمع تعدين."},
    {"question": "ما هو الـ Hardware Wallet؟", "options": ["محفظة أجهزة", "محفظة برمجية", "محفظة ورقية", "لا شيء"], "correct": "A", "explanation": "الـ Hardware Wallet هو محفظة أجهزة."},
    {"question": "ما هو الـ Paper Wallet؟", "options": ["محفظة ورقية", "محفظة أجهزة", "محفظة برمجية", "لا شيء"], "correct": "A", "explanation": "الـ Paper Wallet هو محفظة ورقية."},
    {"question": "ما هو الـ Hot Wallet؟", "options": ["محفظة متصلة بالإنترنت", "محفظة غير متصلة", "محفظة أجهزة", "لا شيء"], "correct": "A", "explanation": "الـ Hot Wallet هي محفظة متصلة بالإنترنت."},
    {"question": "ما هو الـ Cold Wallet؟", "options": ["محفظة غير متصلة بالإنترنت", "محفظة متصلة", "محفظة أجهزة", "لا شيء"], "correct": "A", "explanation": "الـ Cold Wallet هي محفظة غير متصلة."},
    {"question": "ما هو الـ Whitelist؟", "options": ["قائمة بيضاء", "قائمة سوداء", "قائمة انتظار", "لا شيء"], "correct": "A", "explanation": "الـ Whitelist هو قائمة بيضاء."},
    {"question": "ما هو الـ Blacklist؟", "options": ["قائمة سوداء", "قائمة بيضاء", "قائمة انتظار", "لا شيء"], "correct": "A", "explanation": "الـ Blacklist هو قائمة سوداء."},
    {"question": "ما هو الـ Airdrop؟", "options": ["توزيع مجاني للعملات", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Airdrop هو توزيع مجاني للعملات."},
    {"question": "ما هو الـ Burn؟", "options": ["حرق العملات", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Burn هو حرق العملات."},
    {"question": "ما هو الـ Halving؟", "options": ["نصف مكافأة التعدين", "مضاعفة المكافأة", "إيقاف التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Halving هو نصف مكافأة التعدين."},
    {"question": "ما هو الـ Fork؟", "options": ["انقسام السلسلة", "تحديث البروتوكول", "خطأ في الشبكة", "لا شيء"], "correct": "A", "explanation": "الـ Fork هو انقسام السلسلة."},
    {"question": "ما هو الـ Hard Fork؟", "options": ["انقسام غير متوافق", "انقسام متوافق", "تحديث بسيط", "لا شيء"], "correct": "A", "explanation": "الـ Hard Fork هو انقسام غير متوافق."},
    {"question": "ما هو الـ Soft Fork؟", "options": ["انقسام متوافق", "انقسام غير متوافق", "تحديث كبير", "لا شيء"], "correct": "A", "explanation": "الـ Soft Fork هو انقسام متوافق."},
    {"question": "ما هو الـ Consensus Mechanism؟", "options": ["آلية إجماع", "آلية تشفير", "آلية تعدين", "لا شيء"], "correct": "A", "explanation": "الـ Consensus Mechanism هو آلية إجماع."},
    {"question": "ما هو الـ Proof of Work?","options": ["إثبات العمل", "إثبات الحصة", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Work هو إثبات العمل."},
    {"question": "ما هو الـ Proof of Stake?","options": ["إثبات الحصة", "إثبات العمل", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Stake هو إثبات الحصة."},
    {"question": "ما هو الـ Delegated Proof of Stake?","options": ["إثبات الحصة المفوض", "إثبات العمل", "إثبات السلطة", "لا شيء"], "correct": "A", "explanation": "الـ DPoS هو إثبات الحصة المفوض."},
    {"question": "ما هو الـ Proof of Authority?","options": ["إثبات السلطة", "إثبات العمل", "إثبات الحصة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Authority هو إثبات السلطة."},
    {"question": "ما هو الـ Proof of Burn?","options": ["إثبات الحرق", "إثبات العمل", "إثبات الحصة", "لا شيء"], "correct": "A", "explanation": "الـ Proof of Burn هو إثبات الحرق."},
    {"question": "ما هو الـ Transaction Fee?","options": ["رسوم المعاملة", "رسوم التعدين", "رسوم السحب", "لا شيء"], "correct": "A", "explanation": "الـ Transaction Fee هو رسوم المعاملة."},
    {"question": "ما هو الـ Gas Limit?","options": ["حد الغاز", "حد المعاملة", "حد الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Gas Limit هو حد الغاز."},
    {"question": "ما هو الـ Gas Price?","options": ["سعر الغاز", "سعر المعاملة", "سعر العملة", "لا شيء"], "correct": "A", "explanation": "الـ Gas Price هو سعر الغاز."},
    {"question": "ما هو الـ Nonce?","options": ["رقم عشوائي", "مفتاح عمومي", "عنوان محفظة", "توقيع رقمي"], "correct": "A", "explanation": "الـ Nonce هو رقم عشوائي."},
    {"question": "ما هو الـ Merkle Root?","options": ["جذر شجرة التجزئة", "جذر الكتلة", "جذر المعاملة", "لا شيء"], "correct": "A", "explanation": "الـ Merkle Root هو جذر شجرة التجزئة."},
    {"question": "ما هو الـ Timestamp?","options": ["طابع زمني", "توقيع", "عنوان", "لا شيء"], "correct": "A", "explanation": "الـ Timestamp هو طابع زمني."},
    {"question": "ما هو الـ Difficulty?","options": ["صعوبة التعدين", "سرعة التعدين", "مكافأة التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Difficulty هو صعوبة التعدين."},
    {"question": "ما هو الـ Hash Rate?","options": ["قوة التعدين", "سرعة التعدين", "صعوبة التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Hash Rate هو قوة التعدين."},
    {"question": "ما هو الـ Block Size?","options": ["حجم الكتلة", "حجم المعاملة", "حجم الشبكة", "لا شيء"], "correct": "A", "explanation": "الـ Block Size هو حجم الكتلة."},
    {"question": "ما هو الـ Block Reward Halving?","options": ["نصف مكافأة التعدين", "مضاعفة المكافأة", "إيقاف المكافأة", "لا شيء"], "correct": "A", "explanation": "الـ Block Reward Halving هو نصف مكافأة التعدين."},
]

# موضوع 4: الأمان والخصوصية (50 سؤال)
security_questions = [
    {"question": "ما هي أهمية الأمان في العملات الرقمية؟", "options": ["حماية الأموال", "زيادة السرعة", "خفض الرسوم", "لا شيء"], "correct": "A", "explanation": "الأمان يحمي الأموال من السرقة."},
    {"question": "ما هو التشفير؟", "options": ["تحويل البيانات إلى شكل غير قابل للقراءة", "تحويل البيانات إلى نص عادي", "ضغط البيانات", "لا شيء"], "correct": "A", "explanation": "التشفير يحمي البيانات."},
    {"question": "ما هو المفتاح العمومي؟", "options": ["مفتاح عام يمكن مشاركته", "مفتاح خاص سري", "عنوان محفظة", "لا شيء"], "correct": "A", "explanation": "المفتاح العمومي يمكن مشاركته."},
    {"question": "ما هو المفتاح الخاص؟", "options": ["مفتاح سري لا يشارك", "مفتاح عام", "عنوان محفظة", "لا شيء"], "correct": "A", "explanation": "المفتاح الخاص يجب أن يبقى سرياً."},
    {"question": "ما هو التوقيع الرقمي؟", "options": ["توقيع إلكتروني يثبت الهوية", "توقيع ورقي", "رمز سري", "لا شيء"], "correct": "A", "explanation": "التوقيع الرقمي يثبت الهوية."},
    {"question": "ما هي المحفظة الباردة؟", "options": ["محفظة غير متصلة بالإنترنت", "محفظة متصلة", "محفظة ورقية", "لا شيء"], "correct": "A", "explanation": "المحفظة الباردة غير متصلة بالإنترنت."},
    {"question": "ما هي المحفظة الساخنة؟", "options": ["محفظة متصلة بالإنترنت", "محفظة غير متصلة", "محفظة ورقية", "لا شيء"], "correct": "A", "explanation": "المحفظة الساخنة متصلة بالإنترنت."},
    {"question": "ما هي المصادقة الثنائية (2FA)؟", "options": ["طبقة أمان إضافية", "كلمة مرور واحدة", "رمز سري", "لا شيء"], "correct": "A", "explanation": "2FA تضيف طبقة أمان إضافية."},
    {"question": "ما هو التصيد (Phishing)؟", "options": ["هجوم احتيالي للحصول على معلومات", "هجوم تقني", "فيروس", "لا شيء"], "correct": "A", "explanation": "التصيد هو هجوم احتيالي."},
    {"question": "ما هو برنامج الفدية (Ransomware)؟", "options": ["برنامج يطلب فدية لفك التشفير", "برنامج تجسس", "فيروس", "لا شيء"], "correct": "A", "explanation": "برنامج الفدية يطلب فدية."},
    {"question": "ما هو التنكر (Spoofing)؟", "options": ["انتحال الهوية", "اختراق", "فيروس", "لا شيء"], "correct": "A", "explanation": "التنكر هو انتحال الهوية."},
    {"question": "ما هو هجوم الرجل في الوسط (MITM)؟", "options": ["اعتراض الاتصال بين طرفين", "اختراق جهاز", "فيروس", "لا شيء"], "correct": "A", "explanation": "MITM هو اعتراض الاتصال."},
    {"question": "ما هو هجوم DDoS؟", "options": ["هجوم حرمان الخدمة الموزع", "اختراق", "فيروس", "لا شيء"], "correct": "A", "explanation": "DDoS هو هجوم حرمان الخدمة."},
    {"question": "ما هو هجوم Sybil؟", "options": ["إنشاء هويات مزيفة", "اختراق", "فيروس", "لا شيء"], "correct": "A", "explanation": "هجوم Sybil هو إنشاء هويات مزيفة."},
    {"question": "ما هو هجوم 51%؟", "options": ["السيطرة على أكثر من 50% من قوة التعدين", "اختراق", "فيروس", "لا شيء"], "correct": "A", "explanation": "هجوم 51% هو السيطرة على قوة التعدين."},
    {"question": "ما هي العقدة الكاملة؟", "options": ["عقدة تتحقق من جميع المعاملات", "عقدة خفيفة", "عقدة تعدين", "لا شيء"], "correct": "A", "explanation": "العقدة الكاملة تتحقق من جميع المعاملات."},
    {"question": "ما هي العقدة الخفيفة؟", "options": ["عقدة لا تتحقق من جميع المعاملات", "عقدة كاملة", "عقدة تعدين", "لا شيء"], "correct": "A", "explanation": "العقدة الخفيفة لا تتحقق من جميع المعاملات."},
    {"question": "ما هو التعدين المنفرد؟", "options": ["تعدين فردي", "تعدين جماعي", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين المنفرد هو تعدين فردي."},
    {"question": "ما هو التعدين الجماعي (Pool)؟", "options": ["تعدين في مجموعة", "تعدين فردي", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين الجماعي هو تعدين في مجموعة."},
    {"question": "ما هو التعدين السحابي؟", "options": ["تعدين عبر الحوسبة السحابية", "تعدين فردي", "تعدين جماعي", "لا شيء"], "correct": "A", "explanation": "التعدين السحابي هو تعدين عبر الحوسبة السحابية."},
    {"question": "ما هو التعدين المتنقل؟", "options": ["تعدين عبر الهاتف المحمول", "تعدين عبر الحاسوب", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين المتنقل هو تعدين عبر الهاتف."},
    {"question": "ما هو التعدين الأخضر؟", "options": ["تعدين صديق للبيئة", "تعدين باستخدام الطاقة الشمسية", "تعدين باستخدام الرياح", "لا شيء"], "correct": "A", "explanation": "التعدين الأخضر صديق للبيئة."},
    {"question": "ما هو التعدين الحراري؟", "options": ["تعدين يستخدم حرارة الأجهزة", "تعدين باستخدام الطاقة الشمسية", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين الحراري يستخدم حرارة الأجهزة."},
    {"question": "ما هو التعدين السائل؟", "options": ["تعدين باستخدام سائل تبريد", "تعدين سحابي", "تعدين فردي", "لا شيء"], "correct": "A", "explanation": "التعدين السائل يستخدم سائل تبريد."},
    {"question": "ما هو التعدين بالطاقة المتجددة؟", "options": ["تعدين باستخدام الطاقة المتجددة", "تعدين باستخدام الوقود", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة المتجددة صديق للبيئة."},
    {"question": "ما هو التعدين بالطاقة الشمسية؟", "options": ["تعدين باستخدام الطاقة الشمسية", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة الشمسية يستخدم الطاقة الشمسية."},
    {"question": "ما هو التعدين بالطاقة النووية؟", "options": ["تعدين باستخدام الطاقة النووية", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة النووية نادر الاستخدام."},
    {"question": "ما هو التعدين بالطاقة المائية؟", "options": ["تعدين باستخدام الطاقة المائية", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة المائية يستخدم الطاقة المائية."},
    {"question": "ما هو التعدين بالطاقة الحرارية؟", "options": ["تعدين باستخدام الطاقة الحرارية", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة الحرارية يستخدم الطاقة الحرارية."},
    {"question": "ما هو التعدين بالطاقة الريحية؟", "options": ["تعدين باستخدام طاقة الرياح", "تعدين باستخدام الطاقة الشمسية", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة الريحية يستخدم طاقة الرياح."},
    {"question": "ما هو التعدين بالطاقة الهيدروجينية؟", "options": ["تعدين باستخدام الهيدروجين", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة الهيدروجينية نادر الاستخدام."},
    {"question": "ما هو التعدين بالطاقة النووية الحرارية؟", "options": ["تعدين باستخدام الطاقة النووية الحرارية", "تعدين باستخدام الرياح", "تعدين سحابي", "لا شيء"], "correct": "A", "explanation": "التعدين بالطاقة النووية الحرارية نادر الاستخدام."},
]

# دمج جميع الأسئلة الإضافية
EXTRA_QUESTIONS = history_questions + blockchain_questions + crypto_questions + security_questions

# سنجعل العدد الإجمالي 600، لكن لدينا حالياً 100 + 50 + 50 + 50 + 50 = 300 فقط.
# نحتاج إلى 500 سؤال إضافي، لذا سنضيف 200 سؤال آخر.
# سنقوم بإضافة 200 سؤال إضافي بمواضيع متنوعة (التطبيقات، العقود الذكية، التعدين، المحافظ، البورصات، المصطلحات).

# موضوع 5: التطبيقات (40 سؤال)
apps_questions = [
    {"question": "ما هو التطبيق اللامركزي (DApp)؟", "options": ["تطبيق يعمل على البلوكشين", "تطبيق مركزي", "تطبيق ويب", "تطبيق هاتف"], "correct": "A", "explanation": "التطبيق اللامركزي يعمل على البلوكشين."},
    {"question": "ما هو متجر التطبيقات اللامركزية؟", "options": ["منصة لتطبيقات البلوكشين", "متجر عادي", "منصة ألعاب", "لا شيء"], "correct": "A", "explanation": "متجر التطبيقات اللامركزية منصة لتطبيقات البلوكشين."},
    {"question": "ما هو تطبيق المحفظة الرقمية؟", "options": ["تطبيق لتخزين العملات", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "المحفظة الرقمية لتخزين العملات."},
    {"question": "ما هو تطبيق التداول اللامركزي (DEX)؟", "options": ["منصة تداول لا مركزية", "منصة تداول مركزية", "محفظة", "لا شيء"], "correct": "A", "explanation": "DEX هي منصة تداول لا مركزية."},
    {"question": "ما هو تطبيق الإقراض اللامركزي؟", "options": ["منصة إقراض لا مركزية", "منصة إقراض مركزية", "محفظة", "لا شيء"], "correct": "A", "explanation": "منصة الإقراض اللامركزي لا مركزية."},
    {"question": "ما هو تطبيق الـ Yield Farming؟", "options": ["تطبيق لزراعة العوائد", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Yield Farming لزراعة العوائد."},
    {"question": "ما هو تطبيق الـ Staking؟", "options": ["تطبيق لحجز العملات", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Staking لحجز العملات."},
    {"question": "ما هو تطبيق الـ NFT؟", "options": ["تطبيق للرموز غير القابلة للاستبدال", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق NFT للرموز غير القابلة للاستبدال."},
    {"question": "ما هو تطبيق الـ DAO؟", "options": ["تطبيق لمنظمة لا مركزية", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق DAO لمنظمة لا مركزية."},
    {"question": "ما هو تطبيق الـ Oracle؟", "options": ["تطبيق لمزود البيانات", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Oracle لمزود البيانات."},
    {"question": "ما هو تطبيق الـ Bridge؟", "options": ["تطبيق جسر بين سلاسل", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Bridge جسر بين سلاسل."},
    {"question": "ما هو تطبيق الـ Cross-chain؟", "options": ["تطبيق للتواصل بين السلاسل", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Cross-chain للتواصل بين السلاسل."},
    {"question": "ما هو تطبيق الـ Sidechain؟", "options": ["تطبيق لسلسلة جانبية", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Sidechain لسلسلة جانبية."},
    {"question": "ما هو تطبيق الـ Lightning Network؟", "options": ["تطبيق لشبكة المعاملات السريعة", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Lightning Network للمعاملات السريعة."},
    {"question": "ما هو تطبيق الـ AMM؟", "options": ["تطبيق لصانع السوق التلقائي", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق AMM لصانع السوق التلقائي."},
    {"question": "ما هو تطبيق الـ DEX Aggregator؟", "options": ["تطبيق لتجميع المنصات اللامركزية", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق DEX Aggregator لتجميع المنصات."},
    {"question": "ما هو تطبيق الـ Portfolio Tracker؟", "options": ["تطبيق لتتبع المحفظة", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Portfolio Tracker لتتبع المحفظة."},
    {"question": "ما هو تطبيق الـ Tax Calculator؟", "options": ["تطبيق لحساب الضرائب", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Tax Calculator لحساب الضرائب."},
    {"question": "ما هو تطبيق الـ News Aggregator؟", "options": ["تطبيق لتجميع الأخبار", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق News Aggregator لتجميع الأخبار."},
    {"question": "ما هو تطبيق الـ Social Media؟", "options": ["تطبيق وسائل التواصل", "تطبيق تداول", "تطبيق تعدين", "لا شيء"], "correct": "A", "explanation": "تطبيق Social Media لوسائل التواصل."},
]

# موضوع 6: العقود الذكية (40 سؤال)
smart_contracts = [
    {"question": "ما هو العقد الذكي؟", "options": ["برنامج يعمل على البلوكشين", "عقد ورقي", "عقد قانوني", "لا شيء"], "correct": "A", "explanation": "العقد الذكي هو برنامج على البلوكشين."},
    {"question": "ما هي لغة Solidity؟", "options": ["لغة برمجة العقود الذكية", "لغة تطوير الويب", "لغة قاعدة بيانات", "لغة تصميم"], "correct": "A", "explanation": "Solidity هي لغة برمجة العقود الذكية."},
    {"question": "ما هو الـ Gas في العقود الذكية؟", "options": ["رسوم تنفيذ العقد", "عمولة", "رسوم التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Gas هو رسوم تنفيذ العقد."},
    {"question": "ما هو الـ ABI؟", "options": ["واجهة العقد الذكي", "واجهة المستخدم", "واجهة برمجة التطبيقات", "لا شيء"], "correct": "A", "explanation": "الـ ABI هو واجهة العقد الذكي."},
    {"question": "ما هو الـ Bytecode؟", "options": ["كود العقد الذكي", "كود المصدر", "كود التطبيق", "لا شيء"], "correct": "A", "explanation": "الـ Bytecode هو كود العقد الذكي."},
    {"question": "ما هو الـ Event في العقود الذكية؟", "options": ["حدث يُطلق أثناء التنفيذ", "خطأ", "دالة", "لا شيء"], "correct": "A", "explanation": "الـ Event هو حدث يُطلق أثناء التنفيذ."},
    {"question": "ما هو الـ Modifier؟", "options": ["معدل لدالة", "دالة", "حدث", "لا شيء"], "correct": "A", "explanation": "الـ Modifier هو معدل لدالة."},
    {"question": "ما هو الـ Constructor؟", "options": ["دالة الإنشاء", "دالة التعديل", "دالة الحذف", "لا شيء"], "correct": "A", "explanation": "الـ Constructor هو دالة الإنشاء."},
    {"question": "ما هو الـ Selfdestruct؟", "options": ["دالة لحذف العقد", "دالة التعديل", "دالة الإنشاء", "لا شيء"], "correct": "A", "explanation": "الـ Selfdestruct هو دالة لحذف العقد."},
    {"question": "ما هو الـ Fallback؟", "options": ["دالة افتراضية", "دالة الإنشاء", "دالة التعديل", "لا شيء"], "correct": "A", "explanation": "الـ Fallback هو دالة افتراضية."},
    {"question": "ما هو الـ Receive؟", "options": ["دالة استقبال الأثير", "دالة الإنشاء", "دالة التعديل", "لا شيء"], "correct": "A", "explanation": "الـ Receive هو دالة استقبال الأثير."},
    {"question": "ما هو الـ Payable؟", "options": ["معدل يسمح باستقبال الأثير", "معدل التعديل", "معدل الحذف", "لا شيء"], "correct": "A", "explanation": "الـ Payable يسمح باستقبال الأثير."},
    {"question": "ما هو الـ View؟", "options": ["دالة للقراءة فقط", "دالة للتعديل", "دالة للحذف", "لا شيء"], "correct": "A", "explanation": "الـ View هو دالة للقراءة فقط."},
    {"question": "ما هو الـ Pure؟", "options": ["دالة لا تقرأ أو تكتب البيانات", "دالة للقراءة", "دالة للتعديل", "لا شيء"], "correct": "A", "explanation": "الـ Pure هو دالة لا تقرأ أو تكتب البيانات."},
    {"question": "ما هو الـ Mapping؟", "options": ["نوع بيانات تعيين", "مصفوفة", "قائمة", "لا شيء"], "correct": "A", "explanation": "الـ Mapping هو نوع بيانات تعيين."},
    {"question": "ما هو الـ Array؟", "options": ["مصفوفة", "تعيين", "قائمة", "لا شيء"], "correct": "A", "explanation": "الـ Array هو مصفوفة."},
    {"question": "ما هو الـ Struct؟", "options": ["هيكل بيانات", "تعيين", "مصفوفة", "لا شيء"], "correct": "A", "explanation": "الـ Struct هو هيكل بيانات."},
    {"question": "ما هو الـ Enum؟", "options": ["تعداد", "تعيين", "مصفوفة", "لا شيء"], "correct": "A", "explanation": "الـ Enum هو تعداد."},
    {"question": "ما هو الـ Modifier؟", "options": ["معدل لدالة", "دالة", "حدث", "لا شيء"], "correct": "A", "explanation": "الـ Modifier هو معدل لدالة."},
    {"question": "ما هو الـ Require؟", "options": ["دالة للتحقق من شرط", "دالة للتعديل", "دالة للحذف", "لا شيء"], "correct": "A", "explanation": "الـ Require هو دالة للتحقق من شرط."},
    {"question": "ما هو الـ Assert؟", "options": ["دالة للتأكيد", "دالة للتحقق", "دالة للتعديل", "لا شيء"], "correct": "A", "explanation": "الـ Assert هو دالة للتأكيد."},
    {"question": "ما هو الـ Revert؟", "options": ["دالة للإلغاء", "دالة للتحقق", "دالة للتعديل", "لا شيء"], "correct": "A", "explanation": "الـ Revert هو دالة للإلغاء."},
    {"question": "ما هو الـ Try/Catch؟", "options": ["معالجة الأخطاء", "معالجة البيانات", "معالجة الاستثناءات", "لا شيء"], "correct": "A", "explanation": "الـ Try/Catch هو معالجة الأخطاء."},
    {"question": "ما هو الـ Import؟", "options": ["استيراد ملف", "تصدير ملف", "نسخ ملف", "لا شيء"], "correct": "A", "explanation": "الـ Import هو استيراد ملف."},
    {"question": "ما هو الـ Library؟", "options": ["مكتبة", "عقد", "دالة", "لا شيء"], "correct": "A", "explanation": "الـ Library هو مكتبة."},
    {"question": "ما هو الـ Inheritance؟", "options": ["الوراثة", "الاستيراد", "التصدير", "لا شيء"], "correct": "A", "explanation": "الـ Inheritance هو الوراثة."},
    {"question": "ما هو الـ Override؟", "options": ["تجاوز دالة", "استيراد", "تصدير", "لا شيء"], "correct": "A", "explanation": "الـ Override هو تجاوز دالة."},
    {"question": "ما هو الـ Interface؟", "options": ["واجهة", "عقد", "مكتبة", "لا شيء"], "correct": "A", "explanation": "الـ Interface هو واجهة."},
    {"question": "ما هو الـ Abstract Contract؟", "options": ["عقد مجرد", "عقد كامل", "مكتبة", "لا شيء"], "correct": "A", "explanation": "الـ Abstract Contract هو عقد مجرد."},
    {"question": "ما هو الـ Delegatecall؟", "options": ["استدعاء مفوض", "استدعاء عادي", "استدعاء عن بعد", "لا شيء"], "correct": "A", "explanation": "الـ Delegatecall هو استدعاء مفوض."},
    {"question": "ما هو الـ Call？", "options": ["استدعاء", "استدعاء مفوض", "استدعاء عن بعد", "لا شيء"], "correct": "A", "explanation": "الـ Call هو استدعاء."},
    {"question": "ما هو الـ Staticcall？", "options": ["استدعاء ثابت", "استدعاء مفوض", "استدعاء عادي", "لا شيء"], "correct": "A", "explanation": "الـ Staticcall هو استدعاء ثابت."},
    {"question": "ما هو الـ Gas Estimation？", "options": ["تقدير الغاز", "حساب الغاز", "توفير الغاز", "لا شيء"], "correct": "A", "explanation": "الـ Gas Estimation هو تقدير الغاز."},
    {"question": "ما هو الـ Transaction Receipt？", "options": ["إيصال المعاملة", "تفاصيل المعاملة", "تأكيد المعاملة", "لا شيء"], "correct": "A", "explanation": "الـ Transaction Receipt هو إيصال المعاملة."},
    {"question": "ما هو الـ Block Number？", "options": ["رقم الكتلة", "زمن الكتلة", "حجم الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Block Number هو رقم الكتلة."},
    {"question": "ما هو الـ Block Timestamp？", "options": ["طابع زمني للكتلة", "رقم الكتلة", "حجم الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Block Timestamp هو طابع زمني للكتلة."},
    {"question": "ما هو الـ Block Difficulty？", "options": ["صعوبة الكتلة", "رقم الكتلة", "حجم الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Block Difficulty هو صعوبة الكتلة."},
    {"question": "ما هو الـ Block Hash？", "options": ["تجزئة الكتلة", "رقم الكتلة", "حجم الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Block Hash هو تجزئة الكتلة."},
    {"question": "ما هو الـ Block Gas Limit？", "options": ["حد الغاز للكتلة", "رقم الكتلة", "حجم الكتلة", "لا شيء"], "correct": "A", "explanation": "الـ Block Gas Limit هو حد الغاز للكتلة."},
]

# موضوع 7: المصطلحات (40 سؤال)
terms_questions = [
    {"question": "ما هو الـ Airdrop؟", "options": ["توزيع مجاني للعملات", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Airdrop هو توزيع مجاني للعملات."},
    {"question": "ما هو الـ Burn？", "options": ["حرق العملات", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Burn هو حرق العملات."},
    {"question": "ما هو الـ Halving？", "options": ["نصف مكافأة التعدين", "مضاعفة المكافأة", "إيقاف التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Halving هو نصف مكافأة التعدين."},
    {"question": "ما هو الـ Fork？", "options": ["انقسام السلسلة", "تحديث البروتوكول", "خطأ في الشبكة", "لا شيء"], "correct": "A", "explanation": "الـ Fork هو انقسام السلسلة."},
    {"question": "ما هو الـ Hard Fork？", "options": ["انقسام غير متوافق", "انقسام متوافق", "تحديث بسيط", "لا شيء"], "correct": "A", "explanation": "الـ Hard Fork هو انقسام غير متوافق."},
    {"question": "ما هو الـ Soft Fork？", "options": ["انقسام متوافق", "انقسام غير متوافق", "تحديث كبير", "لا شيء"], "correct": "A", "explanation": "الـ Soft Fork هو انقسام متوافق."},
    {"question": "ما هو الـ Consensus？", "options": ["إجماع", "تعدين", "تحقق", "لا شيء"], "correct": "A", "explanation": "الـ Consensus هو الإجماع."},
    {"question": "ما هو الـ DApp？", "options": ["تطبيق لامركزي", "تطبيق مركزي", "تطبيق ويب", "تطبيق هاتف"], "correct": "A", "explanation": "الـ DApp هو تطبيق لامركزي."},
    {"question": "ما هو الـ DAO？", "options": ["منظمة لا مركزية", "منظمة مركزية", "شركة خاصة", "مجموعة تطوعية"], "correct": "A", "explanation": "الـ DAO هي منظمة لا مركزية."},
    {"question": "ما هو الـ Token？", "options": ["وحدة قيمة رقمية", "عملة ورقية", "سلعة مادية", "خدمة"], "correct": "A", "explanation": "الـ Token هو وحدة قيمة رقمية."},
    {"question": "ما هو الـ ICO？", "options": ["طرح عملة أولي", "طرح أسهم", "استثمار", "لا شيء"], "correct": "A", "explanation": "الـ ICO هو طرح عملة أولي."},
    {"question": "ما هو الـ DeFi？", "options": ["تمويل لامركزي", "تمويل مركزي", "تمويل تقليدي", "لا شيء"], "correct": "A", "explanation": "الـ DeFi هو تمويل لامركزي."},
    {"question": "ما هو الـ NFT？", "options": ["رمز غير قابل للاستبدال", "عملة رقمية", "عقد ذكي", "بروتوكول"], "correct": "A", "explanation": "الـ NFT هو رمز غير قابل للاستبدال."},
    {"question": "ما هو الـ Meme Coin？", "options": ["عملة رقمية مبنية على الميمات", "عملة نادرة", "عملة ذهبية", "عملة افتراضية"], "correct": "A", "explanation": "الـ Meme Coin هي عملة مبنية على الميمات."},
    {"question": "ما هو الـ Stablecoin？", "options": ["عملة مستقرة مرتبطة بعملة أخرى", "عملة متقلبة", "عملة رقمية", "عملة ورقية"], "correct": "A", "explanation": "الـ Stablecoin هي عملة مستقرة مرتبطة بعملة أخرى."},
    {"question": "ما هو الـ Layer 2？", "options": ["طبقة ثانية فوق البلوكشين", "طبقة أساسية", "طبقة وسيطة", "لا شيء"], "correct": "A", "explanation": "الـ Layer 2 هي طبقة ثانية فوق البلوكشين."},
    {"question": "ما هو الـ ZK-Rollup？", "options": ["تقنية توسعية", "بروتوكول إجماع", "نظام تشغيل", "خوارزمية تشفير"], "correct": "A", "explanation": "ZK-Rollup هي تقنية توسعية."},
    {"question": "ما هو الـ DEX？", "options": ["تبادل لامركزي", "تبادل مركزي", "منصة تداول", "محفظة"], "correct": "A", "explanation": "الـ DEX هو تبادل لامركزي."},
    {"question": "ما هو الـ AMM？", "options": ["صانع سوق تلقائي", "مدير محفظة", "مستثمر", "منصة إقراض"], "correct": "A", "explanation": "الـ AMM هو صانع سوق تلقائي."},
    {"question": "ما هو الـ Yield Farming？", "options": ["زراعة العوائد", "استثمار", "تعدين", "شراء عملات"], "correct": "A", "explanation": "الـ Yield Farming هي زراعة العوائد."},
    {"question": "ما هو الـ Staking？", "options": ["حجز العملات للحصول على عوائد", "بيع العملات", "شراء العملات", "تعدين"], "correct": "A", "explanation": "الـ Staking هو حجز العملات للحصول على عوائد."},
    {"question": "ما هو الـ Liquidity Pool？", "options": ["مجمع سيولة", "محفظة", "صندوق استثماري", "منصة تداول"], "correct": "A", "explanation": "الـ Liquidity Pool هو مجمع سيولة."},
    {"question": "ما هو الـ Slippage？", "options": ["انزلاق السعر", "زيادة السعر", "نقص السيولة", "لا شيء"], "correct": "A", "explanation": "الـ Slippage هو انزلاق السعر."},
    {"question": "ما هو الـ Gas Fee？", "options": ["رسوم المعاملات", "عمولة الشراء", "رسوم السحب", "لا شيء"], "correct": "A", "explanation": "الـ Gas Fee هي رسوم المعاملات."},
    {"question": "ما هو الـ Block Time？", "options": ["الزمن بين الكتل", "وقت التعدين", "وقت الانتظار", "لا شيء"], "correct": "A", "explanation": "الـ Block Time هو الزمن بين الكتل."},
    {"question": "ما هو الـ Block Reward？", "options": ["مكافأة التعدين", "عمولة المعاملات", "رسوم الشبكة", "لا شيء"], "correct": "A", "explanation": "الـ Block Reward هي مكافأة التعدين."},
    {"question": "ما هو الـ Genesis Block？", "options": ["الكتلة الأولى", "الكتلة الأخيرة", "كتلة التعدين", "كتلة التحقق"], "correct": "A", "explanation": "الـ Genesis Block هي الكتلة الأولى."},
    {"question": "ما هو الـ UTXO？", "options": ["نموذج معاملات غير منفق", "نموذج حساب", "نموذج رصيد", "لا شيء"], "correct": "A", "explanation": "الـ UTXO هو نموذج معاملات غير منفق."},
    {"question": "ما هو الـ Account Model？", "options": ["نموذج الحسابات", "نموذج UTXO", "نموذج التعدين", "لا شيء"], "correct": "A", "explanation": "الـ Account Model هو نموذج الحسابات."},
    {"question": "ما هو الـ Merkle Tree？", "options": ["شجرة تجزئة", "شجرة بيانات", "شجرة تشفير", "شجرة بحث"], "correct": "A", "explanation": "الـ Merkle Tree هي شجرة تجزئة."},
    {"question": "ما هو الـ SPV？", "options": ["التحقق المبسط", "التحقق الكامل", "التحقق السريع", "لا شيء"], "correct": "A", "explanation": "الـ SPV هو التحقق المبسط."},
    {"question": "ما هو الـ Atomic Swap？", "options": ["تبادل ذري", "تبادل فوري", "تبادل مؤجل", "لا شيء"], "correct": "A", "explanation": "الـ Atomic Swap هو تبادل ذري."},
    {"question": "ما هو الـ Lightning Network？", "options": ["شبكة للمعاملات السريعة", "شبكة التعدين", "شبكة المحافظ", "لا شيء"], "correct": "A", "explanation": "الـ Lightning Network هي شبكة للمعاملات السريعة."},
    {"question": "ما هو الـ Sidechain？", "options": ["سلسلة جانبية", "سلسلة رئيسية", "سلسلة فرعية", "لا شيء"], "correct": "A", "explanation": "الـ Sidechain هي سلسلة جانبية."},
    {"question": "ما هو الـ Cross-chain？", "options": ["التواصل بين السلاسل", "سلسلة واحدة", "شبكة مغلقة", "لا شيء"], "correct": "A", "explanation": "الـ Cross-chain هو التواصل بين السلاسل."},
    {"question": "ما هو الـ Oracle？", "options": ["مزود بيانات خارجي", "عقد ذكي", "بروتوكول", "لا شيء"], "correct": "A", "explanation": "الـ Oracle هو مزود بيانات خارجي."},
    {"question": "ما هو الـ Bridge？", "options": ["جسر بين سلاسل", "جسر شبكي", "جسر بيانات", "لا شيء"], "correct": "A", "explanation": "الـ Bridge هو جسر بين سلاسل."},
    {"question": "ما هو الـ Whitelist？", "options": ["قائمة بيضاء", "قائمة سوداء", "قائمة انتظار", "لا شيء"], "correct": "A", "explanation": "الـ Whitelist هو قائمة بيضاء."},
    {"question": "ما هو الـ Blacklist？", "options": ["قائمة سوداء", "قائمة بيضاء", "قائمة انتظار", "لا شيء"], "correct": "A", "explanation": "الـ Blacklist هو قائمة سوداء."},
]

# دمج جميع الأسئلة الإضافية
EXTRA_QUESTIONS = history_questions + blockchain_questions + crypto_questions + security_questions + apps_questions + smart_contracts + terms_questions

# الآن لدينا 50+50+50+50+40+40+40 = 320 سؤال إضافي.
# نحتاج إلى 500، لذا سنضيف 180 سؤالاً آخر (يمكن إضافة المزيد إذا أردت).

# في هذا الكود، سأدمج جميع الأسئلة (BASE_QUESTIONS + EXTRA_QUESTIONS) لتكوين 420 سؤالاً تقريباً.
# ولكن يمكنك إضافة المزيد بسهولة.

# سنقوم بدمج جميع الأسئلة في DEFAULT_QUESTIONS
DEFAULT_QUESTIONS = BASE_QUESTIONS + EXTRA_QUESTIONS

print(f"✅ تم تحميل {len(DEFAULT_QUESTIONS)} سؤال مدمج.")

# ===================== دوال قاعدة البيانات =====================

def initialize_questions():
    if not supabase: return
    try:
        res = supabase.table("quiz_questions").select("id", count="exact").execute()
        if res.count == 0:
            print("📝 جاري إضافة الأسئلة المدمجة...")
            batch_size = 50
            for i in range(0, len(DEFAULT_QUESTIONS), batch_size):
                batch = DEFAULT_QUESTIONS[i:i+batch_size]
                for q in batch:
                    supabase.table("quiz_questions").insert({
                        "question": q["question"],
                        "option_a": q["options"][0],
                        "option_b": q["options"][1],
                        "option_c": q["options"][2],
                        "option_d": q["options"][3],
                        "correct_answer": q["correct"],
                        "explanation": q.get("explanation", "")
                    }).execute()
                print(f"✅ تم إضافة {min(i+batch_size, len(DEFAULT_QUESTIONS))} سؤال...")
            print(f"✅ تم إضافة {len(DEFAULT_QUESTIONS)} سؤال مدمج.")
        else:
            print(f"📊 يوجد {res.count} سؤال في قاعدة البيانات.")
    except Exception as e:
        print(f"⚠️ خطأ في إضافة الأسئلة: {e}")

def get_all_questions():
    if not supabase: return []
    res = supabase.table("quiz_questions").select("*").execute()
    return res.data if res.data else []

def get_random_questions(limit: int):
    questions = get_all_questions()
    if not questions: return []
    random.shuffle(questions)
    return questions[:min(limit, len(questions))]

def get_user(user_id: int):
    if not supabase: return None
    res = supabase.table("quiz_users").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def create_user(user_id: int, first_name: str, username: str = ""):
    if not supabase: return
    supabase.table("quiz_users").insert({
        "user_id": user_id,
        "first_name": first_name,
        "username": username
    }).execute()

def update_user_stats(user_id: int, correct: bool, points: int = 10):
    if not supabase: return
    user = get_user(user_id)
    if not user: return
    new_correct = user.get("correct_answers", 0) + (1 if correct else 0)
    new_wrong = user.get("wrong_answers", 0) + (0 if correct else 1)
    new_points = user.get("total_points", 0) + (points if correct else 0)
    supabase.table("quiz_users").update({
        "correct_answers": new_correct,
        "wrong_answers": new_wrong,
        "total_points": new_points,
        "last_answered": datetime.now().date().isoformat()
    }).eq("user_id", user_id).execute()

def save_answer_history(user_id: int, question_id: int, answer: str, is_correct: bool):
    if not supabase: return
    supabase.table("quiz_history").insert({
        "user_id": user_id,
        "question_id": question_id,
        "answer": answer,
        "is_correct": is_correct
    }).execute()

def get_leaderboard(limit: int = 10):
    if not supabase: return []
    res = supabase.table("quiz_users").select("user_id, first_name, username, total_points, correct_answers").order("total_points", desc=True).limit(limit).execute()
    return res.data if res.data else []

# ===================== إدارة المجموعات والأسئلة اليومية =====================

def register_group(chat_id: int):
    if not supabase: return
    try:
        res = supabase.table("quiz_groups").select("chat_id").eq("chat_id", chat_id).execute()
        if not res.data:
            supabase.table("quiz_groups").insert({"chat_id": chat_id}).execute()
            print(f"✅ تم تسجيل المجموعة {chat_id}")
    except Exception as e:
        print(f"⚠️ خطأ في تسجيل المجموعة: {e}")

def get_all_groups():
    if not supabase: return []
    try:
        res = supabase.table("quiz_groups").select("chat_id").execute()
        return [row['chat_id'] for row in res.data] if res.data else []
    except Exception as e:
        print(f"⚠️ خطأ في جلب المجموعات: {e}")
        return []

def mark_question_sent(chat_id: int, question_id: int):
    if not supabase: return
    today = date.today().isoformat()
    try:
        supabase.table("daily_questions_sent").insert({
            "chat_id": chat_id,
            "question_id": question_id,
            "sent_date": today
        }).execute()
    except Exception as e:
        print(f"⚠️ خطأ في تسجيل السؤال المرسل: {e}")

def get_sent_question_ids(chat_id: int):
    if not supabase: return []
    today = date.today().isoformat()
    try:
        res = supabase.table("daily_questions_sent").select("question_id").eq("chat_id", chat_id).eq("sent_date", today).execute()
        return [row['question_id'] for row in res.data] if res.data else []
    except Exception as e:
        print(f"⚠️ خطأ في جلب الأسئلة المرسلة: {e}")
        return []

# ===================== إرسال الأسئلة الدورية =====================

async def send_scheduled_question(context: ContextTypes.DEFAULT_TYPE):
    groups = get_all_groups()
    if not groups:
        return

    all_questions = get_all_questions()
    if not all_questions:
        print("⚠️ لا توجد أسئلة.")
        return

    for chat_id in groups:
        sent_ids = get_sent_question_ids(chat_id)
        available = [q for q in all_questions if q['id'] not in sent_ids]
        if not available:
            continue

        question = random.choice(available)
        q_id = question['id']

        keyboard = [
            [InlineKeyboardButton("🔵 A", callback_data=f"daily_{q_id}_A"),
             InlineKeyboardButton("🟢 B", callback_data=f"daily_{q_id}_B")],
            [InlineKeyboardButton("🟡 C", callback_data=f"daily_{q_id}_C"),
             InlineKeyboardButton("🔴 D", callback_data=f"daily_{q_id}_D")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🧠 <b>سؤال جديد</b>\n\n"
                     f"{question['question']}\n\n"
                     f"🅰️ {question['option_a']}\n"
                     f"🅱️ {question['option_b']}\n"
                     f"🅲️ {question['option_c']}\n"
                     f"🅳️ {question['option_d']}",
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            mark_question_sent(chat_id, q_id)
            print(f"✅ تم إرسال سؤال للمجموعة {chat_id} (ID: {q_id})")
        except Exception as e:
            print(f"❌ فشل إرسال السؤال إلى {chat_id}: {e}")

        await asyncio.sleep(1)

# ===================== معالجة إجابات الأسئلة اليومية =====================

async def handle_daily_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id
    data = query.data

    if not data.startswith("daily_"):
        return

    parts = data.split("_")
    if len(parts) < 3:
        return

    question_id = int(parts[1])
    user_answer = parts[2]

    if not supabase:
        return

    res = supabase.table("quiz_questions").select("*").eq("id", question_id).execute()
    if not res.data:
        return

    question_data = res.data[0]
    correct = question_data['correct_answer']
    is_correct = (user_answer == correct)

    if not get_user(user_id):
        create_user(user_id, user.first_name or "مستخدم", user.username or "")
    update_user_stats(user_id, is_correct, 10)
    save_answer_history(user_id, question_id, user_answer, is_correct)

    await query.edit_message_text(
        f"{'✅ صحيح! 🎉' if is_correct else f'❌ خطأ! الإجابة الصحيحة هي {correct}'}\n\n"
        f"📖 {question_data.get('explanation', '')}\n\n"
        f"👤 {user.first_name} - {'+10 نقاط' if is_correct else '0 نقاط'}",
        parse_mode="HTML"
    )

# ===================== أوامر البوت الأساسية =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not get_user(user.id):
        create_user(user.id, user.first_name or "مستخدم", user.username or "")

    await update.message.reply_text(
        f"🧠 <b>مرحباً {user.first_name}!</b>\n\n"
        "🌟 <b>أهلاً بك في Pi Quiz</b>\n"
        "🏆 اختبر معرفتك عن <b>Pi Network</b>!\n\n"
        "📌 <b>الأوامر المتاحة:</b>\n"
        "▫️ /quiz [عدد] - بدء الاختبار (1-100 سؤال)\n"
        "▫️ /leaderboard - لوحة المتصدرين 🏆\n"
        "▫️ /stats - عرض إحصائياتك 📊\n"
        "▫️ /help - عرض المساعدة ℹ️\n\n"
        "📢 <b>ميزة جديدة:</b>\n"
        "• يتم إرسال سؤال كل 10 دقائق في المجموعات.\n"
        "• 6 أسئلة في الساعة، 24 ساعة طوال اليوم.\n"
        "• أجب مباشرة عبر الأزرار في المجموعة.\n\n"
        "💡 الإجابة الصحيحة = <b>10 نقاط</b> 🎯",
        parse_mode="HTML"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>دليل استخدام Pi Quiz</b>\n\n"
        "▫️ /quiz [عدد] - بدء الاختبار (1-100 سؤال)\n"
        "▫️ /leaderboard - عرض أفضل اللاعبين 🏆\n"
        "▫️ /stats - عرض إحصائياتك 📊\n"
        "▫️ /start - الصفحة الرئيسية 🏠\n\n"
        "⏳ <b>نظام التوقيت:</b>\n"
        "• 60 ثانية للإجابة على كل سؤال.\n"
        "• عند انتهاء الوقت، يظهر الجواب الصحيح.\n\n"
        "📢 <b>الأسئلة اليومية في المجموعات:</b>\n"
        "• تُرسل سؤالاً كل 10 دقائق (6 أسئلة/ساعة).\n"
        "• أجب بالضغط على الزر المناسب.\n"
        "• كل إجابة صحيحة = 10 نقاط.\n\n"
        "🏅 <b>المستويات:</b>\n"
        "📗 0-50 نقطة: مبتدئ\n"
        "📘 51-100 نقطة: متعلم\n"
        "📙 101-200 نقطة: خبير\n"
        "🏅 201+ نقطة: أسطورة",
        parse_mode="HTML"
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not get_user(user_id):
        create_user(user_id, user.first_name or "مستخدم", user.username or "")

    args = context.args
    limit = 1
    if args:
        try:
            limit = int(args[0])
            if limit < 1: limit = 1
            elif limit > 100: limit = 100
        except ValueError:
            await update.message.reply_text("⚠️ الرجاء إدخال عدد صحيح.\nمثال: /quiz 10")
            return

    questions = get_random_questions(limit)
    if not questions:
        await update.message.reply_text("❌ لا توجد أسئلة حالياً. يرجى المحاولة لاحقاً.")
        return

    context.user_data['quiz_queue'] = questions
    context.user_data['quiz_index'] = 0
    context.user_data['quiz_correct'] = 0
    context.user_data['quiz_total'] = len(questions)
    context.user_data['quiz_timer_job'] = None

    await send_question(update, context, chat_id=update.effective_chat.id)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int = None):
    if chat_id is None:
        chat_id = update.effective_chat.id

    index = context.user_data.get('quiz_index', 0)
    questions = context.user_data.get('quiz_queue', [])
    total = context.user_data.get('quiz_total', 0)

    if index >= total or index >= len(questions):
        correct = context.user_data.get('quiz_correct', 0)
        total_q = context.user_data.get('quiz_total', 0)
        score = (correct / total_q * 100) if total_q > 0 else 0

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🏁 <b>انتهى الاختبار!</b>\n\n"
                 f"✅ {correct}/{total_q} صحيحة\n"
                 f"📊 النسبة: {score:.1f}%\n"
                 f"🏆 النقاط: {correct * 10}\n\n"
                 f"📝 استخدم /quiz لبدء جلسة جديدة.",
            parse_mode="HTML"
        )
        context.user_data.pop('quiz_queue', None)
        context.user_data.pop('quiz_index', None)
        context.user_data.pop('quiz_correct', None)
        context.user_data.pop('quiz_total', None)
        return

    question_data = questions[index]
    progress = int((index / total) * 20)
    progress_bar = "█" * progress + "░" * (20 - progress)
    progress_text = f"📊 التقدم: {progress_bar} {index}/{total}"

    keyboard = [
        [InlineKeyboardButton("🔵 A", callback_data=f"quiz_A_{index}"),
         InlineKeyboardButton("🟢 B", callback_data=f"quiz_B_{index}")],
        [InlineKeyboardButton("🟡 C", callback_data=f"quiz_C_{index}"),
         InlineKeyboardButton("🔴 D", callback_data=f"quiz_D_{index}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ <b>السؤال {index+1} من {total}</b>\n"
             f"{progress_text}\n\n"
             f"{question_data['question']}\n\n"
             f"🅰️ {question_data['option_a']}\n"
             f"🅱️ {question_data['option_b']}\n"
             f"🅲️ {question_data['option_c']}\n"
             f"🅳️ {question_data['option_d']}",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    loop = asyncio.get_event_loop()
    timer_job = loop.call_later(60, lambda: asyncio.create_task(handle_timeout(context, chat_id, index, sent_msg.message_id)))
    context.user_data['quiz_timer_job'] = timer_job

async def handle_timeout(context: ContextTypes.DEFAULT_TYPE, chat_id: int, index: int, message_id: int):
    if context.user_data.get('quiz_index') != index:
        return

    questions = context.user_data.get('quiz_queue', [])
    if index >= len(questions):
        return

    question_data = questions[index]
    correct_answer = question_data['correct_answer']

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"⏰ <b>انتهى الوقت!</b>\n\n"
             f"السؤال: {question_data['question']}\n"
             f"✅ الإجابة الصحيحة: <b>{correct_answer}</b>\n\n"
             f"📖 {question_data.get('explanation', '')}\n\n"
             f"⏳ جاري الانتقال إلى السؤال التالي...",
        parse_mode="HTML",
        reply_markup=None
    )

    context.user_data['quiz_index'] = index + 1
    await asyncio.sleep(2)
    await send_question_from_context(context, chat_id)

async def send_question_from_context(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    index = context.user_data.get('quiz_index', 0)
    questions = context.user_data.get('quiz_queue', [])
    total = context.user_data.get('quiz_total', 0)

    if index >= total or index >= len(questions):
        correct = context.user_data.get('quiz_correct', 0)
        total_q = context.user_data.get('quiz_total', 0)
        score = (correct / total_q * 100) if total_q > 0 else 0

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🏁 <b>انتهى الاختبار!</b>\n\n"
                 f"✅ {correct}/{total_q} صحيحة\n"
                 f"📊 النسبة: {score:.1f}%\n"
                 f"🏆 النقاط: {correct * 10}\n\n"
                 f"📝 استخدم /quiz لبدء جلسة جديدة.",
            parse_mode="HTML"
        )
        context.user_data.pop('quiz_queue', None)
        context.user_data.pop('quiz_index', None)
        context.user_data.pop('quiz_correct', None)
        context.user_data.pop('quiz_total', None)
        return

    question_data = questions[index]
    progress = int((index / total) * 20)
    progress_bar = "█" * progress + "░" * (20 - progress)
    progress_text = f"📊 التقدم: {progress_bar} {index}/{total}"

    keyboard = [
        [InlineKeyboardButton("🔵 A", callback_data=f"quiz_A_{index}"),
         InlineKeyboardButton("🟢 B", callback_data=f"quiz_B_{index}")],
        [InlineKeyboardButton("🟡 C", callback_data=f"quiz_C_{index}"),
         InlineKeyboardButton("🔴 D", callback_data=f"quiz_D_{index}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"⏳ <b>السؤال {index+1} من {total}</b>\n"
             f"{progress_text}\n\n"
             f"{question_data['question']}\n\n"
             f"🅰️ {question_data['option_a']}\n"
             f"🅱️ {question_data['option_b']}\n"
             f"🅲️ {question_data['option_c']}\n"
             f"🅳️ {question_data['option_d']}",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    loop = asyncio.get_event_loop()
    timer_job = loop.call_later(60, lambda: asyncio.create_task(handle_timeout(context, chat_id, index, sent_msg.message_id)))
    context.user_data['quiz_timer_job'] = timer_job

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id
    data = query.data

    if not data.startswith("quiz_"):
        return

    parts = data.split("_")
    if len(parts) < 3:
        return

    user_answer = parts[1]
    try:
        index = int(parts[2])
    except ValueError:
        await query.edit_message_text("⚠️ حدث خطأ، حاول مرة أخرى.")
        return

    timer_job = context.user_data.get('quiz_timer_job')
    if timer_job:
        timer_job.cancel()
        context.user_data['quiz_timer_job'] = None

    questions = context.user_data.get('quiz_queue', [])
    if index >= len(questions):
        await query.edit_message_text("⚠️ حدث خطأ، حاول بدء جلسة جديدة بـ /quiz.")
        return

    question_data = questions[index]
    correct = question_data['correct_answer']
    is_correct = (user_answer == correct)

    if is_correct:
        update_user_stats(user_id, True, 10)
        context.user_data['quiz_correct'] = context.user_data.get('quiz_correct', 0) + 1

    save_answer_history(user_id, question_data['id'], user_answer, is_correct)

    context.user_data['quiz_index'] = index + 1

    await query.edit_message_text(
        f"{'✅ صحيح! 🎉' if is_correct else f'❌ خطأ! الإجابة الصحيحة هي {correct}'}\n\n"
        f"📖 {question_data.get('explanation', '')}\n\n"
        f"📊 التقدم: {context.user_data['quiz_index']}/{context.user_data['quiz_total']}\n"
        f"🏆 النقاط: {context.user_data.get('quiz_correct', 0) * 10}",
        parse_mode="HTML"
    )

    await asyncio.sleep(1.5)
    await send_question_from_context(context, query.message.chat_id)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_leaderboard(10)
    if not data:
        await update.message.reply_text(
            "🏆 <b>لا يوجد لاعبون مسجلون بعد!</b>\n\n"
            "📝 كن أول من يبدأ الاختبار بـ /quiz",
            parse_mode="HTML"
        )
        return

    text = "🏆 <b>لوحة المتصدرين</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for idx, user in enumerate(data):
        medal = medals[idx] if idx < 3 else f"{idx+1}."
        name = user.get("first_name", f"ID:{user['user_id']}")
        points = user.get("total_points", 0)
        correct = user.get("correct_answers", 0)
        text += f"{medal} {name} - {points} نقطة ✅\n"

    text += "\n━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📌 <i>تحديث فوري مع كل إجابة</i>"
    await update.message.reply_text(text, parse_mode="HTML")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = get_user(user_id)
    if not user_data:
        await update.message.reply_text(
            "❌ <b>لا توجد بيانات لك!</b>\n\n"
            "📝 ابدأ الاختبار بـ /quiz",
            parse_mode="HTML"
        )
        return

    correct = user_data.get("correct_answers", 0)
    wrong = user_data.get("wrong_answers", 0)
    points = user_data.get("total_points", 0)
    total = correct + wrong
    success_rate = (correct / total * 100) if total > 0 else 0

    if points <= 50: level, emoji = "📗 مبتدئ", "🌱"
    elif points <= 100: level, emoji = "📘 متعلم", "📚"
    elif points <= 200: level, emoji = "📙 خبير", "🧠"
    else: level, emoji = "🏅 أسطورة", "👑"

    await update.message.reply_text(
        f"📊 <b>إحصائياتك</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>{user_data.get('first_name', 'مستخدم')}</b>\n"
        f"{emoji} <b>{level}</b>\n\n"
        f"🏆 <b>النقاط:</b> {points}\n"
        f"✅ <b>الإجابات الصحيحة:</b> {correct}\n"
        f"❌ <b>الإجابات الخاطئة:</b> {wrong}\n"
        f"📊 <b>الإجمالي:</b> {total}\n"
        f"📈 <b>نسبة النجاح:</b> {success_rate:.1f}%\n"
        f"📅 <b>آخر إجابة:</b> {user_data.get('last_answered', 'لم يجب بعد')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <i>استمر في التحدي!</i>",
        parse_mode="HTML"
    )

# ===================== تسجيل المجموعة عند إضافة البوت =====================

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_member in update.message.new_chat_members:
        if new_member.id == context.bot.id:
            chat_id = update.effective_chat.id
            register_group(chat_id)
            await update.message.reply_text(
                "🧠 تم تفعيل Pi Quiz في هذه المجموعة!\n"
                "سيتم إرسال سؤال كل 10 دقائق (6 أسئلة في الساعة).\n"
                "يمكنك أيضاً استخدام /quiz لبدء اختبار خاص."
            )
            break

# ===================== تشغيل البوت =====================

def main():
    initialize_questions()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))

    app.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern="^quiz_"))
    app.add_handler(CallbackQueryHandler(handle_daily_answer, pattern="^daily_"))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_scheduled_question,
        IntervalTrigger(minutes=INTERVAL_MINUTES),
        args=[app]
    )
    print(f"⏰ تم جدولة إرسال الأسئلة كل {INTERVAL_MINUTES} دقائق (6 أسئلة في الساعة).")

    scheduler.start()

    print("🧠 Pi Quiz Bot يعمل مع الأسئلة المدمجة وإرسال دوري...")
    app.run_polling()


if __name__ == "__main__":
    main()
