import os
import unittest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

import oci
from PIL import Image
from streamlit.testing.v1 import AppTest

from vision_lab.client import MAX_BYTES, analyze_image, validate_image
from vision_lab.config import LabError, Settings
from vision_lab.prompts import PROMPTS


def picture():
    buf = BytesIO()
    Image.new("RGB", (8, 8), "blue").save(buf, format="PNG")
    return buf.getvalue()


class LabTests(unittest.TestCase):
    def test_bad_images(self):
        for data in (b"", b"not a picture", b"x" * (MAX_BYTES + 1)):
            with self.subTest(size=len(data)), self.assertRaises(LabError):
                validate_image(data)
        self.assertEqual(validate_image(picture()).mime_type, "image/png")

    def test_request_and_response(self):
        m = oci.generative_ai_inference.models
        client = Mock()
        client.chat.return_value = SimpleNamespace(
            data=SimpleNamespace(chat_response=m.CohereChatResponseV2(
                finish_reason="COMPLETE", message=m.CohereAssistantMessageV2(
                    content=[m.CohereTextContentV2(text="A blue square.")]))),
            headers={"opc-request-id": "test-request"})
        result = analyze_image(picture(), "What is visible?", Settings("test-compartment"), client)
        self.assertEqual(result.text, "A blue square.")
        request = client.chat.call_args.args[0]
        self.assertEqual(request.chat_request.api_format, "COHEREV2")
        self.assertEqual(request.serving_mode.serving_type, "ON_DEMAND")
        contents = request.chat_request.messages[1].content
        self.assertEqual(contents[0].text, "What is visible?")
        self.assertTrue(contents[1].image_url.url.startswith("data:image/png;base64,"))
        self.assertEqual(result.request_id, "test-request")

    def test_errors_do_not_expose_service_payload(self):
        client = Mock()
        client.chat.side_effect = oci.exceptions.ServiceError(401, "NotAuthenticated", {}, "SECRET")
        with self.assertRaises(LabError) as error:
            analyze_image(picture(), "Describe", Settings("compartment"), client)
        self.assertNotIn("SECRET", str(error.exception))
        self.assertIn("authentication", str(error.exception))

    def test_missing_config_and_question_do_not_call_oci(self):
        client = Mock()
        for settings, question in ((Settings(""), "Describe"), (Settings("x"), "  ")):
            with self.assertRaises(LabError):
                analyze_image(picture(), question, settings, client)
        client.chat.assert_not_called()

    def test_ui_and_prompt_switch(self):
        with patch.dict(os.environ, {"OCI_COMPARTMENT_ID": ""}):
            app = AppTest.from_file("src/vision_lab/app.py").run()
            self.assertFalse(app.exception)
            self.assertTrue(app.button[0].disabled)
            for task in ("Inspect for issues", "Evidence-based analysis",
                         "Extract structured data", "Compare against checklist"):
                app.radio[0].set_value(task).run()
                self.assertEqual(app.text_area[0].value, PROMPTS[task])
            app.radio[0].set_value("Ask your own question").run()
            self.assertEqual(app.text_area[0].value, "")
            self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
