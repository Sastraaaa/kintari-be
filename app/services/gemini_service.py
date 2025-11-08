import os
import json
from typing import Optional
from google import genai
from google.genai import types


class GeminiService:
    """Service untuk integrasi dengan Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.0-flash-exp"
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Ringkasan teks menggunakan Gemini"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"Buatkan ringkasan singkat ({max_length} karakter) dari teks berikut:\n\n{text}\n\nRingkasan:"
        try:
            return self._call_api(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def answer_question(self, question: str, context: str) -> str:
        """Jawab pertanyaan berdasarkan konteks (chatbot)"""
        if not self.api_key:
            return "API Key not configured"

        prompt = f"Berdasarkan konteks berikut, jawab pertanyaan:\n\nKONTEKS:\n{context}\n\nPERTANYAAN:\n{question}\n\nJAWABAN:"
        try:
            return self._call_api(prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def extract_key_info(self, text: str) -> dict:
        """Ekstrak info kunci dari dokumen organisasi"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        prompt = f"""Ekstrak info kunci dari dokumen: Nama organisasi, Tanggal berdiri, Asas, Tujuan, Struktur (jika ada).
        
Dokumen:
{text[:2000]}

Format JSON."""
        try:
            return {"info": self._call_api(prompt)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_members_data(self, members_data: list) -> dict:
        """Analisis data pengurus HIPMI dengan AI"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Build statistics
        total = len(members_data)
        stats = self._build_member_stats(members_data)

        prompt = f"""Analisis data keanggotaan HIPMI berikut dan berikan insight:

DATA ANGGOTA: Total {total}
Distribusi Jabatan: {stats['positions']}
Distribusi Bidang Usaha: {stats['business']}
Distribusi Gender: {stats['gender']}

Format JSON:
{{
    "summary": "Ringkasan kondisi keanggotaan (2-3 kalimat)",
    "total_members": {total},
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "trends": "Analisis tren",
    "recommendations": ["Rekomendasi 1", "Rekomendasi 2"]
}}"""

        try:
            response = self._call_api(prompt)
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            return {"summary": response, "total_members": total, "raw_analysis": response}
        except Exception as e:
            return {"error": str(e)}

    def analyze_documents_data(self, documents_data: list) -> dict:
        """Analisis data dokumen HIPMI dengan AI"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Build statistics
        total = len(documents_data)
        stats = self._build_document_stats(documents_data)

        prompt = f"""Analisis data dokumen HIPMI berikut:

DATA DOKUMEN: Total {total}, Total Halaman {stats['total_pages']}
Distribusi Tipe: {stats['types']}
Distribusi Kategori: {stats['categories']}

Format JSON:
{{
    "summary": "Ringkasan kondisi dokumentasi (2-3 kalimat)",
    "total_documents": {total},
    "total_pages": {stats['total_pages']},
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "document_health": "Status kelengkapan dokumentasi",
    "recommendations": ["Rekomendasi 1", "Rekomendasi 2"]
}}"""

        try:
            response = self._call_api(prompt)
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            return {
                "summary": response,
                "total_documents": total,
                "total_pages": stats['total_pages'],
                "raw_analysis": response,
            }
        except Exception as e:
            return {"error": str(e)}

    def _build_member_stats(self, members_data: list) -> dict:
        """Build statistik dari data members"""
        positions = {}
        business = {}
        gender = {"Male": 0, "Female": 0}

        for m in members_data:
            # Count positions
            pos = m.get("jabatan", "Unknown")
            positions[pos] = positions.get(pos, 0) + 1

            # Count business categories
            biz = m.get("kategori_bidang_usaha", "Unknown")
            business[biz] = business.get(biz, 0) + 1

            # Count gender
            g = m.get("jenis_kelamin")
            if g in ["Male", "Female"]:
                gender[g] += 1

        return {"positions": positions, "business": business, "gender": gender}

    def _build_document_stats(self, documents_data: list) -> dict:
        """Build statistik dari data documents"""
        types_count = {}
        categories = {}
        total_pages = 0

        for doc in documents_data:
            # Count types
            dtype = doc.get("document_type", "Unknown")
            types_count[dtype] = types_count.get(dtype, 0) + 1

            # Count categories
            cat = doc.get("category", "Uncategorized")
            categories[cat] = categories.get(cat, 0) + 1

            # Sum pages
            pages = doc.get("page_count", 0)
            if pages:
                total_pages += pages

        return {"types": types_count, "categories": categories, "total_pages": total_pages}

    def _call_api(self, prompt: str) -> str:
        """Call Gemini API"""
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

            if response.text is None:
                raise Exception("Gemini API returned empty response")

            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
