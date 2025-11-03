# ⚡ Quick Start - نشر سريع على Render

## 🚀 خطوات سريعة (5 دقائق)

### 1️⃣ نسخ النماذج
```powershell
Copy-Item "..\Elzoboon-CRM\Lead_scoring" -Destination "." -Recurse
Copy-Item "..\Elzoboon-CRM\Sales_forecasting" -Destination "." -Recurse
Copy-Item "..\Elzoboon-CRM\Customer_segmentation" -Destination "." -Recurse
```

### 2️⃣ رفع على GitHub
```bash
git init
git add .
git commit -m "ML API for CRM"
git remote add origin https://github.com/YOUR_USERNAME/crm-ml-api.git
git push -u origin main
```

### 3️⃣ نشر على Render
1. [render.com](https://render.com) → New Web Service
2. اختر GitHub repository
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: 
   - Flask: `gunicorn app:app --host 0.0.0.0 --port $PORT`
   - FastAPI: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Deploy ✅

### 4️⃣ تحديث CRM
افتح `crm-frontend/js/api-client.js`:
```javascript
const ML_API_URL = 'https://YOUR_APP_NAME.onrender.com/api';
```

## ✅ اختبار سريع
افتح في المتصفح:
```
https://YOUR_APP_NAME.onrender.com/api/health
```

يجب أن ترى:
```json
{"status": "ok", "models_loaded": {...}}
```

---

📖 **للمزيد من التفاصيل**: راجع `RENDER_DEPLOYMENT_GUIDE_AR.md`

