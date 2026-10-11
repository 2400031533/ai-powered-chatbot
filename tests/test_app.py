import tempfile
import unittest
from pathlib import Path
import app as chatbot_app

class ChatbotTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        chatbot_app.DB_PATH = Path(self.temp_dir.name) / "test.db"
        chatbot_app.init_db()
        chatbot_app.app.config["TESTING"] = True
        self.client = chatbot_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_chat_known_question(self):
        response = self.client.post("/api/chat", json={"message": "How do I track my order?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Orders page", response.json["response"])

    def test_empty_message_rejected(self):
        response = self.client.post("/api/chat", json={"message": "  "})
        self.assertEqual(response.status_code, 400)

    def test_history_records_message(self):
        self.client.post("/api/chat", json={"message": "What are your business hours?"})
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["history"]), 1)

if __name__ == "__main__":
    unittest.main()
