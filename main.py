from flask import Flask, render_template, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)


# ======================
# Load Contest Dataset
# ======================

def load_data():
    try:
        all_contests = pd.read_csv("data/all_contests.csv")

        all_contests['start_date'] = pd.to_datetime(
            all_contests['start_date'],
            errors='coerce'
        )

        all_contests.dropna(
            subset=['start_date'],
            inplace=True
        )

        return all_contests

    except Exception as e:
        print("Error:", e)
        return None


# ======================
# Home Page
# ======================

@app.route('/')
def index():

    all_contests = load_data()

    if all_contests is None:
        return "Error loading data",500

    now = pd.Timestamp.now()

    upcoming = (
        all_contests[
            all_contests['start_date'] > now
        ]
        .sort_values("start_date")
    )

    total = len(all_contests)

    upcoming_count = len(upcoming)

    past_count = total - upcoming_count

    platform_counts = (
        all_contests['platform']
        .value_counts()
        .to_dict()
    )

    duration_stats = (
        all_contests
        .groupby("platform")['duration_min']
        .mean()
        .round(1)
        .to_dict()
    )

    upcoming_list = (
        upcoming
        .head(10)
        .to_dict("records")
    )

    return render_template(
        "index.html",

        total=total,

        upcoming_count=upcoming_count,

        past_count=past_count,

        platform_counts=platform_counts,

        duration_stats=duration_stats,

        upcoming_contests=upcoming_list
    )


# ======================
# Upcoming Page
# ======================

@app.route('/upcoming')
def all_upcoming():

    all_contests = load_data()

    if all_contests is None:
        return "Error loading data",500

    now = pd.Timestamp.now()

    upcoming = (
        all_contests[
            all_contests['start_date'] > now
        ]
        .sort_values("start_date")
    )

    upcoming_list = upcoming.to_dict("records")

    return render_template(
        "upcoming.html",
        upcoming_contests=upcoming_list
    )


# ======================
# Insights API
# ======================

@app.route('/insights')
def insights():

    all_contests = load_data()

    if all_contests is None:
        return jsonify(
            {"error":"failed"}
        )

    monthly = (
        all_contests
        .groupby(
            all_contests[
                'start_date'
            ].dt.month
        )
        .size()
    )

    monthly = monthly.to_dict()

    platform_counts = (
        all_contests['platform']
        .value_counts()
        .to_dict()
    )

    avg_duration = (
        all_contests
        .groupby("platform")[
            'duration_min'
        ]
        .mean()
        .round(1)
        .to_dict()
    )

    return jsonify({

        "monthly_contests":
        monthly,

        "platform_counts":
        platform_counts,

        "average_duration":
        avg_duration
    })


# ======================
# Run
# ======================

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
    