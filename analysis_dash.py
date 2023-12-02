import copy
import dash
import threading
import json
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc

from config import GLOBAL_FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR
from config import roles_mapping, role_translation
import dash_bootstrap_components as dbc
from update_table import update_table_all, update_database, update_last_time, run_periodic_update, get_last_update_time, get_database
from plot import customize_plot, plot_top3_vs_winrate, pick_pick_vs_win, plot_pick_vs_rp, plot_rp_vs_win
from styles import dropdown_style, button_style, container_style, default_character_style, selected_character_style


roles_mapping = copy.deepcopy(roles_mapping)


def generate_character_grid(characters):
    return html.Div(
        [dbc.Row(
            [dbc.Col(html.Div(character, id={'type': 'char-box', 'index': i}, className='character-box', style=default_character_style), width='auto') for i, character in enumerate(characters)],
            className="justify-content-between",
        )],
        className="container-fluid"
    )

# Add custom CSS class for dropdown hover state in your external CSS file or within app layout using the style tag
external_css = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css',  # Example external CSS
    '/assets/custom_styles.css'  # Path to your custom CSS file
]
app = dash.Dash(__name__, external_stylesheets=external_css)


app.layout = html.Div([
    # Fixed Div for selection bars
    html.Div([
        html.Div(id='selected-characters', style={'display': 'none'}),
        dcc.Store(id='stored-selected-characters'),
        # Dropdown for Comparison selection
        dcc.Dropdown(
            id='comparison-dropdown',
            options=[
                {'label': '픽률 vs 승률', 'value': 'pick_vs_win'},
                {'label': '픽률 vs RP 획득량', 'value': 'pick_vs_rp'},
                {'label': 'Top 3 비율 vs Top 3 확보 시 승률', 'value': 'top3_vs_winrate'},
                {'label': 'RP 획득량 vs 승률', 'value': 'rp_vs_win'}
            ],
            value='top3_vs_winrate',  # Default value
            clearable=False,
            style=dropdown_style,
            className='custom-dropdown'
        ),
        dcc.Dropdown(
            id='version-dropdown',
            options=[
                {'label': '이전 버전', 'value': 'prevPatch'},
                {'label': '현재 버전', 'value': 'currentPatch'},
                {'label': '현재 버전 (최근 3일)', 'value': '3day'},
                {'label': '현재 버전 (최근 7일)', 'value': '7day'}
            ],
            value='currentPatch',  # Default value
            style=dropdown_style,
            className='custom-dropdown'
        ),
        # Dropdown for Tier selection
        dcc.Dropdown(
            id='tier-dropdown',
            options=[
                {'label': 'in 1000', 'value': 'in_1000'},
                {'label': '다이아몬드+', 'value': 'diamond_plus'},
                {'label': '플레티넘+', 'value': 'platinum_plus'},
            ],
            value='platinum_plus',  # Default value
            clearable=False,
            style=dropdown_style,
            className='custom-dropdown'
        ),
        dcc.Dropdown(
            id='role-dropdown',
            options=[
                {'label': '전체', 'value': 'Whole'},
                {'label': '근거리 딜러', 'value': 'Melee Carry'},
                {'label': '스킬 원거리 딜러', 'value': 'Skill Ranged Carry'},
                {'label': '평타 원거리 딜러', 'value': 'Attack Ranged Carry'},
                {'label': '탱커', 'value': 'Tanker'},
                {'label': '암살자', 'value': 'Assassin'},
                {'label': '서포터', 'value': 'Supporter'},
                {'label': '유저 정의', 'value': 'User Defined'},
            ],
            value='Whole',  # Default value
            clearable=False,
            style=dropdown_style,
            className='custom-dropdown'
        ),
        html.Div(
            children=[
                html.Button(
                    children='유저 정의 그룹 편집',
                    id='edit-user-defined-roles-button',
                    style=button_style,
                    className='custom-button',
                )
            ],
            id='button-container',
            style=container_style
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-between',  # 내부 요소들을 양쪽 끝과 중앙에 배치
        'alignItems': 'center',  # 버튼과 드롭다운을 세로 중앙 정렬
        'padding': '0.5rem',  # 패딩 조정으로 내부 요소와 경계 사이의 간격을 줄임
        'gap': '0.5rem',  # 요소들 사이의 간격을 줄임
    }),

    # Modal component update with buttons
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("유저 그룹 정의 편집")),
            dbc.ModalBody(
                generate_character_grid(roles_mapping['Reference']),
                style={'maxHeight': 'calc(100vh - 210px)', 'overflowY': 'auto'}
            ),
            dbc.ModalFooter([
                dbc.Button("확인", id="confirm-modal", className="ml-auto", n_clicks=0, size="lg",),
                dbc.Button("초기화", id="reset-modal", className="ml-auto", n_clicks=0, size="lg", disabled=True),
                dbc.Button("취소", id="close-modal", className="ml-auto", n_clicks=0, size="lg",),
            ]),
        ],
        id="modal-edit-user-defined-roles",
        is_open=False,
        style={"zIndex": 1100, "maxWidth": "100vw"},  # Adjusted maxWidth to 100vw for full viewport width
    ),
    dcc.Store(id='confirm-click-flag', data={'clicked': False}),
    dcc.Store(id='char-box-styles', data={}),

    # Rest of the layout
    html.Div(id='slider-value-container',
            style={
                    'textAlign': 'left',
                    'marginLeft': '10px',
                    'marginTop': '-10px',  # Reduced from 30px to 10px
                    'color': TEXT_COLOR,
                    'fontFamily': GLOBAL_FONT_FAMILY,
                    'fontSize': '14px'
                }
    ),
    html.Div(id='slider-container', children=[
        dcc.RangeSlider(
            id='pick-rate-slider',
            min=0,  # Default minimum
            max=1,  # Default maximum
            value=[0, 1],  # Default value
            updatemode='drag'
        )
    ], style={'textAlign': 'center', 'margin': '1rem'}),
    html.Div([
        # Customized Graph Style
        dcc.Graph(
            id='scatter-plot',
            config={'scrollZoom': True, 'displayModeBar': True},  # Hide modebar if not necessary
            style={'width': '100%', 'height': '84vh'}  # Adjusted for responsiveness
        ),
        html.Div(
            id='last-update-time',
            style={
                'textAlign': 'left',
                'color': TEXT_COLOR,
                'fontFamily': GLOBAL_FONT_FAMILY,
                'fontSize': '12px',
                'paddingLeft': '5px',
                "zIndex": 1100,
                "left": "10px",
                "position": "fixed",
            }
        ),
        html.Div(
            html.A(
                "Project Page",
                href="https://github.com/mikigom/ER_plot",
                target="_blank",
                style={
                    'textAlign': 'right',
                    'display': 'block',
                    'color': PRIMARY_COLOR,
                    'fontFamily': GLOBAL_FONT_FAMILY,
                    'fontSize': '12px',
                    'paddingRight': '5px',
                    'textDecoration': 'none',
                    "position": "fixed",
                    "right": "10px",
                    "zIndex": 1100,
                }
            )
        ),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds
        n_intervals=0
    )
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': BACKGROUND_COLOR
})

@app.callback(
    Output('slider-value-container', 'children'),
    [Input('pick-rate-slider', 'value'), Input('comparison-dropdown', 'value')]
)
def update_output(value, comparison):
    min_value, max_value = value
    return f'선택된 유효 픽률 범위: {min_value:.2f}% ~ {max_value:.2f}%'


# Callback for updating RangeSlider's min, max, and value based on dropdowns
@app.callback(
    Output('pick-rate-slider', 'min'),
    Output('pick-rate-slider', 'max'),
    Output('pick-rate-slider', 'value'),
    [Input('version-dropdown', 'value'),
     Input('tier-dropdown', 'value'),
     Input('comparison-dropdown', 'value')]
)
def update_slider(version, tier, comparison):
    database = get_database()
    df = database[(tier, version)]

    # Calculate min and max for the slider
    min_value = df['Pick Rate'].min() if 'Pick Rate' in df.columns else 0
    max_value = df['Pick Rate'].max() if 'Pick Rate' in df.columns else 1

    # Set the slider value to span the entire range initially
    slider_value = [0.3, max_value]

    return min_value, max_value, slider_value


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('pick-rate-slider', 'value'),
     Input('version-dropdown', 'value'),
     Input('tier-dropdown', 'value'),
     Input('comparison-dropdown', 'value'),
     Input('role-dropdown', 'value'),
     Input('confirm-click-flag', 'data')],  # Add the confirm-click-flag input
    prevent_initial_call=True
)
def update_figure(selected_range, version, tier, comparison, role, confirm_flag):
    database = get_database()
    df = database[(tier, version)]

    filtered_df = df[(df['Pick Rate'] >= selected_range[0]) & (df['Pick Rate'] <= selected_range[1])]
    # Determine the color for the points based on the role
    if role != 'Whole':
        # If a specific role is selected, characters in that role will have a different color
        filtered_df['역할군'] = filtered_df['Character'].apply(lambda x: role_translation[role] if x in roles_mapping[role] else '전체')
    else:
        # If 'Whole' is selected, all characters have the same color
        filtered_df['역할군'] = '전체'

    if comparison == 'top3_vs_winrate':
        fig = plot_top3_vs_winrate(filtered_df, df, role, role_translation)
    elif comparison == 'pick_vs_win':
        fig = pick_pick_vs_win(filtered_df, df, role, role_translation)
    elif comparison == 'pick_vs_rp':
        fig = plot_pick_vs_rp(filtered_df, df, role, role_translation)
    elif comparison == 'rp_vs_win':
        fig = plot_rp_vs_win(filtered_df, df, role, role_translation)

    fig = customize_plot(fig)

    return fig


@app.callback(
    [Output('stored-selected-characters', 'data'),
     Output({'type': 'char-box', 'index': ALL}, 'style')],
    [Input({'type': 'char-box', 'index': ALL}, 'n_clicks'),
     Input('reset-modal', 'n_clicks')],
    [State({'type': 'char-box', 'index': ALL}, 'id'),
     State({'type': 'char-box', 'index': ALL}, 'style'),
     State('stored-selected-characters', 'data')],
    prevent_initial_call=True
)
def update_characters_and_styles(all_n_clicks, n_reset, all_ids, all_styles, stored_data):
    ctx = dash.callback_context
    triggered_id, triggered_prop = ctx.triggered[0]['prop_id'].split('.')

    # If the reset button was clicked, reset all styles to default and clear stored data
    if triggered_prop == 'n_clicks' and 'reset-modal' in triggered_id:
        return [], [default_character_style for _ in all_ids]

    # Initialize new_stored_data with stored_data or an empty list if None
    new_stored_data = stored_data or []

    # Initialize new_styles with all_styles or a list of default styles if None
    new_styles = all_styles if all_styles is not None else [default_character_style for _ in all_ids]

    # Proceed if the callback was triggered by a character box click
    if triggered_prop == 'n_clicks' and 'char-box' in triggered_id:
        # Identify which character box was clicked
        clicked_index = json.loads(triggered_id)["index"]
        character_name = roles_mapping['Reference'][clicked_index]

        # Toggle selection and styling
        if character_name in new_stored_data:
            # Deselect and reset style
            new_stored_data.remove(character_name)
            new_styles[clicked_index] = default_character_style
        else:
            # Select and update style
            new_stored_data.append(character_name)
            new_styles[clicked_index] = selected_character_style

    # Return the updated stored data and the styles for the character boxes
    return new_stored_data, new_styles


@app.callback(
    Output('modal-edit-user-defined-roles', 'is_open'),
    Output('confirm-click-flag', 'data'),
    Output('role-dropdown', 'value'),
    [Input('edit-user-defined-roles-button', 'n_clicks'),
     Input('confirm-modal', 'n_clicks'),
     Input('close-modal', 'n_clicks')],
    [State('modal-edit-user-defined-roles', 'is_open'),
     State('stored-selected-characters', 'data')]
)
def toggle_modal(n_open, n_confirm, n_close, is_open, stored_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update, dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "edit-user-defined-roles-button":
            return True, {'clicked': False}, dash.no_update
        elif button_id == "confirm-modal":
            if n_confirm:
                roles_mapping['User Defined'] = stored_data or []
                return False, {'clicked': True}, 'User Defined'
        elif button_id == "close-modal":
            if n_close:
                return False, {'clicked': False}, dash.no_update

    return is_open, {'clicked': False}, dash.no_update


@app.callback(
    Output('last-update-time', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_last_update_time(n):
    return f"마지막 업데이트 시각: {get_last_update_time()}"


@app.callback(
    Output('reset-modal', 'disabled'),
    [Input('stored-selected-characters', 'data')]
)
def toggle_reset_button(stored_data):
    # If stored_data is empty or None, disable the button
    return not stored_data


# Dash 애플리케이션 정의 및 실행
if __name__ == '__main__':
    # update_table_all()
    update_database()
    update_last_time()

    # 주기적 업데이트 스레드 시작
    update_thread = threading.Thread(target=run_periodic_update, daemon=True)
    update_thread.start()

    print("[Dash] Run...")
    app.run_server(debug=False)
