#  Copyright (c) 2021. Bram Vonk, Enexis

from src.plot.dashboard import build_dashboard

if __name__ == "__main__":
    # start with python script.py
    dashboard = build_dashboard()
    dashboard.show(port=8000)