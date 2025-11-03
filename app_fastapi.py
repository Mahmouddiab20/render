"""
ML API for CRM - Render Deployment (FastAPI Version)
تطبيق FastAPI لتوفير خدمات Machine Learning للـCRM على Render
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = FastAPI(
    title="Sawaed CRM ML API",
    description="Machine Learning API للـ CRM",
    version="1.0.0"
)

# السماح بالـ CORS للطلبات من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# مسارات النماذج - Render يستخدم مسار ثابت
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# تحميل النماذج
lead_scoring_model = None
lead_scoring_le_source = None
lead_scoring_le_agent = None
sales_forecasting_model = None
customer_segmentation_model = None
customer_segmentation_scaler = None

def load_models():
    """تحميل جميع النماذج"""
    global lead_scoring_model, lead_scoring_le_source, lead_scoring_le_agent
    global sales_forecasting_model, customer_segmentation_model, customer_segmentation_scaler
    
    try:
        # Lead Scoring
        lead_model_path = os.path.join(MODELS_DIR, 'Lead_scoring', 'lead_scoring_model.pkl')
        if os.path.exists(lead_model_path):
            lead_scoring_model = joblib.load(lead_model_path)
            lead_scoring_le_source = joblib.load(os.path.join(MODELS_DIR, 'Lead_scoring', 'le_source.pkl'))
            lead_scoring_le_agent = joblib.load(os.path.join(MODELS_DIR, 'Lead_scoring', 'le_agent.pkl'))
            print("✅ تم تحميل Lead Scoring Model")
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم تحميل Lead Scoring Model: {e}")
    
    try:
        # Sales Forecasting
        sales_model_path = os.path.join(MODELS_DIR, 'Sales_forecasting', 'sales_forecasting_model.pkl')
        if os.path.exists(sales_model_path):
            sales_forecasting_model = joblib.load(sales_model_path)
            print("✅ تم تحميل Sales Forecasting Model")
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم تحميل Sales Forecasting Model: {e}")
    
    try:
        # Customer Segmentation
        seg_model_path = os.path.join(MODELS_DIR, 'Customer_segmentation', 'customer_segmentation_model.pkl')
        if os.path.exists(seg_model_path):
            customer_segmentation_model = joblib.load(seg_model_path)
            customer_segmentation_scaler = joblib.load(os.path.join(MODELS_DIR, 'Customer_segmentation', 'customer_segmentation_scaler.pkl'))
            print("✅ تم تحميل Customer Segmentation Model")
    except Exception as e:
        print(f"⚠️  تحذير: لم يتم تحميل Customer Segmentation Model: {e}")

# === Pydantic Models للـ Request/Response ===

class Lead(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    source: Optional[str] = "الموقع الإلكتروني"
    agent: Optional[str] = "غير محدد"
    tags: Optional[List[str]] = []
    createdAt: Optional[str] = None
    budget: Optional[float] = 0

class LeadScoringRequest(BaseModel):
    lead: Lead

class SalesForecastRequest(BaseModel):
    start_date: str
    end_date: str
    avg_transactions: Optional[int] = 5

class Customer(BaseModel):
    recency: Optional[int] = 30
    frequency: Optional[int] = 1
    monetary: Optional[float] = 0
    lead_count: Optional[int] = 1
    avg_budget: Optional[float] = 0

class CustomerSegmentRequest(BaseModel):
    customer: Customer

class BatchLeadScoringRequest(BaseModel):
    leads: List[Lead]

# === API Endpoints ===

@app.get("/")
async def home():
    """الصفحة الرئيسية"""
    return {
        "message": "Sawaed CRM ML API is running!",
        "status": "ok",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs",
            "lead_scoring": "/api/lead-scoring",
            "sales_forecast": "/api/sales-forecast",
            "customer_segment": "/api/customer-segment",
            "batch_lead_scoring": "/api/batch-lead-scoring"
        }
    }

@app.get("/api/health")
async def health_check():
    """فحص حالة API"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "lead_scoring": lead_scoring_model is not None,
            "sales_forecasting": sales_forecasting_model is not None,
            "customer_segmentation": customer_segmentation_model is not None
        }
    }

@app.post("/api/lead-scoring")
async def predict_lead_score(request: LeadScoringRequest):
    """التنبؤ بدرجة العميل"""
    if lead_scoring_model is None:
        raise HTTPException(status_code=500, detail="Lead Scoring model not loaded")
    
    try:
        lead = request.lead
        
        # تحضير البيانات
        source = lead.source or "الموقع الإلكتروني"
        agent = lead.agent or "غير محدد"
        tags = lead.tags or []
        createdAt = lead.createdAt or datetime.now().strftime('%Y-%m-%d')
        budget = lead.budget or 0
        
        # حساب الأيام منذ الإنشاء
        try:
            created_date = pd.to_datetime(createdAt)
            days_since_created = (pd.Timestamp.now() - created_date).days
        except:
            days_since_created = 0
        
        # ترميز
        try:
            source_encoded = lead_scoring_le_source.transform([source])[0]
        except:
            source_encoded = 0
        
        try:
            agent_encoded = lead_scoring_le_agent.transform([agent])[0]
        except:
            agent_encoded = 0
        
        tags_count = len(tags) if isinstance(tags, list) else 0
        
        # التنبؤ
        features = np.array([[source_encoded, agent_encoded, tags_count, days_since_created, float(budget)]])
        score = lead_scoring_model.predict_proba(features)[0][1] * 100
        
        return {
            "success": True,
            "lead_score": round(score, 2),
            "priority": "High" if score > 70 else "Medium" if score > 40 else "Low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales-forecast")
async def predict_sales(request: SalesForecastRequest):
    """التنبؤ بالمبيعات"""
    if sales_forecasting_model is None:
        raise HTTPException(status_code=500, detail="Sales Forecasting model not loaded")
    
    try:
        start_date = request.start_date or (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = request.end_date or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        avg_transactions = request.avg_transactions or 5
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        predictions = []
        
        for date in dates:
            features = pd.DataFrame({
                'year': [date.year],
                'month': [date.month],
                'day': [date.day],
                'week': [date.isocalendar().week],
                'weekday': [date.weekday()],
                'quarter': [date.quarter],
                'transaction_count': [avg_transactions],
                'sales_7day_avg': [0],
                'sales_30day_avg': [0]
            })
            
            pred = sales_forecasting_model.predict(features)[0]
            predictions.append({
                "date": date.strftime('%Y-%m-%d'),
                "predicted_sales": round(max(0, pred), 2)
            })
        
        total_forecast = sum(p['predicted_sales'] for p in predictions)
        
        return {
            "success": True,
            "predictions": predictions,
            "total_forecast": round(total_forecast, 2),
            "average_daily": round(total_forecast / len(predictions), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customer-segment")
async def predict_segment(request: CustomerSegmentRequest):
    """التنبؤ بقسم العميل"""
    if customer_segmentation_model is None:
        raise HTTPException(status_code=500, detail="Customer Segmentation model not loaded")
    
    try:
        customer = request.customer
        
        # استخراج الميزات
        recency = customer.recency or 30
        frequency = customer.frequency or 1
        monetary = customer.monetary or 0
        lead_count = customer.lead_count or 1
        avg_budget = customer.avg_budget or 0
        
        features = np.array([[recency, frequency, monetary, lead_count, avg_budget]])
        features_scaled = customer_segmentation_scaler.transform(features)
        
        segment = customer_segmentation_model.predict(features_scaled)[0]
        
        segment_names = {
            0: "Bronze",
            1: "Silver",
            2: "Gold",
            3: "Platinum"
        }
        
        return {
            "success": True,
            "segment": int(segment),
            "segment_name": segment_names.get(int(segment), "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch-lead-scoring")
async def batch_lead_scoring(request: BatchLeadScoringRequest):
    """التنبؤ بدرجة عدة عملاء دفعة واحدة"""
    if lead_scoring_model is None:
        raise HTTPException(status_code=500, detail="Lead Scoring model not loaded")
    
    try:
        leads = request.leads
        results = []
        
        for lead in leads:
            try:
                source = lead.source or "الموقع الإلكتروني"
                agent = lead.agent or "غير محدد"
                tags = lead.tags or []
                createdAt = lead.createdAt or datetime.now().strftime('%Y-%m-%d')
                budget = lead.budget or 0
                
                try:
                    created_date = pd.to_datetime(createdAt)
                    days_since_created = (pd.Timestamp.now() - created_date).days
                except:
                    days_since_created = 0
                
                try:
                    source_encoded = lead_scoring_le_source.transform([source])[0]
                except:
                    source_encoded = 0
                
                try:
                    agent_encoded = lead_scoring_le_agent.transform([agent])[0]
                except:
                    agent_encoded = 0
                
                tags_count = len(tags) if isinstance(tags, list) else 0
                
                features = np.array([[source_encoded, agent_encoded, tags_count, days_since_created, float(budget)]])
                score = lead_scoring_model.predict_proba(features)[0][1] * 100
                
                results.append({
                    "lead_id": lead.id,
                    "name": lead.name,
                    "lead_score": round(score, 2),
                    "priority": "High" if score > 70 else "Medium" if score > 40 else "Low"
                })
            except Exception as e:
                results.append({
                    "lead_id": lead.id,
                    "name": lead.name,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# تحميل النماذج عند بدء التطبيق
@app.on_event("startup")
async def startup_event():
    print("🚀 جارٍ تحميل النماذج...")
    load_models()
    print("✅ API جاهز!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

