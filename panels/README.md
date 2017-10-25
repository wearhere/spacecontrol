To create a new panel, implement the abstract base class panel_client.PanelStateBase.

Run run your panel, modify run_panel.py:
    - import your panel class
    - add your panel class to PANELS
    - [opionally] add support for other command line flags.
    - run with './run_panel.py --panel_type ${YOUR_PANEL}'