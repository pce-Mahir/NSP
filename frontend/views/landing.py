import streamlit as st


def render():
    
    # Landing page CSS
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
        }
        .main-header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>CareerPath AI</h1>
        <h3>AI-Enhanced Career Guidance System for Personalized Career Pathways</h3>
        <p>Score your resume, then let Gemini recommend pathways, learning plans, and interview prep</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Call-to-Action Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Analyzing Your Resume", use_container_width=True, type="primary"):
            st.session_state.current_view = 'scorer'
            st.rerun()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧭 Career Pathways", use_container_width=True):
            st.session_state.current_view = 'pathways'
            st.rerun()
    with c2:
        if st.button("🗺️ Learning Roadmap", use_container_width=True):
            st.session_state.current_view = 'roadmap'
            st.rerun()
    with c3:
        if st.button("🎤 Interview Coach", use_container_width=True):
            st.session_state.current_view = 'interview'
            st.rerun()
    
    st.markdown("---")
    
    # Features Overview
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Comprehensive Scoring
        Get detailed scores across 5 key dimensions:
        - Formatting (20%)
        - Keywords & Skills (25%)
        - Content Quality (25%)
        - Skill Validation (15%)
        - ATS Compatibility (15%)
        """)
    
    with col2:
        st.markdown("""
        ### 🔍 Skill Validation
        Verify that your claimed skills are demonstrated in your projects and experience using AI-powered semantic analysis.
        
        **No more empty claims!**
        """)
    
    with col3:
        st.markdown("""
        ### 🧭 Personalized Pathways
        Gemini turns your skills and goals into career paths, a 90-day learning roadmap, and interview practice.
        
        **Guidance after the score**
        """)
    
    st.markdown("---")
    
    # How It Works
    st.markdown("## 🚀 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 1️⃣ Upload Your Resume
        Support for PDF, DOC, and DOCX formats
        """)
    
    with col2:
        st.markdown("""
        #### 2️⃣ AI Analysis
        Our local AI models analyze your resume across multiple dimensions
        """)
    
    with col3:
        st.markdown("""
        #### 3️⃣ Get Actionable Feedback
        Receive detailed recommendations to improve your resume
        """)
