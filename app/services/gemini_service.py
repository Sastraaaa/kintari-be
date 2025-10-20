import os
import requests
from typing import Optional


class GeminiService:
    """Service untuk integrasi dengan Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-pro"

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
        """Call Gemini API"""
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            return "No response from Gemini API"
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
