"""
UI Theme Configuration
========================
CSS styling, color palette, and theme utilities for the Streamlit app.
"""


def get_custom_css() -> str:
    """Return custom CSS for the Streamlit app."""
    return """
    <style>
        /* === Global Styles === */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        .stApp {
            font-family: 'Inter', sans-serif;
        }

        /* === Sidebar Styling === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29 0%, #1a1a4e 50%, #24243e 100%);
        }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] .stMarkdown label,
        [data-testid="stSidebar"] .stRadio p,
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stRadio span,
        [data-testid="stSidebar"] .stRadio div {
            color: #ffffff !important;
        }

        /* === Metric Cards === */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 20px 24px;
            color: white;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
        }
        .metric-card .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 8px 0 4px 0;
        }
        .metric-card .metric-label {
            font-size: 0.85rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* === Card Variants === */
        .metric-card.critical {
            background: linear-gradient(135deg, #FF1744 0%, #D50000 100%);
            box-shadow: 0 8px 32px rgba(255, 23, 68, 0.25);
        }
        .metric-card.high {
            background: linear-gradient(135deg, #FF6D00 0%, #E65100 100%);
            box-shadow: 0 8px 32px rgba(255, 109, 0, 0.25);
        }
        .metric-card.medium {
            background: linear-gradient(135deg, #FFD600 0%, #F9A825 100%);
            box-shadow: 0 8px 32px rgba(255, 214, 0, 0.25);
            color: #333;
        }
        .metric-card.low {
            background: linear-gradient(135deg, #00C853 0%, #00E676 100%);
            box-shadow: 0 8px 32px rgba(0, 200, 83, 0.25);
        }

        /* === Status Badge === */
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            letter-spacing: 0.3px;
        }
        .status-badge.compliant {
            background: linear-gradient(135deg, #00C853, #69F0AE);
            color: #1B5E20;
        }
        .status-badge.warning {
            background: linear-gradient(135deg, #FFD600, #FFFF00);
            color: #E65100;
        }
        .status-badge.non-compliant {
            background: linear-gradient(135deg, #FF1744, #FF5252);
            color: white;
        }

        /* === Severity Badge === */
        .severity-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
        }
        .severity-badge.critical { background: #FF1744; color: white; }
        .severity-badge.high { background: #FF6D00; color: white; }
        .severity-badge.medium { background: #FFD600; color: #333; }
        .severity-badge.low { background: #00C853; color: white; }

        /* === Score Display === */
        .score-display {
            text-align: center;
            padding: 30px;
            border-radius: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .score-value {
            font-size: 4rem;
            font-weight: 700;
            line-height: 1;
        }
        .score-label {
            font-size: 1rem;
            color: #666;
            margin-top: 8px;
        }

        /* === Violation Card === */
        .violation-card {
            border-left: 4px solid;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
            background: #fafafa;
        }
        .violation-card.critical { border-color: #FF1744; background: #fff5f5; }
        .violation-card.high { border-color: #FF6D00; background: #fff8f0; }
        .violation-card.medium { border-color: #FFD600; background: #fffef0; }
        .violation-card.low { border-color: #00C853; background: #f0fff5; }

        /* === Progress Animation === */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .scanning-indicator {
            animation: pulse 1.5s ease-in-out infinite;
            color: #667eea;
            font-weight: 600;
        }

        /* === File Upload Area === */
        [data-testid="stFileUploader"] {
            border: 2px dashed #667eea;
            border-radius: 16px;
            padding: 20px;
            background: rgba(102, 126, 234, 0.05);
        }

        /* === Divider === */
        .gradient-divider {
            height: 3px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            border: none;
            border-radius: 2px;
            margin: 20px 0;
        }

        /* === Header === */
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px 30px;
            border-radius: 16px;
            color: white;
            margin-bottom: 24px;
        }
        .app-header h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
        }
        .app-header p {
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }

        /* === Hide default Streamlit footer and menu === */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """
