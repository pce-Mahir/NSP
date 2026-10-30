import streamlit as st


def render():
    """Render the resources page"""
    
    st.title("📚 Resources & Tips")
    st.markdown("ATS resume advice plus how CareerPath AI uses Gemini for personalized pathways")
    
    # ATS Tips
    st.markdown("## 🎯 ATS Optimization Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ Do's
        - Use standard section headings
        - Include relevant keywords from job description
        - Use simple, clean formatting
        - List skills explicitly
        - Quantify achievements with numbers
        - Use standard fonts (Arial, Calibri, Times New Roman)
        - Save as PDF or DOCX
        """)
    
    with col2:
        st.markdown("""
        ### ❌ Don'ts
        - Avoid tables and text boxes
        - Don't use headers/footers for important info
        - Avoid images and graphics
        - Don't use unusual fonts
        - Avoid columns (use single column layout)
        - Don't keyword stuff
        - Avoid abbreviations without spelling out first
        """)
    
    st.markdown("---")
    
    # Common ATS Keywords
    st.markdown("## 🔑 Common ATS Keywords by Industry")
    
    tab1, tab2, tab3 = st.tabs(["💻 Tech", "💼 Business", "🎨 Creative"])
    
    with tab1:
        st.markdown("""
        **Software Development:**
        - Programming languages (Python, Java, JavaScript)
        - Frameworks (React, Django, Spring)
        - Tools (Git, Docker, Kubernetes)
        - Methodologies (Agile, Scrum, CI/CD)
        """)
    
    with tab2:
        st.markdown("""
        **Business & Management:**
        - Project management
        - Stakeholder engagement
        - Budget management
        - Strategic planning
        - Team leadership
        """)
    
    with tab3:
        st.markdown("""
        **Creative & Design:**
        - Adobe Creative Suite
        - UI/UX Design
        - Wireframing & Prototyping
        - Brand identity
        - Visual communication
        """)
    
    st.markdown("---")
    
    # Resume Templates
    st.markdown("## 📄 ATS-Friendly Resume Templates")
    st.info("Coming soon: Downloadable ATS-optimized resume templates")

    st.markdown("---")
    st.markdown("## 🧭 Using Gemini career guidance")
    st.markdown("""
    1. Score a resume so the app has your skills, experience, and projects.
    2. Open **Career Pathways** to see roles that fit you.
    3. Open **Learning Roadmap** for a 30/60/90-day skill plan.
    4. Practice with **Interview Coach**, then ask follow-ups in **Career Advisor**.
    """)
