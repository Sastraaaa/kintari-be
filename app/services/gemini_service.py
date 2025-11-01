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

    def analyze_members_data(self, members_data: list) -> dict:
        """Analisis data anggota HIPMI dengan AI"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Prepare data summary
        total = len(members_data)
        organizations = {}
        positions = {}
        membership_types = {}
        years_data = {}

        for member in members_data:
            # Count by organization
            org = member.get("organization", "Unknown")
            organizations[org] = organizations.get(org, 0) + 1

            # Count by position
            pos = member.get("position", "Unknown")
            positions[pos] = positions.get(pos, 0) + 1

            # Count by membership type
            mtype = member.get("membership_type", "Unknown")
            membership_types[mtype] = membership_types.get(mtype, 0) + 1

            # Count by year
            joined = member.get("joined_date", "")
            if joined:
                try:
                    year = str(joined)[:4]
                    years_data[year] = years_data.get(year, 0) + 1
                except:
                    pass

        data_summary = f"""
Total Anggota: {total}
Distribusi Organisasi: {organizations}
Distribusi Jabatan: {positions}
Distribusi Tipe Membership: {membership_types}
Distribusi per Tahun: {years_data}
"""

        prompt = f"""Sebagai AI analyst untuk organisasi HIPMI, analisis data keanggotaan berikut dan berikan insight:

DATA ANGGOTA HIPMI:
{data_summary}

Berikan analisis dalam format JSON dengan struktur:
{{
    "summary": "Ringkasan singkat kondisi keanggotaan HIPMI (2-3 kalimat)",
    "total_members": {total},
    "key_insights": [
        "Insight 1 tentang distribusi organisasi",
        "Insight 2 tentang jabatan/posisi",
        "Insight 3 tentang tren keanggotaan"
    ],
    "trends": "Analisis tren pertumbuhan anggota per tahun",
    "recommendations": [
        "Rekomendasi 1 untuk pengembangan",
        "Rekomendasi 2 untuk retensi anggota"
    ]
}}

Pastikan response dalam format JSON yang valid."""

        try:
            response = self._call_api(prompt)
            # Try to parse as JSON, if fails return as text
            import json

            try:
                return json.loads(response)
            except:
                return {
                    "summary": response,
                    "total_members": total,
                    "raw_analysis": response,
                }
        except Exception as e:
            return {"error": str(e)}

    def analyze_documents_data(self, documents_data: list) -> dict:
        """Analisis data dokumen HIPMI dengan AI"""
        if not self.api_key:
            return {"error": "API Key not configured"}

        # Prepare data summary
        total = len(documents_data)
        doc_types = {}
        categories = {}
        total_pages = 0

        for doc in documents_data:
            # Count by document type
            dtype = doc.get("document_type", "Unknown")
            doc_types[dtype] = doc_types.get(dtype, 0) + 1

            # Count by category
            cat = doc.get("category", "Uncategorized")
            categories[cat] = categories.get(cat, 0) + 1

            # Sum pages
            pages = doc.get("page_count", 0)
            if pages:
                total_pages += pages

        data_summary = f"""
Total Dokumen: {total}
Total Halaman: {total_pages}
Distribusi Tipe: {doc_types}
Distribusi Kategori: {categories}
"""

        prompt = f"""Sebagai AI analyst untuk organisasi HIPMI, analisis data dokumen berikut dan berikan insight:

DATA DOKUMEN HIPMI:
{data_summary}

Berikan analisis dalam format JSON dengan struktur:
{{
    "summary": "Ringkasan singkat kondisi dokumentasi HIPMI (2-3 kalimat)",
    "total_documents": {total},
    "total_pages": {total_pages},
    "key_insights": [
        "Insight 1 tentang distribusi tipe dokumen",
        "Insight 2 tentang kategorisasi",
        "Insight 3 tentang kelengkapan dokumentasi"
    ],
    "document_health": "Status kelengkapan dan kualitas dokumentasi",
    "recommendations": [
        "Rekomendasi 1 untuk perbaikan dokumentasi",
        "Rekomendasi 2 untuk organisasi dokumen"
    ]
}}

Pastikan response dalam format JSON yang valid."""

        try:
            response = self._call_api(prompt)
            # Try to parse as JSON, if fails return as text
            import json

            try:
                return json.loads(response)
            except:
                return {
                    "summary": response,
                    "total_documents": total,
                    "total_pages": total_pages,
                    "raw_analysis": response,
                }
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
