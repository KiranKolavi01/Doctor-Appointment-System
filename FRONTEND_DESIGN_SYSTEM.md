## SECTION 1 — FONTS

- Every Google Fonts @import URL:
  - `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap`
  - `https://fonts.googleapis.com/css2?family=Michroma&display=swap`
  - `https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap`

- Heading font: Montserrat
  - Weight: 600
  - Style: normal
  - Line height: 1.2
  - Letter spacing: 0.02em
  - Color: #111827

- Body font: Inter
  - Weight: 400
  - Style: normal
  - Line height: normal (Streamlit default)
  - Color: #111827

- Mono/accent font: Michroma (Brand font)
  - Weight: 400
  - Style: normal
  - Letter spacing: -0.02em
  - Text-transform: uppercase

- Font size, weight, line height, letter spacing, color for specific elements:
  - Page titles (h1, h2, h3): Montserrat, 600, 1.2, 0.02em, #111827
  - Section headers: Montserrat, 600, 1.2, 0.02em, #111827
  - Card titles (Metric Label): Inter, 0.65rem, 800, normal, 0.12em, #6B7280 (uppercase)
  - Card values (Metric Value): Inter, 2.2rem, 800, normal, -0.03em, #000000
  - Table headers: Inter, Streamlit default (global text color #111827)
  - Table cells: Inter, Streamlit default (global text color #111827)
  - Sidebar items (nav item): Inter, 0.95rem, 600, normal, -0.01em, #4B5563
  - Button text: Inter, 13px, 700, normal, -0.01em, #FFFFFF
  - Label text (technical label): Inter, 14px, 800, normal, 0.15em, #6B7280 (uppercase)
  - Muted/helper text (sidebar footer): Inter, 11px, normal, normal, 0.05em, #999999

## SECTION 2 — COLORS

- Page background color: #F8F9FB
- Sidebar background color: #FFFFFF
- Card/surface background color: #FFFFFF
- Primary accent color: #34ACED
- Accent hover color: #34ACED
- Primary text color: #111827
- Secondary/muted text color: #6B7280
- Border color: #E5E7EB
- Divider color: #E5E7EB
- Input field background color: Streamlit dark/light default overrides (not explicitly customized)
- Input field border color: Streamlit default
- Input field text color: Streamlit default
- Input field focus border color: Streamlit default
- Success color: background #D1FAE5, text #065F46 (Border/Icon: #10B981)
- Warning color: background #FEF3C7, text #92400E (Border/Icon: #F59E0B)
- Danger/error color: background #FEE2E2, text #991B1B (Border/Icon: #EF4444)
- Info color: Streamlit default (`st.info()`)
- Button background color: #000000
- Button text color: #FFFFFF
- Button hover background color: #34ACED
- Button border radius: 4px
- Active nav item background color: #F0F9FF
- Active nav item text color: #34ACED
- Inactive nav item background color: transparent (hover #F8F9FB)
- Inactive nav item text color: #4B5563
- Table header background color: #FFFFFF (via `[data-testid="stDataFrame"]`)
- Table header text color: #111827
- Table row background color: #FFFFFF
- Table row alternate background color: Streamlit default empty
- Table row hover color: Streamlit default
- Table border color: #E5E7EB
- Scrollbar color: Streamlit default

## SECTION 3 — SPACING & LAYOUT

- Page max width: 100% (using layout="wide")
- Page padding: Main block container padding top/bottom 0rem (modified in Auth pages)
- Sidebar width: Streamlit default explicit CSS width with `padding-top: 1rem`
- Section margin between major sections: Divider margins `2rem 0`
- Card padding: 24px
- Card margin between cards: Streamlit column grid gap handling
- Card border radius: 6px
- Card border width and color: 1px solid #E5E7EB
- Card box shadow: none
- Gap between columns in metric card row: Streamlit default `st.columns()` tracking
- Gap between chart and table on same page: Streamlit default spacer with `st.divider()`
- Input field padding: Streamlit default
- Input field border radius: Streamlit default
- Button padding (horizontal and vertical): 0.75rem 1.5rem
- Button border radius: 4px
- Table cell padding: Streamlit default padding
- Table border radius: 4px

## SECTION 4 — METRIC CARDS

```python
def metric_card(title: str, value, unit: str = ""):
    """
    Render a single metric using Streamlit native st.metric().
    If unit is provided and value doesn't already end with it, append it.
    """
    val_str = str(value)
    if unit and not val_str.endswith(unit.strip()):
        display_value = f"{val_str}{unit}"
    else:
        display_value = val_str
    st.metric(label=title, value=display_value)
```

Metric card styling details:
- Title text: Inter, 0.65rem, 800, #6B7280
- Value text: Inter, 2.2rem, 800, #000000
- Unit text: (Inherits from value)
- Card background: #FFFFFF
- Card border: 1px solid #E5E7EB
- Card border-radius: 6px
- Card padding: 24px
- Card box-shadow: none
- Card hover effect: `border-color: #34ACED`
- How many cards per row: Controlled via `render_metric_row()` with `st.columns(len(metrics))` outputting as many columns as requested.
- Column gap between cards: Streamlit native layout.

## SECTION 5 — SECTION HEADERS

```python
def section_header(title: str):
    """
    Render a page/section title.
    Section 5 — FRONTEND_DESIGN_SYSTEM.md.
    Uses st.title() — Montserrat 600 #111827 via global CSS.
    """
    st.title(title)
```

- Font name: Montserrat
- Font size: Streamlit Native (for h1)
- Font weight: 600
- Font color: #111827
- Bottom border or underline: None explicitly inside `section_header()`, but often followed by `st.divider()` in the project pattern.
- Margin above and below the header: Streamlit native margins overrides.
- Any icon or decorator before/after the title: None explicitly declared.

## SECTION 6 — SIDEBAR

```css
        /* Sidebar */
        [data-testid="stSidebar"] { 
            background-color: #FFFFFF !important; 
            border-right: 1px solid #E5E7EB !important; 
            padding-top: 1rem;
        }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Navigation Radio */
        div[data-testid="stRadio"] { padding: 0 !important; }
        div[data-testid="stRadio"] [role="radiogroup"] { gap: 0.2rem !important; }
        div[data-testid="stRadio"] label {
            padding: 8px 12px !important;
            margin-bottom: 2px !important;
            cursor: pointer !important;
            border-radius: 4px !important;
            border: 1px solid transparent !important;
            background-color: transparent !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #F8F9FB !important;
        }
        div[role="radiogroup"] > label > div:first-child,
        div[data-testid="stRadio"] label div[data-baseweb="radio"],
        .stRadio [role="radio"] > div:first-child,
        .stRadio div[role="radiogroup"] label > div:first-child {
            display: none !important;
            opacity: 0 !important;
            width: 0px !important;
            height: 0px !important;
            overflow: hidden !important;
        }
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            color: #4B5563 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.01em !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] {
            background-color: #F0F9FF !important;
            border: 1px solid #BAE6FD !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
            color: #34ACED !important;
            font-weight: 800 !important;
        }
```

- Background color: #FFFFFF
- Border-right style: 1px solid #E5E7EB
- Logo or title at top: Inter, 14px, #6B7280 (Platform), Michroma, 20px, #000000 (RetailPulse), Inter, 14px, #6B7280 (Analytics Dashboard); Margin customized in `app.py`.
- Nav item padding: 8px 12px
- Nav item font: Inter
- Nav item size: 0.95rem
- Nav item color: #4B5563
- Nav item border-radius: 4px
- Nav item active background: #F0F9FF
- Nav item active text color: #34ACED
- Nav item active font-weight: 800
- Nav item hover background: #F8F9FB
- Nav item spacing between items: 0.2rem (gap), margin-bottom 2px
- Sign Out button: Standard Streamlit button behavior injected via `st.button()` directly in the sidebar
- Dividers inside sidebar: Uses `st.divider()`

## SECTION 7 — BUTTONS

```css
        /* Buttons */
        .stButton > button, .stDownloadButton > button, div[data-testid="stDownloadButton"] > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important; 
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0.75rem 1.5rem !important;
            text-transform: none !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button *, .stDownloadButton > button *, div[data-testid="stDownloadButton"] > button * {
            color: #FFFFFF !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
            background-color: #34ACED !important;
            transform: translateY(-1px);
        }
        .stButton > button:active, .stDownloadButton > button:active, div[data-testid="stDownloadButton"] > button:active {
            transform: translateY(0);
        }
```

- Primary button background: #000000
- Primary button text color: #FFFFFF
- Primary button border: none
- Primary button radius: 4px
- Primary button padding: 0.75rem 1.5rem
- Primary button font: Inter, 13px, 700, -0.01em
- Primary button hover background: #34ACED
- Primary button hover text color: #FFFFFF
- Secondary button: (None distinct explicitly styled, all `.stButton > button` match this styling)
- Danger button: (None distinct explicitly styled)

## SECTION 8 — TABLES

```css
        /* DataFrames */
        [data-testid="stDataFrame"] { 
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB; 
            border-radius: 4px; 
            padding: 0;
        }
```

- Table background color: #FFFFFF
- Table border style: 1px solid #E5E7EB
- Table border-radius: 4px
- Header row, Data rows, row hover, gridlines mostly fallback to Streamlit Dataframe internals with overrides on the outer wrapper padding (0).

## SECTION 9 — INPUT FIELDS & FORMS

- Input field background: Streamlit default
- Input field border: Streamlit default
- Input field border-radius: Streamlit default
- Input field padding: Streamlit default
- Input field font: Streamlit default Inter
- Input field color: #111827 (global)
- Input field placeholder: Streamlit default placeholder colors
- Input field focus: Streamlit default
- Label: Collapsed via code (`label_visibility="collapsed"`) inside authentication, generally handled by Streamlit.

## SECTION 10 — ALERT / BANNER COMPONENTS

```python
def show_error(message: str):
    """
    Section 10 — Error Banner (page-level).
    Uses Streamlit native st.error().
    """
    st.error(f"⚠️ {message}")


def show_success(message: str):
    """
    Section 10 — Success Banner.
    Custom HTML to match exact design spec colors.
    """
    st.markdown(
        f"""
        <div style='padding: 10px; background-color: #D1FAE5; border: 2px solid #10B981; border-radius: 5px; margin-bottom: 15px;'>
            <p style='color: #065F46; font-weight: bold; margin: 0; font-size: 14px;'>
                ✓ {message}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_warning(message: str):
    """
    Section 10 — Warning Banner.
    Custom HTML to match exact design spec colors.
    """
    st.markdown(
        f"""
        <div style='padding: 14px 18px; background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; margin-bottom: 8px;'>
            <p style='color: #92400E; font-size: 14px; font-weight: 600; margin: 0;'>
                {message}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
```

## SECTION 11 — LOADING STATES

- Spinner style: Native `st.spinner("Loading data...")` or `st.spinner("Pipeline running...")`
- Skeleton loader style: None explicitly provided
- Loading text: Streamlit's native implementation (typically Inter, global text color)
- Any overlay or blur effect while loading: None explicitly applied globally for loaders natively.

## SECTION 12 — COLOR CODING RULES

- HIGH / CRITICAL: exact background hex #FEE2E2, exact text hex #991B1B
- MEDIUM / WARNING: exact background hex #FEF3C7, exact text hex #92400E
- LOW / SAFE: exact background hex #D1FAE5, exact text hex #065F46
- INFO / NEUTRAL: exact background hex #F8F9FB (app bg), exact text hex #111827
- TRUE (boolean): exact background hex #FEE2E2, exact text hex #991B1B
- FALSE (boolean): exact background hex #D1FAE5, exact text hex #065F46

## SECTION 13 — NAVIGATION LOGIC (copy verbatim)

```python
# ── 1. SESSION STATE INITIALIZATION ──────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state["username"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Run Pipeline"
if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "signin"

# ── 2. QUERY PARAMS — PAGE REFRESH FIX ───────────────────────────────────────
params = st.query_params
if "page" in params:
    st.session_state["current_page"] = params["page"]


def navigate_to(page_name: str):
    st.session_state["current_page"] = page_name
    st.query_params["page"] = page_name


# ── 3. AUTH GUARD ─────────────────────────────────────────────────────────────
if st.session_state["username"] is None:
    if st.session_state["auth_page"] == "signin":
        from pages.signin import render
        render()
    else:
        from pages.signup import render
        render()
    st.stop()

# ── 6. SIDEBAR ────────────────────────────────────────────────────────────────
def on_nav_change():
    navigate_to(st.session_state["nav_radio"])

with st.sidebar:
    st.markdown('<p class="tech-label">Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-font">RetailPulse</p>', unsafe_allow_html=True)
    st.markdown('<p class="tech-label" style="margin-top:-5px;">Analytics Dashboard</p>', unsafe_allow_html=True)
    st.divider()

    current_page = st.session_state.get("current_page", "Run Pipeline")
    if current_page not in PAGE_NAMES:
        current_page = PAGE_NAMES[0]
    if "nav_radio" not in st.session_state or st.session_state["nav_radio"] != current_page:
        st.session_state["nav_radio"] = current_page

    st.radio(
        "Navigation",
        PAGE_NAMES,
        key="nav_radio",
        on_change=on_nav_change,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        f"<div style='font-size:11px;color:#999;letter-spacing:0.05em;'>"
        f"<p><strong>API ENDPOINT</strong><br/>{BASE_URL}</p>"
        f"<p>Signed in as <strong>{st.session_state.get('username','')}</strong></p></div>",
        unsafe_allow_html=True,
    )

    if st.button("Sign Out", key="sign_out_btn"):
        st.session_state["username"] = None
        st.session_state["current_page"] = "Run Pipeline"
        st.session_state["auth_page"] = "signin"
        st.query_params.clear()
        st.rerun()

# ── 7. PAGE ROUTING ───────────────────────────────────────────────────────────
from pages import (
    run_pipeline, sales_trends, customer_loyalty, at_risk_alerts,
    top_products, rfm_segmentation, predictive_analytics,
    rejected_records, visualizations,
)

page_map = {
    "Run Pipeline":         run_pipeline.render,
    "Sales Trends":         sales_trends.render,
    "Customer Loyalty":     customer_loyalty.render,
    "At-Risk Alerts":       at_risk_alerts.render,
    "Top Products":         top_products.render,
    "RFM Segmentation":     rfm_segmentation.render,
    "Predictive Analytics": predictive_analytics.render,
    "Rejected Records":     rejected_records.render,
    "Visualizations":       visualizations.render,
}

current = st.session_state.get("current_page", "Run Pipeline")
page_map.get(current, run_pipeline.render)()
```

## SECTION 14 — AUTH COMPONENTS

- Sign In Form:
    - Background: Default main interface with spacing override (0rem padding so it spans width effectively).
    - Styling of headers uses inline HTML Markdown for 'RETAILPULSE' text (Montserrat, #111827).
    - `st.text_input` fields used for Username and Password with `label_visibility="collapsed"`.
    - Double `st.button` rendering mapped on columns (`[1, 1]`) providing full container width buttons for login and subpage redirect.
    - Error message style via standard `st.error()` enclosed within an `st.empty` display.
- Sign Up Form:
    - Follows identical configuration with Username, Email, Password, Confirm Password mapped across `st.text_input`.
- Auth Card: Structure mapped via nested column rendering `_, col, _ = st.columns([1, 1.2, 1])` embedded inside `st.container(border=True)`. Uses Streamlit's container bounds.

## SECTION 15 — API CLIENT PATTERN

```python
class RetailPulseClient:

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _make_request(self, endpoint: str, method: str = "GET", json=None) -> Optional[requests.Response]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method, url=url, json=json, timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Failed to connect to API at {url}. Is the backend running?"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request to {url} timed out after {self.timeout} seconds"
            )
        except requests.exceptions.HTTPError:
            self._handle_error(response)
        except Exception as e:
            raise Exception(f"Unexpected error occurred: {str(e)}")

    def _handle_error(self, response: requests.Response) -> None:
        status_code = response.status_code
        if status_code == 400:
            raise ValueError(f"Bad request: {response.text}")
        elif status_code == 401:
            raise PermissionError(f"401 Unauthorized: {response.text}")
        elif status_code == 403:
            raise PermissionError(f"403 Forbidden: {response.text}")
        elif status_code == 404:
            raise FileNotFoundError(f"404 Resource not found: {response.url}")
        elif status_code == 500:
            raise Exception(f"500 Server error: {response.text}")
        else:
            raise Exception(f"HTTP {status_code}: {response.text}")
```

## SECTION 16 — PAGE TEMPLATE PATTERN

```python
def render():
    from custom_styles import apply_theme, section_header
    from helpers import safe_mean, safe_sum, safe_count, render_table, show_api_error, render_metric_row
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()
    section_header("Sales Trends")
    st.markdown("Sales performance over time across all stores.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_sales_header())
        except Exception as e:
            show_api_error(e, context="sales data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Summary Cards ─────────────────────────────────────────────────────────
    total_transactions = safe_count(df)
    
    # [Data Setup]

    render_metric_row([
        ("Total Transactions", f"{total_transactions:,}", ""),
        # [Other Metrics]
    ])

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("All Sales Records")
    render_table(df)
```

## SECTION 17 — GLOBAL CSS OVERRIDES

```css
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap');

        /* Main body background and technical grid */
        .stApp { 
            background-color: #F8F9FB; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            color: #111827;
            background-image: 
                linear-gradient(#E5E7EB 1px, transparent 1px),
                linear-gradient(90deg, #E5E7EB 1px, transparent 1px);
            background-size: 40px 40px;
            background-position: center;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 251, 0.8) 100%);
            z-index: -1;
        }

        /* Headers */
        h1, h2, h3 { 
            font-family: 'Montserrat', sans-serif !important;
            color: #111827 !important; 
            font-weight: 600 !important; 
            letter-spacing: 0.02em !important; 
            line-height: 1.2 !important;
            text-transform: none !important;
        }

        /* Branding Font */
        .brand-font {
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: -0.02em !important;
            color: #000000 !important;
            font-size: 20px !important;
            margin-bottom: 0 !important;
        }

        /* Technical Status Labels */
        .tech-label {
            font-size: 14px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.15em !important;
            color: #6B7280 !important;
            margin-bottom: 4px !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] { 
            background-color: #FFFFFF !important; 
            border-right: 1px solid #E5E7EB !important; 
            padding-top: 1rem;
        }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Metrics */
        [data-testid="stMetricValue"] { 
            color: #000000 !important; 
            font-weight: 800; 
            font-size: 2.2rem !important;
            letter-spacing: -0.03em;
        }
        [data-testid="stMetricLabel"] { 
            color: #6B7280 !important; 
            font-weight: 800; 
            font-size: 0.65rem; 
            text-transform: uppercase; 
            letter-spacing: 0.12em; 
        }
        [data-testid="stMetric"] { 
            background-color: #FFFFFF; 
            padding: 24px !important; 
            border-radius: 6px; 
            border: 1px solid #E5E7EB;
            box-shadow: none;
            transition: border-color 0.2s;
        }
        [data-testid="stMetric"]:hover { border-color: #34ACED; }

        /* Navigation Radio */
        div[data-testid="stRadio"] { padding: 0 !important; }
        div[data-testid="stRadio"] [role="radiogroup"] { gap: 0.2rem !important; }
        div[data-testid="stRadio"] label {
            padding: 8px 12px !important;
            margin-bottom: 2px !important;
            cursor: pointer !important;
            border-radius: 4px !important;
            border: 1px solid transparent !important;
            background-color: transparent !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #F8F9FB !important;
        }
        div[role="radiogroup"] > label > div:first-child,
        div[data-testid="stRadio"] label div[data-baseweb="radio"],
        .stRadio [role="radio"] > div:first-child,
        .stRadio div[role="radiogroup"] label > div:first-child {
            display: none !important;
            opacity: 0 !important;
            width: 0px !important;
            height: 0px !important;
            overflow: hidden !important;
        }
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            color: #4B5563 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.01em !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] {
            background-color: #F0F9FF !important;
            border: 1px solid #BAE6FD !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
            color: #34ACED !important;
            font-weight: 800 !important;
        }

        /* Dividers */
        hr { border-bottom: 1px solid #E5E7EB !important; opacity: 1; margin: 2rem 0 !important; }

        /* DataFrames */
        [data-testid="stDataFrame"] { 
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB; 
            border-radius: 4px; 
            padding: 0;
        }

        /* Buttons */
        .stButton > button, .stDownloadButton > button, div[data-testid="stDownloadButton"] > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important; 
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0.75rem 1.5rem !important;
            text-transform: none !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button *, .stDownloadButton > button *, div[data-testid="stDownloadButton"] > button * {
            color: #FFFFFF !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
            background-color: #34ACED !important;
            transform: translateY(-1px);
        }
        .stButton > button:active, .stDownloadButton > button:active, div[data-testid="stDownloadButton"] > button:active {
            transform: translateY(0);
        }

        /* Status Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 100px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background-color: #F3F4F6;
            border: 1px solid #E5E7EB;
            color: #4B5563;
        }
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .dot-success { background-color: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
        .dot-error { background-color: #EF4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
        .dot-warning { background-color: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }

        /* Visualization Cards */
        .viz-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 24px;
            margin-bottom: 24px;
        }

        /* Auth-specific page overrides (signin.py, signup.py) */
        .main > div { padding-top: 0rem !important; }
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
        [data-testid="stAppViewContainer"] > section.main { padding-top: 0 !important; }
        div[data-testid="stMarkdownContainer"] {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="element-container"]:has(div[data-testid="stMarkdownContainer"]) {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
```
