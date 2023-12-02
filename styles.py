from config import GLOBAL_FONT_FAMILY, PRIMARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR


# Define the button style with flexbox layout
button_style = {
    'display': 'inline-flex',  # Use inline-flex so the button does not stretch to fill the container
    'alignItems': 'center',  # Center children along the cross axis
    'justifyContent': 'center',  # Center children along the main axis
    'padding': '6px 12px',
    'fontSize': '16px',
    'borderRadius': '5px',
    'backgroundColor': PRIMARY_COLOR,
    'color': 'white',
    'border': 'none',
    'cursor': 'pointer',
    'height': '38px',  # Set a fixed height if needed, adjust accordingly
    'lineHeight': '1',  # This ensures the text inside the button is not affected by line height
}

# Define the container style
container_style = {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'flex-start',
    'height': '100%',
    'marginTop': '-8px'
}

# Dropdown style for default state
dropdown_style = {
    'width': '100%', 'minWidth': '100px', 'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center',
    'cursor': 'pointer',  # Change cursor to indicate clickable
    'transition': 'all 0.3s ease',  # Smooth transition for any changes
}

# Dropdown style for hover state
dropdown_hover_style = {
    'width': '100%', 'minWidth': '100px', 'display': 'inline-block', 'alignItems': 'center', 'justifyContent': 'center',
    'backgroundColor': '#e8f0fe',  # Slightly lighter background to indicate hover
    'boxShadow': '0 2px 4px 0 rgba(0,0,0,0.2)',  # Subtle shadow to lift the dropdown
}

default_character_style = {
    'fontSize': '13px',
    'border': '1px solid #ddd',
    'padding': '0.3rem',
    'marginBottom': '0.3rem',
    'textAlign': 'center',
    'cursor': 'pointer',
    'backgroundColor': 'white'
}

selected_character_style = {
    'fontSize': '13px',
    'border': '1px solid #007BFF',  # Highlight the border to indicate selection
    'padding': '0.3rem',
    'marginBottom': '0.3rem',
    'textAlign': 'center',
    'cursor': 'pointer',
    'backgroundColor': '#e7f3ff'  # Light blue background for selected items
}
