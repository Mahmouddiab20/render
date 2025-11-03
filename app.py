"""
ML API for CRM - Render Deployment
تطبيق Flask لتوفير خدمات Machine Learning للـCRM على Render
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # للسماح بالطلبات من أي مصدر

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

@app.route('/', methods=['GET'])
def index():
    """الصفحة الرئيسية"""
    return jsonify({
        'message': 'ML API for CRM',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'lead_scoring': '/api/lead-scoring',
            'sales_forecast': '/api/sales-forecast',
            'customer_segment': '/api/customer-segment',
            'batch_lead_scoring': '/api/batch-lead-scoring'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص حالة API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': {
            'lead_scoring': lead_scoring_model is not None,
            'sales_forecasting': sales_forecasting_model is not None,
            'customer_segmentation': customer_segmentation_model is not None
        }
    })

@app.route('/api/lead-scoring', methods=['POST'])
def predict_lead_score():
    """التنبؤ بدرجة العميل"""
    if lead_scoring_model is None:
        return jsonify({'error': 'Lead Scoring model not loaded'}), 500
    
    try:
        data = request.json
        lead = data.get('lead', {})
        
        # تحضير البيانات
        source = lead.get('source', 'الموقع الإلكتروني')
        agent = lead.get('agent', 'غير محدد')
        tags = lead.get('tags', [])
        createdAt = lead.get('createdAt', datetime.now().strftime('%Y-%m-%d'))
        budget = lead.get('budget', 0)
        
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
        
        return jsonify({
            'success': True,
            'lead_score': round(score, 2),
            'priority': 'High' if score > 70 else 'Medium' if score > 40 else 'Low'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales-forecast', methods=['POST'])
def predict_sales():
    """التنبؤ بالمبيعات"""
    if sales_forecasting_model is None:
        return jsonify({'error': 'Sales Forecasting model not loaded'}), 500
    
    try:
        data = request.json
        start_date = data.get('start_date', (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        avg_transactions = data.get('avg_transactions', 5)
        
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
                'date': date.strftime('%Y-%m-%d'),
                'predicted_sales': round(max(0, pred), 2)
            })
        
        total_forecast = sum(p['predicted_sales'] for p in predictions)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'total_forecast': round(total_forecast, 2),
            'average_daily': round(total_forecast / len(predictions), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-segment', methods=['POST'])
def predict_segment():
    """التنبؤ بقسم العميل"""
    if customer_segmentation_model is None:
        return jsonify({'error': 'Customer Segmentation model not loaded'}), 500
    
    try:
        data = request.json
        customer = data.get('customer', {})
        
        # استخراج الميزات
        recency = customer.get('recency', 30)
        frequency = customer.get('frequency', 1)
        monetary = customer.get('monetary', 0)
        lead_count = customer.get('lead_count', 1)
        avg_budget = customer.get('avg_budget', 0)
        
        features = np.array([[recency, frequency, monetary, lead_count, avg_budget]])
        features_scaled = customer_segmentation_scaler.transform(features)
        
        segment = customer_segmentation_model.predict(features_scaled)[0]
        
        segment_names = {
            0: 'Bronze',
            1: 'Silver',
            2: 'Gold',
            3: 'Platinum'
        }
        
        return jsonify({
            'success': True,
            'segment': int(segment),
            'segment_name': segment_names.get(int(segment), 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-lead-scoring', methods=['POST'])
def batch_lead_scoring():
    """التنبؤ بدرجة عدة عملاء دفعة واحدة"""
    if lead_scoring_model is None:
        return jsonify({'error': 'Lead Scoring model not loaded'}), 500
    
    try:
        data = request.json
        leads = data.get('leads', [])
        
        results = []
        for lead in leads:
            try:
                source = lead.get('source', 'الموقع الإلكتروني')
                agent = lead.get('agent', 'غير محدد')
                tags = lead.get('tags', [])
                createdAt = lead.get('createdAt', datetime.now().strftime('%Y-%m-%d'))
                budget = lead.get('budget', 0)
                
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
                    'lead_id': lead.get('id'),
                    'name': lead.get('name'),
                    'lead_score': round(score, 2),
                    'priority': 'High' if score > 70 else 'Medium' if score > 40 else 'Low'
                })
            except Exception as e:
                results.append({
                    'lead_id': lead.get('id'),
                    'name': lead.get('name'),
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# تحميل النماذج عند بدء التطبيق
if __name__ == '__main__':
    print("🚀 جارٍ تحميل النماذج...")
    load_models()
    print("\n✅ API جاهز!")
    
    # على Render، سيستخدم PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # عند استخدام gunicorn على Render
    load_models()

