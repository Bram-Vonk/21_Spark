#  Copyright (c) 2021. Bram Vonk, Enexis

import panel as pn

def build_dashboard():
     return pn.pane.Markdown("Hello World")

if __name__.startswith("bokeh"):
    # start with panel serve script.py
    dashboard = build_dashboard()
    dashboard.servable()
if __name__ == "__main__":
    # start with python script.py
    dashboard = build_dashboard()
    dashboard.show(port=5007)