# ML API for CRM - Render Deployment

خدمة Machine Learning API للـ CRM، مُعدّة للعمل على Render.

## 🚀 البداية السريعة

لنشر سريع في 5 دقائق، راجع: **[QUICK_START.md](QUICK_START.md)**

للدليل الشامل بالعربية خطوة بخطوة: **[RENDER_DEPLOYMENT_GUIDE_AR.md](RENDER_DEPLOYMENT_GUIDE_AR.md)**

---

## 📋 المتطلبات

- Python 3.8+
- حساب Render (مجاني أو مدفوع)
- حساب GitHub

---

## 🔀 اختيار الإصدار

### خيار 1: Flask (الموجود حالياً)
- ✅ `app.py` - Flask application
- ✅ `requirements.txt`
- ✅ `Procfile` - يستخدم gunicorn

### خيار 2: FastAPI (جديد - موصى به)
- ✅ `app_fastapi.py` - FastAPI application
- ✅ `requirements_fastapi.txt`
- ✅ `Procfile_fastapi` - يستخدم uvicorn
- ✅ **مميزات**: واجهة تفاعلية `/docs`، أداء أفضل، async support

**لتبديل إلى FastAPI:**
```bash
# Windows PowerShell
Rename-Item app_fastapi.py app.py
Rename-Item requirements_fastapi.txt requirements.txt
Rename-Item Procfile_fastapi Procfile
```

---

## 🚀 خطوات النشر على Render

### 1️⃣ إعداد المستودع

1. ارفع محتويات مجلد `ml-api/` إلى GitHub repository
2. تأكد من وجود جميع ملفات النماذج (`.pkl`) في المجلدات:
   - `Lead_scoring/`
   - `Sales_forecasting/`
   - `Customer_segmentation/`

### 2️⃣ إنشاء خدمة جديدة على Render

1. سجل الدخول إلى [Render](https://render.com)
2. اضغط على **New +** → **Web Service**
3. اختر المستودع الخاص بك

### 3️⃣ إعدادات الخدمة

**Basic Settings:**
- **Name**: `crm-ml-api` (أو أي اسم تفضله)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: 
  - Flask: `gunicorn app:app --host 0.0.0.0 --port $PORT`
  - FastAPI: `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- لا حاجة لإعدادات خاصة
- Render سيستخدم `PORT` environment variable تلقائياً

### 4️⃣ رفع ملفات النماذج

**خيار 1: رفع مع الكود** (موصى به)
- ارفع مجلدات النماذج (`Lead_scoring/`, `Sales_forecasting/`, `Customer_segmentation/`) مع الكود

**خيار 2: استخدام Render Disk** (للخطط المدفوعة)
- يمكنك تخزين النماذج على Render Disk

**خيار 3: استخدام Cloud Storage**
- ارفع النماذج إلى AWS S3 أو Google Cloud Storage
- حدّث الكود لتحميل النماذج من Cloud Storage

### 5️⃣ الحصول على الرابط

بعد النشر الناجح، ستحصل على رابط مثل:
```
https://crm-ml-api.onrender.com
```

**مهم**: احفظ هذا الرابط لتحديثه في `crm-frontend/js/api-client.js`

---

## 📁 هيكل الملفات

```
ml-api/
├── app.py                    # Flask application (الموجود)
├── app_fastapi.py           # FastAPI application (الجديد)
├── Procfile                 # Flask deployment
├── Procfile_fastapi         # FastAPI deployment
├── requirements.txt         # Flask dependencies
├── requirements_fastapi.txt # FastAPI dependencies
├── README.md                # هذا الملف
├── QUICK_START.md           # دليل سريع
├── RENDER_DEPLOYMENT_GUIDE_AR.md  # دليل شامل بالعربية
├── Lead_scoring/            # مجلد نموذج Lead Scoring
│   ├── lead_scoring_model.pkl
│   ├── le_source.pkl
│   └── le_agent.pkl
├── Sales_forecasting/       # مجلد نموذج Sales Forecasting
│   └── sales_forecasting_model.pkl
└── Customer_segmentation/   # مجلد نموذج Customer Segmentation
    ├── customer_segmentation_model.pkl
    └── customer_segmentation_scaler.pkl
```

---

## 🔗 API Endpoints

### Health Check
```
GET /
GET /api/health
```
يرجع حالة API والنماذج المحملة

### Lead Scoring
```
POST /api/lead-scoring
```
Body:
```json
{
  "lead": {
    "id": 1,
    "name": "خالد العمري",
    "source": "الموقع الإلكتروني",
    "agent": "أحمد محمود",
    "tags": ["VIP"],
    "createdAt": "2025-10-15",
    "budget": 2500000
  }
}
```

### Sales Forecast
```
POST /api/sales-forecast
```
Body:
```json
{
  "start_date": "2025-12-01",
  "end_date": "2025-12-31",
  "avg_transactions": 5
}
```

### Customer Segmentation
```
POST /api/customer-segment
```
Body:
```json
{
  "customer": {
    "recency": 15,
    "frequency": 5,
    "monetary": 500000,
    "lead_count": 3,
    "avg_budget": 2000000
  }
}
```

### Batch Lead Scoring
```
POST /api/batch-lead-scoring
```
Body:
```json
{
  "leads": [
    { /* lead 1 */ },
    { /* lead 2 */ }
  ]
}
```

**FastAPI فقط:** افتح `/docs` لواجهة تفاعلية لاختبار جميع الـ Endpoints!

---

## 🔧 التطوير المحلي

### تشغيل محلياً (Flask)

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل التطبيق
python app.py
```

### تشغيل محلياً (FastAPI)

```bash
# تثبيت المكتبات
pip install -r requirements_fastapi.txt

# تشغيل التطبيق
python app_fastapi.py
# أو
uvicorn app_fastapi:app --reload
```

التطبيق سيعمل على `http://localhost:8000`

---

## 📊 مراقبة الأداء

Render يوفر:
- **Logs**: عرض السجلات مباشرة من Dashboard
- **Metrics**: مراقبة الأداء والذاكرة
- **Alerts**: تنبيهات عند حدوث مشاكل

---

## ⚠️ ملاحظات مهمة

1. **Sleep Mode**: في الخطة المجانية، الخدمة تدخل في وضع السكون بعد 15 دقيقة من عدم الاستخدام
   - الطلب الأول قد يستغرق 30-60 ثانية للاستيقاظ
   - للحل: استخدم Render Pro أو أضف cron job للـ ping

2. **Memory**: تأكد من أن حجم النماذج لا يتجاوز حدود الذاكرة (512MB في الخطة المجانية)

3. **Cold Start**: عند استخدام الخطة المجانية، قد يستغرق تحميل النماذج وقتاً أطول في البداية

---

## 🔄 تحديث النماذج

عند تحديث النماذج:
1. ارفع النماذج الجديدة إلى المستودع
2. أعد نشر الخدمة على Render
3. النماذج ستُحمّل تلقائياً عند إعادة التشغيل

---

## 🐛 استكشاف الأخطاء

### خطأ "Model not loaded"
- تحقق من وجود ملفات `.pkl` في المجلدات الصحيحة
- راجع Logs في Render Dashboard

### خطأ في Memory
- قلل حجم النماذج
- استخدم خطة أعلى من Render

### الخدمة لا تستجيب
- تحقق من Logs
- تأكد من أن `Procfile` صحيح
- جرب Health Check endpoint

---

## 📞 الدعم

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 💰 التكلفة

- **Free Plan**: مجاني مع قيود (Sleep mode بعد 15 دقيقة)
- **Starter Plan**: $7/شهر (دون Sleep mode)
- **Professional Plan**: $25/شهر (أداء أفضل)

---

## ✅ قائمة التحقق

- [ ] ✅ تم نسخ ملفات النماذج
- [ ] ✅ تم رفع الكود على GitHub
- [ ] ✅ تم إنشاء Web Service على Render
- [ ] ✅ تم النشر بنجاح
- [ ] ✅ تم اختبار `/api/health`
- [ ] ✅ تم تحديث رابط ML API في CRM
- [ ] ✅ جميع النماذج محملة بشكل صحيح

---

## 🎉 جاهز للاستخدام!

بعد إكمال جميع الخطوات، ML API جاهز للاستخدام من CRM الخاص بك! 🚀
