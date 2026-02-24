import streamlit as st
import os
import sys
import io
from PIL import Image

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from ensemble_model import predict_image
    from database import init_db, get_history
except ImportError as e:
    st.error(f"Failed to import core logic: {e}")
    st.stop()

# Page Config
st.set_page_config(
    page_title="Pulsar Medical AI | Ensemble Diagnosis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: radial-gradient(circle at top right, #0F172A, #020617);
        color: #F8FAFC;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 1rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(14, 165, 233, 0.4);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 2rem;
        padding: 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card {
        background: rgba(14, 165, 233, 0.1);
        border-right: 4px solid #38BDF8;
        padding: 1.5rem;
        border-radius: 1rem;
    }
    
    h1, h2, h3 {
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sidebar .sidebar-content {
        background: #020617;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
init_db()

# Header Section
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem;'>Precision <span class='gradient-text'>Scanning</span></h1>
    <p style='color: #94A3B8; font-size: 1.2rem;'>Multi-Modality Deep Ensemble Interpretation for Bone, Chest, and Brain Analysis</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🧬 Neural Input")
    uploaded_file = st.file_uploader("Upload Image (X-Ray, CT, MRI)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption="Target Scan Preview")
        
        if st.button("Execute Ensemble Scan"):
            with st.spinner("Analyzing neural patterns..."):
                # Convert to bytes for predict_image
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Run Prediction
                result = predict_image(io.BytesIO(img_byte_arr))
                st.session_state.result = result
                st.session_state.analysis_done = True
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        res = st.session_state.result
        report = res['report']
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem;">
                <div>
                    <p style="color: #38BDF8; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 0.2rem;">Radiology Impression</p>
                    <h2 style="font-size: 3rem; margin: 0; color: {'#4ADE80' if res['condition'] == 'Normal' else '#F87171'};">
                        {res['condition']}
                    </h2>
                </div>
                <div class="metric-card">
                    <p style="color: #38BDF8; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">AI Confidence</p>
                    <span style="font-size: 2rem; font-weight: 800;">{res['confidence']*100:.1f}%</span>
                </div>
            </div>
            
            <div style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(255,255,255,0.02); border-radius: 1rem; border: 1px solid rgba(255,255,255,0.05);">
                <h4 style="color: #38BDF8; margin-bottom: 1rem; font-size: 0.9rem;">STRUCTURAL FINDINGS</h4>
                <ul style="margin: 0; padding-left: 1.2rem; color: #CBD5E1; line-height: 1.6;">
                    {"".join([f"<li>{f}</li>" for f in report['clinical_findings']])}
                </ul>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="padding: 1.5rem; background: rgba(14, 165, 233, 0.05); border-radius: 1rem; border-left: 4px solid #38BDF8;">
                    <h4 style="color: #38BDF8; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 0.5rem;">Clinical Severity</h4>
                    <p style="font-weight: 800; margin: 0;">{report['severity']}</p>
                </div>
                <div style="padding: 1.5rem; background: rgba(14, 165, 233, 0.05); border-radius: 1rem; border-left: 4px solid #38BDF8;">
                    <h4 style="color: #38BDF8; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 0.5rem;">System Modality</h4>
                    <p style="font-weight: 800; margin: 0;">{res['modality']}</p>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem;">
                <h4 style="color: #38BDF8; font-size: 0.9rem; margin-bottom: 0.5rem;">RECOMMENDATION</h4>
                <p style="font-style: italic; color: #94A3B8;">{report['recommendation']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ensemble Breakdown
        st.markdown("### 🧬 Neural Consensus Matrix")
        cols = st.columns(len(res['ensemble_breakdown']))
        for i, m in enumerate(res['ensemble_breakdown']):
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 1rem; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem; text-align: center;">
                    <p style="color: #38BDF8; font-size: 0.7rem; font-weight: 800; margin-bottom: 0.5rem;">{m['model']}</p>
                    <p style="font-size: 0.9rem; font-weight: 800; margin: 0;">{m['prediction']}</p>
                    <p style="font-size: 0.7rem; color: #64748B;">{m['confidence']*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; opacity: 0.5;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🔬</div>
            <h3>Waiting for Analysis</h3>
            <p>Upload a scan and execute the ensemble engine to see detailed diagnostic reports.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.8rem; padding: 2rem;'>
    <p>Pulsar Medical AI Hub | Powered by Deep Ensemble Neural Networks</p>
    <p>© 2026 Advanced Diagnostic Systems</p>
</div>
""", unsafe_allow_html=True)
