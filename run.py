import uuid
import datetime
import threading
import dash
import copy
import time
import threading
import json
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc

from config import GLOBAL_FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR
from config import default_roles_mapping
from config import role_translation
import dash_bootstrap_components as dbc
from update_table import update_table_all, update_database, update_last_time, run_periodic_update, get_last_update_time, get_database
from plot import customize_plot, plot_top3_vs_winrate, pick_pick_vs_win, plot_pick_vs_rp, plot_rp_vs_win, plot_tk_vs_top3
from styles import dropdown_style, button_style, container_style, default_character_style, selected_character_style


# 세션 정보를 저장할 딕셔너리
running_session_ids = {}

def generate_session_id():
    return str(uuid.uuid4())

def update_session_activity(session_id):
    running_session_ids[session_id] = datetime.datetime.now()

def remove_expired_sessions():
    def trim_log_file(file_path, max_lines=200000):
        with open(file_path, 'r', encoding='UTF-8') as file:
            lines = file.readlines()

        if len(lines) > max_lines:
            with open(file_path, 'w', encoding='UTF-8') as file:
                file.writelines(lines[-max_lines:])

    while True:
        current_time = datetime.datetime.now()
        expired_sessions = [session_id for session_id, last_active in running_session_ids.items()
                            if (current_time - last_active).total_seconds() > 300]
        for session_id in expired_sessions:
            del running_session_ids[session_id]

        # running_session_ids를 파일에 로깅
        with open("session_log.txt", "a", encoding='UTF-8') as log_file:
            now = datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S")
            log_file.write(f"[{now}]: 현재 활성 세션 - {list(running_session_ids.keys())}\n")

        # Check and trim the log file if it exceeds 200,000 lines
        trim_log_file("session_log.txt")

        time.sleep(300)  # 매 300초마다 실행

def generate_character_grid(characters, selected_characters):
    return html.Div(
        [dbc.Row(
            [dbc.Col(
                html.Div(
                    character,
                    id={'type': 'char-box', 'index': i},
                    className='character-box',
                    style=selected_character_style if character in selected_characters else default_character_style
                ),
                width='auto'
            ) for i, character in enumerate(characters)],
            className="justify-content-between",
        )],
        className="container"
    )


# Add custom CSS class for dropdown hover state in your external CSS file or within app layout using the style tag
external_css = [
    dbc.themes.BOOTSTRAP,
    'https://codepen.io/chriddyp/pen/bWLwgP.css',  # Example external CSS
    '/assets/custom_styles.css'  # Path to your custom CSS file
]
app = dash.Dash(__name__, external_stylesheets=external_css, title='ER Plot')
server = app.server


app.layout = html.Div([
    # Fixed Div for selection bars
    dcc.Store(id='session_roles_mapping', storage_type='memory'),
    dcc.Store(id='session-id', storage_type='session'),
    dcc.Interval(id='init-interval', interval=1, n_intervals=0),
    html.Div([
        html.Div(id='selected-characters', style={'display': 'none'}),
        dcc.Store(id='stored-selected-characters', storage_type='memory'),
        # Dropdown for Comparison selection
        dcc.Dropdown(
            id='comparison-dropdown',
            options=[
                {'label': '픽률 vs 승률', 'value': 'pick_vs_win'},
                {'label': '픽률 vs RP 획득량', 'value': 'pick_vs_rp'},
                {'label': 'Top 3 비율 vs Top 3 확보 시 승률', 'value': 'top3_vs_winrate'},
                {'label': '평균 팀킬 수 vs Top 3 비율', 'value': 'tk_vs_top3'},
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
                id='modal-body',
                style={'maxHeight': 'calc(100vh - 210px)', 'overflowY': 'auto'}
            ),
            dbc.ModalFooter([
                dbc.Button("확인", id="confirm-modal", className="ml-auto", n_clicks=0, size="lg"),
                dbc.Button("초기화", id="reset-modal", className="ml-auto", n_clicks=0, size="lg", disabled=True),
                dbc.Button("취소", id="close-modal", className="ml-auto", n_clicks=0, size="lg"),
            ]),
        ],
        id="modal-edit-user-defined-roles",
        is_open=False,
        style={"zIndex": 1100, "maxWidth": "100vw"}
    ),

    dcc.Store(id='confirm-click-flag', data={'clicked': False}, storage_type='memory'),

    # Container for slider value and slider
    html.Div([
        # Container for displaying the slider value
        # html.Div(id='slider-value-container', children='Selected pick rate will be displayed here', style={
        #             'textAlign': 'left',
        #             'marginLeft': '10px',
        #             'marginTop': '-16px',  # Reduced from 30px to 10px
        #             'color': TEXT_COLOR,
        #             'fontFamily': GLOBAL_FONT_FAMILY,
        #             'fontSize': '14px'
        #         }),
        html.Div(id='slider-value-container', children='Selected pick rate will be displayed here', style={
            'textAlign': 'center',  # Center align text
            'marginTop': '-16px',
            'marginLeft': '5px',
            # 'margin': '0 10px',  # Add margin to the left and right
            'padding': '5px 10px',  # Add padding inside the container
            'background-color': '#f8f9fa',  # Light grey background
            'border-radius': '5px',  # Rounded corners
            'border': '1px solid #dee2e6',  # Light grey border
            'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',  # Subtle shadow
            'display': 'inline-block',  # Allow the div to size to content
            'color': TEXT_COLOR,
            'fontFamily': GLOBAL_FONT_FAMILY,
            # 'fontWeight': 'bold',  # Bold font weight
            'fontSize': '14px'
        }),

        # Container for the slider
        html.Div([
           dcc.RangeSlider(
            id='pick-rate-slider',
            min=0,  # Default minimum
            max=1,  # Default maximum
            value=[0, 1],  # Default value
            updatemode='drag',
            step=0.02,
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        ], id='slider-container', style={
            'flex': '2',  # Slider can take up twice as much space
            # 'padding': '0 10px',  # Add some padding
        }),
    ], style={
        'display': 'flex',  # Use Flexbox
        'align-items': 'center',  # Align items vertically in the center
        'justify-content': 'start',  # Start alignment
        'flex-wrap': 'nowrap',  # Prevent wrapping to a new line
        'width': '100%',  # Ensure the container takes full width
        'box-sizing': 'border-box',  # Include padding in the width calculation
    }),

    html.Div([
        # Customized Graph Style
        dcc.Graph(
            id='scatter-plot',
            config={'scrollZoom': True, 'displayModeBar': True,
                    'showTips': False, 'displaylogo': False,
                    'dragmode': 'pan',
                    'modeBarButtonsToRemove': ['lasso2d', 'resetScale2d', 'select']},  # Hide modebar if not necessary
            style={'width': '100%', 'height': '88vh'}  # Adjusted for responsiveness
        ),
        html.Div(
            id='last-update-time',
            style={
                'textAlign': 'left',
                'color': TEXT_COLOR,
                'fontFamily': GLOBAL_FONT_FAMILY,
                'fontSize': '12px',
                # 'paddingLeft': '1px',
                "zIndex": 1100,
                "left": "10px",
                "position": "fixed",
            }
        ),
        html.Div(
            html.A(
                "Manual Page",
                href="https://github.com/mikigom/ER_plot/wiki",
                target="_blank",
                style={
                    'textAlign': 'right',
                    'display': 'block',
                    'color': PRIMARY_COLOR,
                    'fontFamily': GLOBAL_FONT_FAMILY,
                    'fontSize': '14px',
                    'paddingBottom': '4px',
                    # 'paddingRight': '5px',
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
    ),
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


@app.callback(
    Output('pick-rate-slider', 'min'),
    Output('pick-rate-slider', 'max'),
    Output('pick-rate-slider', 'value'),
    Output('pick-rate-slider', 'marks'),
    [Input('version-dropdown', 'value'),
     Input('tier-dropdown', 'value')]
)
def update_slider(version, tier):
    database = get_database()
    df_selected = database[(tier, version)]

    # Calculate quantiles for the slider
    quantile_values = df_selected['Pick Rate'].quantile([0.25, 0.5, 0.75])

    # Find the closest characters corresponding to the quantiles
    characters_at_quantiles = {}
    for quantile, value in quantile_values.items():
        closest_index = (df_selected['Pick Rate'] - value).abs().idxmin()
        characters_at_quantiles[value] = df_selected.loc[closest_index, 'Character']

    # Calculate min and max for the slider
    min_value = df_selected['Pick Rate'].min() if 'Pick Rate' in df_selected.columns else 0
    max_value = df_selected['Pick Rate'].max() if 'Pick Rate' in df_selected.columns else 1

    # Find the characters corresponding to the min and max pick rate
    min_char = df_selected.loc[df_selected['Pick Rate'].idxmin(), 'Character']
    max_char = df_selected.loc[df_selected['Pick Rate'].idxmax(), 'Character']

    # Create the marks with character labels
    marks = {
        str(min_value): {'label': min_char, 'style': {'color': '#f50'}},
        **{str(key): {'label': value, 'style': {'color': '#555'}} for key, value in characters_at_quantiles.items()},
        str(max_value): {'label': max_char, 'style': {'color': '#77b0b1'}}
    }

    # Adjust the slider value if necessary
    slider_value = [0.3, 1.1 * max_value]

    return 0, 1.1 * max_value, slider_value, marks


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('pick-rate-slider', 'value'),
     Input('version-dropdown', 'value'),
     Input('tier-dropdown', 'value'),
     Input('comparison-dropdown', 'value'),
     Input('role-dropdown', 'value'),
     Input('confirm-click-flag', 'data')],  # Add the confirm-click-flag input
    [State('session_roles_mapping', 'data')],
    prevent_initial_call=True
)
def update_figure(selected_range, version, tier, comparison, role, confirm_flag, session_roles_mapping):
    if session_roles_mapping is None:
        session_roles_mapping = copy.deepcopy(default_roles_mapping)

    database = get_database()
    df = database[(tier, version)]

    filtered_df = df[(df['Pick Rate'] >= selected_range[0]) & (df['Pick Rate'] <= selected_range[1])]
    filtered_df_copied = copy.deepcopy(filtered_df)
    if role == 'User Defined':
        filtered_df_copied.loc[:, '역할군'] = filtered_df['Character'].apply(
            lambda x: role_translation[role] if any(item in x for item in session_roles_mapping[role]) else '전체'
        )
    elif role != 'Whole':
        # If a specific role is selected, characters in that role will have a different color
        filtered_df_copied.loc[:, '역할군'] = filtered_df['Character'].apply(lambda x: role_translation[role] if x in session_roles_mapping[role] else '전체')
    else:
        # If 'Whole' is selected, all characters have the same color
        filtered_df_copied.loc[:, '역할군'] = '전체'
    filtered_df = filtered_df_copied

    filtered_df.loc[:, 'sort_column'] = filtered_df['역할군'] == '전체'
    filtered_df.sort_values(by='sort_column', inplace=True, ascending=False)
    filtered_df.drop('sort_column', axis=1, inplace=True)

    if comparison == 'top3_vs_winrate':
        fig = plot_top3_vs_winrate(filtered_df, df, role, role_translation)
    elif comparison == 'pick_vs_win':
        fig = pick_pick_vs_win(filtered_df, df, role, role_translation)
    elif comparison == 'pick_vs_rp':
        fig = plot_pick_vs_rp(filtered_df, df, role, role_translation)
    elif comparison == 'rp_vs_win':
        fig = plot_rp_vs_win(filtered_df, df, role, role_translation)
    elif comparison == 'tk_vs_top3':
        fig = plot_tk_vs_top3(filtered_df, df, role, role_translation)

    fig = customize_plot(fig)

    return fig


@app.callback(
    [Output('stored-selected-characters', 'data'),
     Output({'type': 'char-box', 'index': ALL}, 'style')],
    [Input({'type': 'char-box', 'index': ALL}, 'n_clicks'),
     Input('reset-modal', 'n_clicks'),
     Input('modal-edit-user-defined-roles', 'is_open'),],
    [State({'type': 'char-box', 'index': ALL}, 'id'),
     State({'type': 'char-box', 'index': ALL}, 'style'),
     State('stored-selected-characters', 'data'),
     State('session_roles_mapping', 'data')],
    prevent_initial_call=True
)
def update_characters_and_styles(all_n_clicks, n_reset, is_open, all_ids, all_styles, stored_data, session_roles_mapping):
    if session_roles_mapping is None:
        session_roles_mapping = copy.deepcopy(default_roles_mapping)

    ctx = dash.callback_context
    triggered_id, triggered_prop = ctx.triggered[0]['prop_id'].split('.')

    # If the reset button was clicked, reset all styles to default and clear stored data
    if triggered_prop == 'n_clicks' and 'reset-modal' in triggered_id:
        return None, [default_character_style for _ in all_ids]

    # Initialize new_stored_data with stored_data or an empty list if None
    new_stored_data = stored_data or []

    # Initialize new_styles with all_styles or a list of default styles if None
    new_styles = all_styles if all_styles is not None else [default_character_style for _ in all_ids]

    # Proceed if the callback was triggered by a character box click
    if triggered_prop == 'n_clicks' and 'char-box' in triggered_id:
        # Identify which character box was clicked
        clicked_index = json.loads(triggered_id)["index"]
        character_name = session_roles_mapping['Reference'][clicked_index]

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
    Output('session_roles_mapping', 'data'),
    [Input('edit-user-defined-roles-button', 'n_clicks'),
     Input('confirm-modal', 'n_clicks'),
     Input('close-modal', 'n_clicks')],
    [State('modal-edit-user-defined-roles', 'is_open'),
     State('stored-selected-characters', 'data'),
     State('session_roles_mapping', 'data')],
    prevent_initial_call=True
)
def toggle_modal(n_open, n_confirm, n_close, is_open, stored_data, session_roles_mapping):
    if session_roles_mapping is None:
        session_roles_mapping = copy.deepcopy(default_roles_mapping)

    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, {'clicked': False}, 'Whole', session_roles_mapping

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "edit-user-defined-roles-button":
        return True, {'clicked': False}, dash.no_update, session_roles_mapping
    elif button_id == "confirm-modal":
        if n_confirm:
            updated_roles_mapping = session_roles_mapping.copy()
            updated_roles_mapping['User Defined'] = stored_data or []
            return False, {'clicked': True}, 'User Defined', updated_roles_mapping
    elif button_id == "close-modal":
        return False, {'clicked': False}, dash.no_update, session_roles_mapping

    return is_open, {'clicked': False}, dash.no_update, session_roles_mapping


@app.callback(
    Output('modal-body', 'children'),
    [Input('stored-selected-characters', 'data')],
    prevent_initial_call=True
)
def update_modal_content(selected_characters):
    if selected_characters is None:
        selected_characters = []

    return generate_character_grid(default_roles_mapping['Reference'], selected_characters)


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


@app.callback(
    Output('session-id', 'data'),
    [Input('scatter-plot', 'figure')],
    [State('session-id', 'data')]
)
def manage_session(figure, existing_session_id):
    if existing_session_id is None:
        new_session_id = generate_session_id()
        update_session_activity(new_session_id)
        return new_session_id
    else:
        update_session_activity(existing_session_id)
        return existing_session_id


# Dash 애플리케이션 정의 및 실행
if __name__ == '__main__':
    update_database()
    update_last_time()

    # 주기적 업데이트 스레드 시작
    update_thread = threading.Thread(target=run_periodic_update, daemon=True)
    update_thread.start()

    # 세션 만료 처리 스레드 시작
    expiration_thread = threading.Thread(target=remove_expired_sessions, daemon=True)
    expiration_thread.start()

    print("[Dash] Run...")
    context = ('certs/local.crt','certs/local.key')
    app.run_server(debug=False, host='0.0.0.0', port=80)
