import os
from typing import Optional
from google import genai
from google.genai import types


class GeminiService:
    """Service untuk integrasi dengan Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.0-flash-exp"

        # Initialize client dengan API key
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Ringkasan teks menggunakan Gemini"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"""Buatkan ringkasan singkat dari teks berikut dalam {max_length} karakter:

{text}

Ringkasan:"""

        try:
            response = self._call_api(prompt)
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def answer_question(self, question: str, context: str) -> str:
        """Menjawab pertanyaan berdasarkan konteks (untuk chatbot)"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"""Berdasarkan konteks berikut, jawab pertanyaan dengan jelas dan akurat:

KONTEKS:
{context}

PERTANYAAN:
{question}

JAWABAN:"""

        try:
            response = self._call_api(prompt)
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_key_info(self, text: str) -> dict:
        """Ekstrak informasi kunci dari dokumen"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        prompt = f"""Ekstrak informasi kunci berikut dari dokumen organisasi:
1. Nama organisasi
2. Tanggal berdiri
3. Ideologi/Asas
4. Tujuan utama
5. Struktur organisasi (jika ada)

Dokumen:
{text[:2000]}

Format jawaban sebagai JSON."""

        try:
            response = self._call_api(prompt)
            return {"info": response}
        except Exception as e:
            return {"error": str(e)}

    def _call_api(self, prompt: str) -> str:
        """Call Gemini API menggunakan google-genai library"""
        if not self.client:
            raise Exception("Gemini API client not initialized. Check GEMINI_API_KEY.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=2048,
                ),
            )

            # Handle None case
            if response.text is None:
                raise Exception("Gemini API returned empty response")

            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
