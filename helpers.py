# helpers.py
# Allow to detect if we are on host url or deployed on cloud. 

from flask import request, url_for

def get_scheme():
    if request.host.startswith('127.0.0.1') or request.host.startswith('localhost'):
        return 'http'
    else:
        return 'https'

def get_url(endpoint, **values):
    scheme = get_scheme()
    return url_for(endpoint, _external=True, _scheme=scheme, **values)

def interpolate_color(value, start_color, end_color):
    return [
        int(start_color[i] + (end_color[i] - start_color[i]) * value)
        for i in range(3)
    ]

def get_color(mean_score):
    try:
        mean_score = float(mean_score)  # Ensure mean_score is a float
    except ValueError:
        mean_score = 0.0  # Default to 0 if conversion fails

    normalized_score = mean_score / 10.0

    # Define color stops for red, yellow, and green
    color_stops = [
        (0.0, (255, 0, 0)),    # Red
        (0.5, (255, 255, 0)),  # Yellow
        (1.0, (0, 255, 0)),    # Green
    ]

    # Find the two color stops the score is between
    for i in range(len(color_stops) - 1):
        if color_stops[i][0] <= normalized_score <= color_stops[i + 1][0]:
            value = (normalized_score - color_stops[i][0]) / (color_stops[i + 1][0] - color_stops[i][0])
            color = interpolate_color(value, color_stops[i][1], color_stops[i + 1][1])
            return f"rgb({color[0]}, {color[1]}, {color[2]})"

    # Default to the last color stop if something goes wrong
    return f"rgb{color_stops[-1][1]}"
