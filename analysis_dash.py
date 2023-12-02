import dash
import os
import numpy as np
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from bs4 import BeautifulSoup

from config import roles_mapping, role_translation


# Define some style settings
GLOBAL_FONT_FAMILY = "Helvetica Neue, Helvetica, Arial, sans-serif"
PRIMARY_COLOR = "#007BFF"
SECONDARY_COLOR = "#6c757d"
BACKGROUND_COLOR = "#f8f9fa"
TEXT_COLOR = "#212529"


def adjust_text_position(df, x_col, y_col, text_col):
    # The positions of the texts are initialized to the top center of the point
    positions = ['top center' for _ in range(len(df))]

    # Extracting coordinates for all points
    points = df[[x_col, y_col]].values
    # Estimating the width and height of text boxes
    # This is a placeholder; actual implementation should calculate based on text size and length
    text_box_width = max(df[text_col].apply(len)) * 0.02  # Width of the text box
    text_box_height = 0.05  # Height of the text box (assuming single line of text)
    
    # Define a function to create bounding boxes for each point
    def get_bounding_boxes(points, text_box_width, text_box_height):
        return [(x - text_box_width / 2, y - text_box_height / 2,
                 x + text_box_width / 2, y + text_box_height / 2) for x, y in points]
    
    bounding_boxes = get_bounding_boxes(points, text_box_width, text_box_height)
    
    # Function to check if two boxes overlap
    def boxes_overlap(box1, box2):
        return not (box1[2] < box2[0] or box1[0] > box2[2] or
                    box1[3] < box2[1] or box1[1] > box2[3])

    # Check each pair of boxes for overlap and adjust positions
    for i, box1 in enumerate(bounding_boxes):
        for j, box2 in enumerate(bounding_boxes):
            if i != j and boxes_overlap(box1, box2):
                # If they overlap, adjust positions
                if points[i][1] < points[j][1]:
                    # If point i is lower than point j, move the text of point i to the bottom
                    positions[i] = 'bottom center'
                else:
                    # If point i is higher than point j, move the text of point i to the top
                    positions[i] = 'top center'

    return positions



def customize_plot(fig):
    # Simplify gridlines
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='WhiteSmoke')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='WhiteSmoke')

    # Update layout for a cleaner look
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig


def parse_html(file_path):
    # Since the format of the data in the file is unknown, I will first open the file and read its content to understand its structure.
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Using BeautifulSoup to parse the HTML content
    soup = BeautifulSoup("".join(lines), 'html.parser')

    # Finding all rows in the table
    rows = soup.find_all('tr')

    # Define a function to extract text from a tag, stripping and replacing unwanted characters
    def extract_text(tag):
        text = tag.get_text(strip=True)
        if '%' in text:
            return text.split('%')[0]
        elif '#' in text:
            return text.replace('#', '')
        elif '-' in text:
            raise AttributeError
        return text

    # Parsing each row
    data = []
    for row in rows:
        # Finding all cells in the row
        cells = row.find_all('td')
        if len(cells) > 1:  # Making sure it's not a header or empty row
            try:
                # Extracting data from each cell
                character_name = extract_text(cells[1])  # Character name
                rp_gain = float(extract_text(cells[2]))  # RP Gain
                pick_rate = float(extract_text(cells[3]))  # Pick Rate
                win_rate = float(extract_text(cells[4]))  # Win Rate
                top_3 = float(extract_text(cells[5]))  # TOP 3
                average_rank = float(extract_text(cells[6]))  # Average Rank
                damage = int(extract_text(cells[7]).replace(',', ''))  # Damage
                average_tk = float(extract_text(cells[8]))  # Average TK
                player_kills = float(extract_text(cells[9]))  # Player Kills
                animal_kills = float(extract_text(cells[10]))  # Animal Kills

                # Adding the extracted data to the list
                data.append([character_name, rp_gain, pick_rate, win_rate, top_3, average_rank, damage, average_tk, player_kills, animal_kills, 100 * (win_rate / top_3)])
            except AttributeError:
                continue

    # Creating a DataFrame from the parsed data
    columns = ['Character', 'RP Gain', 'Pick Rate', 'Win Rate', 'TOP 3', 'Average Rank', 'Damage', 'Average TK', 'Player Kills', 'Animal Kills', 'Win Rate / Top 3']
    df = pd.DataFrame(data, columns=columns)
    return df

database = {}
from config import url_mapping
for key, url in url_mapping.items():
    tier, version = key
    database[key] = parse_html(os.path.join('data', f"('{tier}', '{version}').html"))


app = dash.Dash(__name__)

app.layout = html.Div([
    # Fixed Div for selection bars
    html.Div([
        # Dropdown for Version selection
        dcc.Dropdown(
            id='version-dropdown',
            options=[
                {'label': '이전 버전', 'value': 'prevPatch'},
                {'label': '현재 버전', 'value': 'currentPatch'},
                {'label': '현재 버전 (최근 3일)', 'value': '3day'},
                {'label': '현재 버전 (최근 7일)', 'value': '7day'}
            ],
            value='currentPatch',  # Default value
            clearable=False,
            style={'width': '30%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center'}
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
            style={'width': '30%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center'}
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
            ],
            value='Whole',  # Default value
            clearable=False,
            style={'width': '40%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center'}
        ),
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
            style={'width': '60%', 'display': 'inline-block', 'align-items': 'center', 'justify-content': 'center'}
        ),
    ], style={
        'position': 'fixed', 
        'top': '4px', 
        'left': 0, 
        'right': 0, 
        'background-color': 'white', 
        'z-index': '9999',  # Set a high z-index to ensure it's on top
        # 'border-bottom': 'solid 1px #d6d6d6', 
        # 'padding': '3px',
        'box-shadow': '0 2px 2px -2px gray'  # Optional: adds shadow for better separation
    }),

    # Spacer for content below fixed div
    html.Div(style={'height': '55px'}),

    # Rest of the layout
    html.Div(id='slider-value-container', 
             style={
                    'text-align': 'left', 
                    'margin-top': '30px',
                    'color': TEXT_COLOR,
                    'font-family': GLOBAL_FONT_FAMILY
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
    ], style={'text-align': 'center', 'margin-top': '20px'}),
    dcc.Graph(
        id='scatter-plot',
        config={
            'scrollZoom': True  # This enables the scroll zoom
        },
        style={'width': '100vw', 'height': '82vh'}  # This makes the graph fill the screen
    ),
], style={
    'font-family': GLOBAL_FONT_FAMILY,
    'background-color': BACKGROUND_COLOR
}
)


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
     Input('role-dropdown', 'value')],  # Add the role-dropdown input
    prevent_initial_call=True
)
def update_figure(selected_range, version, tier, comparison, role):
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
        fig = plot_top3_vs_winrate(filtered_df, df, role)
    elif comparison == 'pick_vs_win':
        fig = pick_pick_vs_win(filtered_df, df, role)
    elif comparison == 'pick_vs_rp':
        fig = plot_pick_vs_rp(filtered_df, df, role)
    elif comparison == 'rp_vs_win':
        fig = plot_rp_vs_win(filtered_df, df, role)

    fig = customize_plot(fig)

    return fig


def plot_top3_vs_winrate(filtered_df, df, role):
    sizes = 3 + (filtered_df['Pick Rate'] - df['Pick Rate'].min()) / (df['Pick Rate'].max() - df['Pick Rate'].min()) * 120

    fig = px.scatter(filtered_df, x='TOP 3', y='Win Rate / Top 3', text='Character', size=sizes,
                     color='역할군',  # Use the color column for point colors
                     color_discrete_map={role_translation[role]: "Crimson", "전체": "LightSkyBlue"},
                     custom_data=[filtered_df['Pick Rate']])
    
    # Add the weighted average lines
    weighted_avg_win_per_third = (df['Pick Rate'] * df['Win Rate / Top 3']).sum() / df['Pick Rate'].sum() if df['Pick Rate'].sum() != 0 else 0
    weighted_avg_top_3 = (df['Pick Rate'] * df['TOP 3']).sum() / df['Pick Rate'].sum() if df['Pick Rate'].sum() != 0 else 0

    fig.add_hline(y=weighted_avg_win_per_third, line_dash="dot",
                    annotation_text=f"<b>3등 확보 시 평균 승률: {weighted_avg_win_per_third:.2f}%</b>",
                    annotation_position="bottom right", line_color="orange",
                    annotation_font={'size': 12, 'color': 'orange'})

    fig.add_vline(x=weighted_avg_top_3, line_dash="dot",
                    annotation_text=f"<b>평균 3등 확보 비율: {weighted_avg_top_3:.2f}%</b>",
                    annotation_position="top right", line_color="green",
                    annotation_font={'size': 12, 'color': 'green'})

        
    # Set layout details
    fig.update_layout(
            xaxis_title='<b>Top 3 비율 (%)</b>',
            yaxis_title='<b>Top 3 시 승률 (%)</b>',
            plot_bgcolor='white',
            hovermode='closest',
        )

    text_positions = adjust_text_position(df, 'TOP 3', 'Win Rate / Top 3', 'Character')
    for trace, position in zip(fig.data, text_positions):
        trace.update(textposition=position)

    # Customize hover info for each trace (point)
    fig.update_traces(
        hovertemplate='<b>%{text}</b><br>Top 3 비율: %{x:.2f}%<br>Top 3 시 승률: %{y:.2f}%<br>픽률: %{customdata[0]:.2f}%<extra></extra>'
    )

    # Customize the appearance of the hover box
    fig.update_traces(hoverlabel=dict(bgcolor='RoyalBlue', font_size=14, font_family='Arial'))

    return fig


def pick_pick_vs_win(filtered_df, df, role):
    # Calculate the weighted average win rate
    weighted_sum = (df['Pick Rate'] * df['Win Rate']).sum()
    total_pick_rate = df['Pick Rate'].sum()
    weighted_avg_win_rate = weighted_sum / total_pick_rate if total_pick_rate != 0 else 0

    # Create the scatter plot
    sizes = 3 + (filtered_df['Pick Rate'] - df['Pick Rate'].min()) / (df['Pick Rate'].max() - df['Pick Rate'].min()) * 120
    fig = px.scatter(filtered_df, x='Pick Rate', y='Win Rate', text='Character', size=sizes,
                     color='역할군',  # Use the color column for point colors
                     color_discrete_map={role_translation[role]: "Crimson", "전체": "LightSkyBlue"},)

    fig.add_hline(y=weighted_avg_win_rate, line_dash="dot",
                    annotation_text=f"<b>전체 평균 승률: {weighted_avg_win_rate:.2f}%</b>",
                    annotation_position="bottom right", line_color="orange",
                    annotation_font={'size': 12, 'color': 'orange'})

    # Customize hover info for each trace (point)
    for trace in fig.data:
        trace.hoverinfo = 'text'
        trace.hovertemplate = '<b>%{text}</b><br>픽률: %{x:.2f}%<br>승률: %{y:.2f}%<extra></extra>'

    # Customize layout for readability
    fig.update_layout(
        xaxis_title='<b>픽률 (%)</b>',
        yaxis_title='<b>승률 (%)</b>',
        plot_bgcolor='white',
        hovermode='closest'
    )

    text_positions = adjust_text_position(filtered_df, 'Pick Rate', 'Win Rate', 'Character')
    for trace, position in zip(fig.data, text_positions):
        trace.update(textposition=position)
    return fig


def plot_pick_vs_rp(filtered_df, df, role):
    weighted_sum = (df['Pick Rate'] * df['RP Gain']).sum()
    total_pick_rate = df['Pick Rate'].sum()
    weighted_avg_rpgain = weighted_sum / total_pick_rate if total_pick_rate != 0 else 0

    # Create the scatter plot
    sizes = 3 + (filtered_df['Pick Rate'] - df['Pick Rate'].min()) / (df['Pick Rate'].max() - df['Pick Rate'].min()) * 120
    fig = px.scatter(filtered_df, x='Pick Rate', y='RP Gain', text='Character', size=sizes,
                     color='역할군',  # Use the color column for point colors
                     color_discrete_map={role_translation[role]: "Crimson", "전체": "LightSkyBlue"},)

    fig.add_hline(y=weighted_avg_rpgain, line_dash="dot",
                    annotation_text=f"<b>전체 평균 RP 획득량: {weighted_avg_rpgain:.2f}</b>",
                    annotation_position="bottom right", line_color="orange",
                    annotation_font={'size': 12, 'color': 'orange'})

    # Customize hover info for each trace (point)
    for trace in fig.data:
        trace.hoverinfo = 'text'
        trace.hovertemplate = '<b>%{text}</b><br>픽률: %{x:.2f}%<br>RP 획득량: %{y:.2f}<extra></extra>'

    # Customize layout for readability
    fig.update_layout(
        # title='픽률 vs RP 획득량',
        xaxis_title='<b>픽률 (%)</b>',
        yaxis_title='<b>RP 획득량</b>',
        plot_bgcolor='white',
        hovermode='closest'
    )

    text_positions = adjust_text_position(filtered_df, 'Pick Rate', 'RP Gain', 'Character')
    for trace, position in zip(fig.data, text_positions):
        trace.update(textposition=position)
    return fig


def plot_rp_vs_win(filtered_df, df, role):
    # Create the scatter plot
    sizes = 3 + (filtered_df['Pick Rate'] - df['Pick Rate'].min()) / (df['Pick Rate'].max() - df['Pick Rate'].min()) * 120
    fig = px.scatter(filtered_df, x='RP Gain', y='Win Rate', text='Character', size=sizes,
                     color='역할군',  # Use the color column for point colors
                     color_discrete_map={role_translation[role]: "Crimson", "전체": "LightSkyBlue"},
                     custom_data=[filtered_df['Pick Rate']])

    total_pick_rate = df['Pick Rate'].sum()

    weighted_sum = (df['Pick Rate'] * df['RP Gain']).sum()
    weighted_avg_rpgain = weighted_sum / total_pick_rate if total_pick_rate != 0 else 0
    fig.add_vline(x=weighted_avg_rpgain, line_dash="dot",
                  annotation_text=f"<b>전체 평균 RP 획득량: {weighted_avg_rpgain:.2f}</b>",
                  annotation_position="bottom right", line_color="orange",
                  annotation_font={'size': 12, 'color': 'orange'})
    
    weighted_sum = (df['Pick Rate'] * df['Win Rate']).sum()
    weighted_avg_rpgain = weighted_sum / total_pick_rate if total_pick_rate != 0 else 0
    fig.add_hline(y=weighted_avg_rpgain, line_dash="dot",
                  annotation_text=f"<b>전체 평균 승률: {weighted_avg_rpgain:.2f}</b>",
                  annotation_position="bottom right", line_color="green",
                  annotation_font={'size': 12, 'color': 'green'})


    # Customize hover info for each trace (point)
    fig.update_traces(
        hovertemplate='<b>%{text}</b><br>RP 획득량: %{x:.2f}<br>승률: %{y:.2f}%<br>픽률: %{customdata[0]:.2f}%<extra></extra>'
    )

    # Customize layout for readability
    fig.update_layout(
        xaxis_title='<b>RP 획득량</b>',
        yaxis_title='<b>승률 (%)</b>',
        plot_bgcolor='white',
        hovermode='closest'
    )

    text_positions = adjust_text_position(filtered_df, 'RP Gain', 'Win Rate', 'Character')
    for trace, position in zip(fig.data, text_positions):
        trace.update(textposition=position)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)