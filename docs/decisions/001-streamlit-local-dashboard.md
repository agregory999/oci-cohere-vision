# 001: Use Streamlit for the local dashboard

The application is a single-screen, local, internal-style exploration tool with no public API
or multi-user authorization requirement. Streamlit keeps the UI and Python workflow compact
without introducing a browser framework. The UI remains thin, and OCI interaction stays behind
the `services/oci_vision.py` adapter so a different delivery format can reuse it later.
