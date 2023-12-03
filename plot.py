import plotly.express as px


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

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="left",
        x=0.01,
        bgcolor="GhostWhite",
        bordercolor="LightSteelBlue",
        borderwidth=1
    ))

    fig.update_layout(legend_title_text='')
    return fig


def plot_top3_vs_winrate(filtered_df, df, role, role_translation):
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
    # fig.update_traces(hoverlabel=dict(bgcolor='RoyalBlue', font_size=14, font_family='Arial'))

    return fig


def pick_pick_vs_win(filtered_df, df, role, role_translation):
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


def plot_pick_vs_rp(filtered_df, df, role, role_translation):
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


def plot_rp_vs_win(filtered_df, df, role, role_translation):
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
