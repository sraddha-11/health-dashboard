import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Health Analytics Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 32px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("💊 Health Analytics Dashboard")
st.markdown("**Ages 35–55 | Obesity & Overweight Management**")
st.markdown("---")

# ============================================================================
# LOAD & CACHE DATA
# ============================================================================

@st.cache_data
def load_data():
    """Load and cache the processed health data"""
    try:
        df = pd.read_csv('PROCESSED_HEALTH_DATA.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ PROCESSED_HEALTH_DATA.csv not found. Please upload the CSV file.")
        return None

df = load_data()

if df is None:
    st.stop()

# ============================================================================
# SIDEBAR: FILTERS
# ============================================================================

st.sidebar.header("🔍 Filters")

# Age range filter
age_range = st.sidebar.slider(
    "Age Range",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(int(df['age'].min()), int(df['age'].max())),
    step=1
)

# BMI category filter
bmi_categories = st.sidebar.multiselect(
    "BMI Category",
    options=df['BMI_category'].dropna().unique(),
    default=df['BMI_category'].dropna().unique()
)

# Risk tier filter
risk_tiers = st.sidebar.multiselect(
    "Risk Tier",
    options=df['Risk_Tier'].unique(),
    default=df['Risk_Tier'].unique()
)

# Gender filter (if available)
if 'sex' in df.columns:
    genders = st.sidebar.multiselect(
        "Gender",
        options=df['sex'].unique(),
        default=df['sex'].unique()
    )
else:
    genders = df.get('sex', pd.Series(['All'])).unique()

# ============================================================================
# APPLY FILTERS
# ============================================================================

df_filtered = df[
    (df['age'] >= age_range[0]) & 
    (df['age'] <= age_range[1]) &
    (df['BMI_category'].isin(bmi_categories)) &
    (df['Risk_Tier'].isin(risk_tiers))
]

if 'sex' in df.columns:
    df_filtered = df_filtered[df_filtered['sex'].isin(genders)]

# Show filter results
st.sidebar.info(f"📊 Showing {len(df_filtered)} of {len(df)} patients")

# ============================================================================
# KEY METRICS
# ============================================================================

st.header("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Patients",
        value=len(df_filtered),
        delta=f"{len(df_filtered) / len(df) * 100:.0f}% of cohort"
    )

with col2:
    avg_bmi = df_filtered['BMI'].mean()
    st.metric(
        label="Average BMI",
        value=f"{avg_bmi:.1f}",
        delta=f"Range: {df_filtered['BMI'].min():.1f} - {df_filtered['BMI'].max():.1f}"
    )

with col3:
    mets_prev = df_filtered['Metabolic_Syndrome_Flag'].sum() / len(df_filtered) * 100
    st.metric(
        label="Metabolic Syndrome",
        value=f"{mets_prev:.0f}%",
        delta=f"{int(df_filtered['Metabolic_Syndrome_Flag'].sum())} patients"
    )

with col4:
    avg_activity = df_filtered['Activity_Score'].mean()
    st.metric(
        label="Avg Activity Score",
        value=f"{avg_activity:.1f}",
        delta="0-100 scale"
    )

st.markdown("---")

# ============================================================================
# VISUALIZATIONS - ROW 1
# ============================================================================

st.header("📊 Data Visualizations")

col1, col2 = st.columns(2)

# BMI Distribution
with col1:
    st.subheader("BMI Distribution by Category")
    bmi_counts = df_filtered['BMI_category'].value_counts()
    colors = {
        'Normal': '#10b981',
        'Overweight': '#f59e0b',
        'Obese_I': '#ef4444',
        'Obese_II': '#dc2626',
        'Obese_III': '#7c2d12'
    }
    fig_bmi = go.Figure(data=[
        go.Bar(
            x=bmi_counts.index,
            y=bmi_counts.values,
            marker_color=[colors.get(cat, '#999999') for cat in bmi_counts.index],
            text=bmi_counts.values,
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    fig_bmi.update_layout(
        title="",
        xaxis_title="BMI Category",
        yaxis_title="Number of Patients",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_bmi, use_container_width=True)

# Risk Tier Distribution
with col2:
    st.subheader("Risk Stratification")
    risk_counts = df_filtered['Risk_Tier'].value_counts()
    risk_colors = {
        'Low_Risk': '#10b981',
        'Moderate_Risk': '#f59e0b',
        'High_Risk': '#ef4444',
        'Critical_Risk': '#7c2d12'
    }
    fig_risk = go.Figure(data=[
        go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            marker_colors=[risk_colors.get(tier, '#999999') for tier in risk_counts.index],
            hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>%{percent}<extra></extra>',
            textposition='inside',
            textinfo='label+percent'
        )
    ])
    fig_risk.update_layout(height=400)
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATIONS - ROW 2
# ============================================================================

col1, col2 = st.columns(2)

# Age Distribution
with col1:
    st.subheader("Age Distribution")
    fig_age = go.Figure()
    fig_age.add_trace(go.Histogram(
        x=df_filtered['age'],
        nbinsx=10,
        marker_color='#3b82f6',
        name='Patients',
        hovertemplate='Age: %{x}<br>Count: %{y}<extra></extra>'
    ))
    fig_age.update_layout(
        title="",
        xaxis_title="Age (years)",
        yaxis_title="Number of Patients",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_age, use_container_width=True)

# BMI vs Activity Score
with col2:
    st.subheader("BMI vs Activity Engagement")
    fig_scatter = go.Figure()
    for risk_tier in df_filtered['Risk_Tier'].unique():
        df_tier = df_filtered[df_filtered['Risk_Tier'] == risk_tier]
        fig_scatter.add_trace(go.Scatter(
            x=df_tier['BMI'],
            y=df_tier['Activity_Score'],
            mode='markers',
            name=risk_tier,
            marker=dict(
                size=8,
                color=risk_colors.get(risk_tier, '#999999'),
                opacity=0.7
            ),
            text=df_tier['patient_id'],
            hovertemplate='<b>%{text}</b><br>BMI: %{x:.1f}<br>Activity: %{y:.1f}<extra></extra>'
        ))
    fig_scatter.update_layout(
        title="",
        xaxis_title="BMI",
        yaxis_title="Activity Score (0-100)",
        height=400,
        hovermode='closest'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATIONS - ROW 3
# ============================================================================

col1, col2 = st.columns(2)

# Metabolic Health Indicators
with col1:
    st.subheader("HbA1c Status (Diabetes Risk)")
    hba1c_cats = df_filtered['HbA1c_category'].value_counts()
    hba1c_colors = {
        'Normal': '#10b981',
        'Prediabetic': '#f59e0b',
        'Diabetic': '#ef4444'
    }
    fig_hba1c = go.Figure(data=[
        go.Bar(
            y=hba1c_cats.index,
            x=hba1c_cats.values,
            orientation='h',
            marker_color=[hba1c_colors.get(cat, '#999999') for cat in hba1c_cats.index],
            text=hba1c_cats.values,
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Patients: %{x}<extra></extra>'
        )
    ])
    fig_hba1c.update_layout(
        title="",
        xaxis_title="Number of Patients",
        yaxis_title="",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_hba1c, use_container_width=True)

# Behavioral Metrics
with col2:
    st.subheader("Behavioral Health Scores")
    metrics_data = pd.DataFrame({
        'Metric': ['Activity\nScore', 'Diet\nCompliance', 'Sleep\nQuality'],
        'Average': [
            df_filtered['Activity_Score'].mean(),
            df_filtered['Diet_Compliance_%'].mean(),
            df_filtered['Sleep_Quality_Index'].mean()
        ]
    })
    fig_behav = go.Figure(data=[
        go.Bar(
            x=metrics_data['Metric'],
            y=metrics_data['Average'],
            marker_color=['#3b82f6', '#10b981', '#8b5cf6'],
            text=metrics_data['Average'].round(1),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}/100<extra></extra>'
        )
    ])
    fig_behav.update_layout(
        title="",
        yaxis_title="Score (0-100)",
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, 110])
    )
    st.plotly_chart(fig_behav, use_container_width=True)

st.markdown("---")

# ============================================================================
# DATA TABLE
# ============================================================================

st.header("📋 Patient Data Table")

# Select columns to display
display_cols = [
    'patient_id', 'age', 'sex', 'BMI', 'BMI_category', 'HbA1c', 'HbA1c_category',
    'Metabolic_Syndrome_Flag', 'Activity_Score', 'Sleep_Quality_Index',
    'Clinic_Attendance_Rate_%', 'Risk_Tier', 'data_quality_flag'
]

# Only show columns that exist
display_cols = [col for col in display_cols if col in df_filtered.columns]

# Format and display
df_display = df_filtered[display_cols].copy()
df_display = df_display.round(2)

st.dataframe(
    df_display,
    use_container_width=True,
    height=400,
    hide_index=True
)

# Download button
csv = df_display.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="health_analytics_export.csv",
    mime="text/csv"
)

st.markdown("---")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

st.header("📊 Summary Statistics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Clinical Indicators")
    summary_stats = f"""
    **BMI Statistics:**
    - Mean: {df_filtered['BMI'].mean():.1f}
    - Median: {df_filtered['BMI'].median():.1f}
    - Range: {df_filtered['BMI'].min():.1f} - {df_filtered['BMI'].max():.1f}
    
    **Metabolic Health:**
    - Avg HbA1c: {df_filtered['HbA1c'].mean():.1f}%
    - Metabolic Syndrome: {df_filtered['Metabolic_Syndrome_Flag'].sum() / len(df_filtered) * 100:.1f}%
    - Comorbidity Count (avg): {df_filtered['Comorbidity_Count'].mean():.1f}
    """
    st.markdown(summary_stats)

with col2:
    st.subheader("Engagement Metrics")
    engagement_stats = f"""
    **Activity & Lifestyle:**
    - Avg Activity Score: {df_filtered['Activity_Score'].mean():.1f}/100
    - Avg Diet Compliance: {df_filtered['Diet_Compliance_%'].mean():.1f}%
    - Avg Sleep Quality: {df_filtered['Sleep_Quality_Index'].mean():.1f}/100
    
    **Program Participation:**
    - Avg Clinic Attendance: {df_filtered['Clinic_Attendance_Rate_%'].mean():.1f}%
    - Avg Days in Program: {df_filtered['Days_in_Program'].mean():.0f}
    """
    st.markdown(engagement_stats)

st.markdown("---")

# ============================================================================
# RISK TIER EXPLANATIONS
# ============================================================================

st.header("🎯 Risk Stratification Explained")

risk_explanations = {
    'Low_Risk': {
        'color': '🟢',
        'description': 'Patients with BMI < 30 or well-controlled metabolic markers and high engagement. Good prognosis with standard monitoring.',
        'typical_scores': '0-3 points'
    },
    'Moderate_Risk': {
        'color': '🟡',
        'description': 'Patients with BMI 30-35 or emerging metabolic concerns. Require closer monitoring and regular interventions.',
        'typical_scores': '4-6 points'
    },
    'High_Risk': {
        'color': '🔴',
        'description': 'Patients with BMI 35+ or multiple comorbidities/metabolic syndrome. Need intensive program with frequent visits.',
        'typical_scores': '7-10 points'
    },
    'Critical_Risk': {
        'color': '⚫',
        'description': 'Patients with severe obesity (BMI > 40) or complex comorbidities. Require multi-disciplinary care and frequent monitoring.',
        'typical_scores': '>10 points'
    }
}

cols = st.columns(2)
for idx, (tier, info) in enumerate(risk_explanations.items()):
    with cols[idx % 2]:
        st.markdown(f"**{info['color']} {tier.replace('_', ' ')}**")
        st.markdown(f"{info['description']}")
        st.caption(f"Scoring: {info['typical_scores']}")

st.markdown("---")

# ============================================================================
# ABOUT & DOCUMENTATION
# ============================================================================

with st.expander("📖 About This Dashboard"):
    st.markdown("""
    ## Health Analytics Dashboard
    **Target Population:** Individuals aged 35-55 with obesity or overweight (BMI ≥ 25)
    
    ### Data Sources
    This dashboard integrates data from **5 sources**:
    
    1. **Hospital EHR** - Clinical metrics, lab results, diagnoses
    2. **Pharmacy** - Medication adherence, refill patterns
    3. **Gym/Fitness Systems** - Activity logs, visit frequency
    4. **Patient Surveys** - Lifestyle assessment, barriers to adherence
    5. **Wearables/Mobile Apps** - Steps, sleep, heart rate monitoring
    
    ### Feature Engineering
    The system creates **25+ features** across these categories:
    
    - **Body Composition** (6): BMI, Waist-Hip Ratio, Weight Change
    - **Metabolic Risk** (8): HbA1c, Glucose, Lipid Score, Metabolic Syndrome Flag
    - **Clinical** (5): Comorbidity Count, Medication Load
    - **Behavioral** (4): Activity Score, Diet Compliance, Sleep Quality
    - **Engagement** (2): Days in Program, Clinic Attendance Rate
    
    ### Data Preprocessing Pipeline
    
    1. **Standardization** - BP format (130/80), units, numeric types
    2. **Imputation** - Missing values (median by age, forward-fill)
    3. **Outlier Detection** - Flags extreme values (weight > 10kg change, BP > 220)
    4. **Deduplication** - Keeps best record per patient-visit by source priority
    5. **Temporal Alignment** - Joins multi-source data (±14 days to nearest visit)
    
    ### Risk Stratification Algorithm
    
    Patients are scored on:
    - BMI category (0-3 points)
    - Metabolic syndrome status (+2 points)
    - HbA1c level (+2 points if diabetic)
    - Comorbidity count (+1 per condition)
    - Engagement metrics (+1 if low activity, low attendance)
    
    **Total Score determines Risk Tier:**
    - **Low Risk**: 0-3 points
    - **Moderate Risk**: 4-6 points
    - **High Risk**: 7-10 points
    - **Critical Risk**: >10 points
    """)

with st.expander("🔧 Technical Details"):
    st.markdown(f"""
    ### Dataset Information
    - **Total Records:** {len(df)}
    - **Filtered Records:** {len(df_filtered)}
    - **Age Range:** {df['age'].min():.0f} - {df['age'].max():.0f} years
    - **BMI Range:** {df['BMI'].min():.1f} - {df['BMI'].max():.1f}
    
    ### Data Quality
    - Clean records: {(df['data_quality_flag'] == 'clean').sum()} ({(df['data_quality_flag'] == 'clean').sum() / len(df) * 100:.1f}%)
    - Flagged for review: {(df['data_quality_flag'] != 'clean').sum()} ({(df['data_quality_flag'] != 'clean').sum() / len(df) * 100:.1f}%)
    
    ### Distribution by Risk Tier
    {df['Risk_Tier'].value_counts().to_string()}
    """)

with st.expander("📚 Feature Definitions"):
    st.markdown("""
    ### Body Composition Features
    - **BMI** = weight(kg) / height(m)²
    - **BMI_category** = Classification (Normal/Overweight/Obese I-III)
    - **Waist_Hip_Ratio** = Waist circumference / Hip circumference
    
    ### Metabolic Risk Features
    - **HbA1c** = Glycated hemoglobin (3-month avg blood sugar)
    - **Glucose_category** = Normal (<100) / Impaired (100-125) / Diabetic (≥126)
    - **Lipid_Risk_Score** = Normalized composite of cholesterol, LDL, HDL, triglycerides
    - **Metabolic_Syndrome_Flag** = 1 if ≥3 of 5 NCEP criteria met
    
    ### Behavioral Features
    - **Activity_Score** = Composite (50% steps, 30% gym visits, 20% active minutes)
    - **Diet_Compliance_%** = % of days following meal plan
    - **Sleep_Quality_Index** = Normalized score (duration, efficiency, consistency)
    
    ### Clinical Features
    - **Comorbidity_Count** = Sum of HTN, diabetes, sleep apnea, GERD, osteoarthritis
    - **Clinic_Attendance_Rate_%** = % of scheduled visits attended
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p><strong>Health Analytics Dashboard</strong> | Ages 35-55 Weight Management Program</p>
    <p>Data Integration • Feature Engineering • Risk Stratification</p>
    <p>Built with Streamlit & Plotly | Data Science Ready</p>
</div>
""", unsafe_allow_html=True)
