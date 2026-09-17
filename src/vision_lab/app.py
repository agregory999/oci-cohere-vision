import hashlib
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from vision_lab.client import analyze_image, validate_image
from vision_lab.config import LabError, Settings
from vision_lab.prompts import PROMPTS

PROJECT_ROOT = Path(__file__).parents[2]
load_dotenv(PROJECT_ROOT / "run" / ".env")
load_dotenv(PROJECT_ROOT / ".env")  # Legacy local-only fallback.
st.set_page_config(page_title="Vision Lab · OCI", page_icon="◈", layout="wide")
settings = Settings.from_env()

st.title("Vision Lab")
st.caption("Explore what Cohere Command A Vision can tell you about an image.")
with st.sidebar:
    st.subheader("Connection")
    st.text(settings.region)
    st.caption(settings.model_id)
    st.caption("On-demand inference · up to 1,500 output tokens")
    if settings.compartment_id:
        st.caption("Compartment configured. Access is checked when you analyze.")
    else:
        st.warning("Set OCI_COMPARTMENT_ID in .env before analyzing.")
    st.divider()
    st.caption("Uploads stay in this local app until you press Analyze image. "
               "Then the image and question are sent to OCI. This app does not save them to disk.")
    st.caption("Suggested labels are generated descriptions, not calibrated detection scores.")

left, right = st.columns([1, 1.25], gap="large")
with left:
    st.subheader("1. Choose an image")
    upload = st.file_uploader("PNG or JPEG · up to 5 MB", type=["png", "jpg", "jpeg"])
    data = upload.getvalue() if upload else None
    image_key = hashlib.sha256(data).hexdigest() if data else None
    if st.session_state.get("image_key") != image_key:
        st.session_state["image_key"] = image_key
        st.session_state.pop("result", None)
    valid = False
    if data:
        try:
            info = validate_image(data)
            valid = True
            st.image(data, width="stretch")
            st.caption(f"{info.width:,} × {info.height:,} pixels · {len(data) / 1024:,.0f} KB")
        except LabError as exc:
            st.error(str(exc))
    else:
        st.info("Try a product photo, an equipment image, or a scene with several objects.")

with right:
    st.subheader("2. Ask about it")
    def choose_prompt():
        st.session_state["question"] = PROMPTS[st.session_state["task"]]

    st.radio("Start with a guided task", list(PROMPTS), horizontal=True,
             key="task", on_change=choose_prompt)
    if "question" not in st.session_state:
        st.session_state["question"] = PROMPTS[st.session_state["task"]]
    with st.form("analyze"):
        question = st.text_area("Your question — edit freely", key="question", height=180,
                                max_chars=8000, placeholder="What would you like to know?")
        submitted = st.form_submit_button("Analyze image", type="primary",
                                         disabled=not valid or not settings.compartment_id)
    st.caption("Each request uses the current image and question, without previous answers.")
    if submitted:
        st.session_state.pop("result", None)
        try:
            with st.spinner("Examining your image…"):
                result = analyze_image(data, question, settings)
            st.session_state["result"] = (question, result)
        except LabError as exc:
            st.error(str(exc))

    if "result" in st.session_state:
        asked, result = st.session_state["result"]
        st.divider()
        st.subheader("Answer")
        with st.expander("Question used"):
            st.write(asked)
        st.markdown(result.text)
        if result.finish_reason == "MAX_TOKENS":
            st.warning("The answer reached its length limit. Ask a narrower question for more detail.")
        st.caption(f"{result.elapsed:.1f} seconds · {result.region}")
        st.download_button("Download answer", result.text, "vision-answer.md", "text/markdown")
        with st.expander("Copy answer"):
            st.code(result.text, language=None)
        with st.expander("Request details"):
            st.json({"model": result.model, "region": result.region,
                     "elapsed_seconds": round(result.elapsed, 2),
                     "finish_reason": result.finish_reason, "request_id": result.request_id})
