# components/layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback_context, no_update
from config import Config
from utils.general import load_markdown_file
from i18n import t


def create_navbar():
    """
    Create a modern navbar with dynamic language dropdown.
    Only languages with a configured APP_URL_* appear in the switcher.
    """

    current_language = Config.APP_LANGUAGE

    # All supported languages: (code, translation_key, url)
    # Ordered: English first, then alphabetical by native name
    all_languages = [
        ('en', 'navbar.lang_english', Config.APP_URL_EN),
        ('cs', 'navbar.lang_czech', Config.APP_URL_CS),
        ('da', 'navbar.lang_danish', Config.APP_URL_DA),
        ('de', 'navbar.lang_german', Config.APP_URL_DE),
        ('es', 'navbar.lang_spanish', Config.APP_URL_ES),
        ('fr', 'navbar.lang_french', Config.APP_URL_FR),
        ('hr', 'navbar.lang_croatian', Config.APP_URL_HR),
        ('it', 'navbar.lang_italian', Config.APP_URL_IT),
        ('nl', 'navbar.lang_dutch', Config.APP_URL_NL),
        ('pl', 'navbar.lang_polish', Config.APP_URL_PL),
        ('pt', 'navbar.lang_portuguese', Config.APP_URL_PT),
        ('sk', 'navbar.lang_slovak', Config.APP_URL_SK),
        ('sl', 'navbar.lang_slovenian', Config.APP_URL_SL),
        ('sv', 'navbar.lang_swedish', Config.APP_URL_SV),
        ('uk', 'navbar.lang_ukrainian', Config.APP_URL_UK),
    ]

    # Build dropdown: English first with divider, then the rest
    language_items = []
    en_url = Config.APP_URL_EN
    if en_url:
        language_items.append(dbc.DropdownMenuItem([
            html.I(className="fas fa-globe me-2"),
            t("navbar.lang_english")
        ], href=en_url, active=(current_language == 'en')))

    other_items = []
    for code, key, url in all_languages:
        if code == 'en' or not url:
            continue
        other_items.append(dbc.DropdownMenuItem([
            html.I(className="fas fa-globe me-2"),
            t(key)
        ], href=url, active=(current_language == code)))

    if language_items and other_items:
        language_items.append(dbc.DropdownMenuItem(divider=True))
    language_items.extend(other_items)

    # Navigation items
    nav_items = [
        # Language Dropdown
        dbc.NavItem([
            dbc.DropdownMenu(
                children=language_items,
                nav=True,
                in_navbar=True,
                label=[
                    html.I(className="fas fa-language me-2"),
                    t("navbar.language")
                ],
                direction="down",
                className="me-3"
            ),
        ]),

        # How to use nav link - opens modal
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-question-circle me-2"),
            t("navbar.how_to_use")
        ], id="how-to-use-nav-link", className="nav-link", style={"cursor": "pointer"})),

        # Feedback nav link - opens modal
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-comment-dots me-2"),
            t("navbar.feedback")
        ], id="feedback-nav-link", className="nav-link", style={"cursor": "pointer"})),

        dbc.NavItem(dbc.NavLink([
            html.I(className="fab fa-github me-2"),
            t("navbar.github")
        ], href=Config.GITHUB_URL, target="_blank", className="nav-link")),
    ]

    # Brand element
    brand_children = []
    if Config.LOGO_PATH:
        brand_children.append(html.Img(
            src=Config.LOGO_PATH,
            height="40px",
            className="me-3"
        ))
    brand_children.append(html.Span(
        t("app.brand_name"),
        className="navbar-brand-text",
        style={
            'fontWeight': '700',
            'fontSize': '1.5rem',
            'color': 'white'
        }
    ))
    brand = html.Div(brand_children, className="d-flex align-items-center")

    return dbc.Navbar(
        dbc.Container([
            # Brand
            dbc.NavbarBrand(brand, href="/", className="me-auto"),

            # Toggler for mobile
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

            # Collapsible content
            dbc.Collapse(
                dbc.Nav(nav_items, className="ms-auto", navbar=True),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ], fluid=True),
        className="modern-navbar",
        sticky="top",
        dark=True,
    )

def create_feedback_modal():
    """Create the feedback modal component."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(t("feedback.title"))),
        dbc.ModalBody([
            dbc.Label(t("feedback.category_label"), html_for="feedback-category", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="feedback-category",
                options=[
                    {"label": t("feedback.category_not_specified"), "value": "not_specified"},
                    {"label": t("feedback.category_bug"), "value": "bug"},
                    {"label": t("feedback.category_appreciation"), "value": "appreciation"},
                    {"label": t("feedback.category_recommendation"), "value": "recommendation"},
                ],
                value="not_specified",
                clearable=False,
                className="mb-3",
            ),
            dbc.Label(t("feedback.message_label"), html_for="feedback-message", style={"fontWeight": "bold"}),
            dbc.Textarea(
                id="feedback-message",
                placeholder=t("feedback.message_placeholder"),
                style={"height": "150px"},
                className="mb-3",
            ),
            dbc.Alert(
                id="feedback-alert",
                is_open=False,
                dismissable=True,
                duration=5000,
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button(t("feedback.btn_close"), id="feedback-close-btn", color="secondary", className="me-2"),
            dbc.Button(t("feedback.btn_submit"), id="feedback-submit-btn", color="primary"),
        ]),
    ], id="feedback-modal", is_open=False, centered=True)

def create_how_to_use_modal():
    """Create the How to Use modal component."""
    how_to_use_content = load_markdown_file("how_to_use.md")

    footer_buttons = [
        dbc.Button(t("how_to_use.btn_close"), id="how-to-use-close-btn", color="secondary", className="me-2"),
    ]
    if Config.DOCUMENTATION_URL:
        footer_buttons.append(dbc.Button([
            html.I(className="fas fa-book me-2"),
            t("how_to_use.btn_docs")
        ], href=Config.DOCUMENTATION_URL, target="_blank", color="primary"))

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-question-circle me-2"),
            t("how_to_use.title")
        ])),
        dbc.ModalBody(
            dcc.Markdown(how_to_use_content, className="markdown-content",
                         link_target="_blank"),
            id="how-to-use-modal-body",
        ),
        dbc.ModalFooter(footer_buttons),
    ], id="how-to-use-modal", size="lg", scrollable=True, centered=True, is_open=False)


def create_footer():
    """
    Create a modern footer similar to zboardio design

    Returns:
        html.Footer: Configured footer component
    """

    return html.Footer([
        html.Div([
            dbc.Container([
                dbc.Row([
                    # Main Footer Content
                    dbc.Col([
                        # Brand and Description
                        html.Div([
                            html.H5(t("app.title"), className="footer-brand"),
                            html.P(t("app.description"), className="footer-description")
                        ], className="mb-4"),

                        # Links Section
                        html.Div([
                            html.A([
                                html.I(className="fas fa-envelope footer-icon"),
                                t("footer.contact_us")
                            ], id="contact-email-link", style={"cursor": "pointer"}),

                            html.A([
                                html.I(className="fas fa-globe footer-icon"),
                                t("footer.our_website")
                            ], href=Config.WEBSITE_URL, target="_blank"),

                            html.A([
                                html.I(className="fab fa-github footer-icon"),
                                t("footer.open_source")
                            ], href=Config.GITHUB_URL, target="_blank"),

                            html.A([
                                html.I(className="fas fa-comment-dots footer-icon"),
                                t("footer.feedback")
                            ], id="feedback-footer-link", style={"cursor": "pointer"}),
                        ] + ([
                            html.A([
                                html.I(className="fas fa-book footer-icon"),
                                t("footer.documentation")
                            ], href=Config.DOCUMENTATION_URL, target="_blank"),
                        ] if Config.DOCUMENTATION_URL else []), className="footer-links mb-4"),

                        # Build transparency
                        html.Div([
                            html.P([
                                html.I(className="fas fa-code-branch footer-icon"),
                                t("footer.build"),
                                html.A(
                                    Config.GIT_COMMIT,
                                    href=f"{Config.GITHUB_URL}/commit/{Config.GIT_COMMIT}" if Config.GIT_COMMIT != 'dev' else Config.GITHUB_URL,
                                    target="_blank",
                                    style={'color': 'var(--accent-color)'}
                                ),
                                " — ",
                                html.A(
                                    t("footer.verify_source"),
                                    href=f"{Config.GITHUB_URL}",
                                    target="_blank",
                                    style={'color': 'var(--accent-color)'}
                                ),
                            ], style={'fontSize': '0.85rem', 'color': '#B0BEC5', 'marginBottom': '0.5rem'}),
                        ]),

                        # Copyright
                        html.Div([
                            html.P([
                                html.I(className="fas fa-copyright footer-icon"),
                                f"{Config.COPYRIGHT_YEAR} {Config.COMPANY_NAME}",
                                t("footer.all_rights")
                            ], className="copyright mb-0")
                        ])
                    ], width=12, className="text-center")
                ])
            ], fluid=True)
        ], className="footer-content")
    ], className="modern-footer")


def create_email_toast():
    """Create toast notification for email copy feedback."""
    return dbc.Toast(
        t("footer.email_copied"),
        id="email-copied-toast",
        header=t("footer.contact_us"),
        icon="success",
        is_open=False,
        dismissable=True,
        duration=3000,
        style={"position": "fixed", "bottom": 20, "right": 20, "zIndex": 9999},
    )


# Callback for navbar toggler (mobile menu)
def register_navbar_callbacks(app):
    """Register callbacks for navbar functionality"""

    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    # Toggle How to Use modal open/close
    @app.callback(
        Output("how-to-use-modal", "is_open"),
        [Input("how-to-use-nav-link", "n_clicks"),
         Input("how-to-use-close-btn", "n_clicks")],
        [State("how-to-use-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_how_to_use_modal(nav_clicks, close_clicks, is_open):
        return not is_open

    # Toggle feedback modal open/close
    @app.callback(
        Output("feedback-modal", "is_open"),
        [Input("feedback-nav-link", "n_clicks"),
         Input("feedback-footer-link", "n_clicks"),
         Input("feedback-close-btn", "n_clicks"),
         Input("feedback-submit-btn", "n_clicks")],
        [State("feedback-modal", "is_open"),
         State("feedback-message", "value")],
        prevent_initial_call=True,
    )
    def toggle_feedback_modal(nav_clicks, footer_clicks, close_clicks, submit_clicks, is_open, message):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id in ("feedback-nav-link", "feedback-footer-link"):
            return True
        if trigger_id == "feedback-close-btn":
            return False
        if trigger_id == "feedback-submit-btn":
            # Close modal only on successful submit (message non-empty)
            if message and message.strip():
                return False
            # Keep open if validation fails
            return True
        return no_update

    # Submit feedback
    @app.callback(
        [Output("feedback-alert", "children"),
         Output("feedback-alert", "color"),
         Output("feedback-alert", "is_open"),
         Output("feedback-message", "value"),
         Output("feedback-category", "value")],
        Input("feedback-submit-btn", "n_clicks"),
        [State("feedback-category", "value"),
         State("feedback-message", "value")],
        prevent_initial_call=True,
    )
    def submit_feedback(n_clicks, category, message):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update

        if not message or not message.strip():
            return t("feedback.validation_empty"), "warning", True, no_update, no_update

        from utils.mongodb import save_feedback
        success, error = save_feedback(category, message.strip(), Config.APP_LANGUAGE)

        if success:
            return t("feedback.success"), "success", True, "", "not_specified"

        return t("feedback.error"), "danger", True, no_update, no_update

    # Copy email to clipboard and show toast
    app.clientside_callback(
        f"""
        function(n_clicks) {{
            if (n_clicks) {{
                navigator.clipboard.writeText("{Config.CONTACT_EMAIL}");
                return true;
            }}
            return window.dash_clientside.no_update;
        }}
        """,
        Output("email-copied-toast", "is_open"),
        Input("contact-email-link", "n_clicks"),
        prevent_initial_call=True,
    )
