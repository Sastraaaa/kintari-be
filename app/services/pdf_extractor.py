import pdfplumber
import re
from pathlib import Path
from typing import Dict, Tuple


class PDFExtractor:
    """Ekstraksi data dari PDF dokumen organisasi (HIPMI, AD/ART, PO, dll)"""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Ekstrak semua teks dari PDF"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def extract_metadata(file_path: str) -> Dict:
        """Ekstrak metadata dari PDF"""
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = {
                    "total_pages": len(pdf.pages),
                    "author": pdf.metadata.get("Author", "Unknown"),
                    "title": pdf.metadata.get("Title", "Unknown"),
                    "creation_date": pdf.metadata.get("CreationDate", "Unknown"),
                }
            return metadata
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def extract_tables(file_path: str) -> list:
        """Ekstrak tabel dari PDF"""
        try:
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            tables.append({"page": page_num + 1, "data": table})
            return tables
        except Exception as e:
            return []

    @staticmethod
    def extract_hipmi_data(file_path: str) -> Dict:
        """Ekstrak data spesifik dari dokumen HIPMI"""
        text = PDFExtractor.extract_text(file_path)

        # Pattern matching untuk data HIPMI
        data = {
            "organization_name": PDFExtractor._extract_org_name(text),
            "founded_date": PDFExtractor._extract_founded_date(text),
            "ideology": PDFExtractor._extract_ideology(text),
            "legal_basis": PDFExtractor._extract_legal_basis(text),
            "objectives": PDFExtractor._extract_objectives(text),
            "full_text": text[:2000] + "..." if len(text) > 2000 else text,
        }
        return data

    @staticmethod
    def _extract_org_name(text: str) -> str:
        """Ekstrak nama organisasi"""
        patterns = [
            r"(?:HIPMI|Himpunan Pengusaha Muda Indonesia)",
            r"(?:nama organisasi|organization name)[\s:]*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if ":" in pattern else match.group(0)
        return "Unknown"

    @staticmethod
    def _extract_founded_date(text: str) -> str:
        """Ekstrak tanggal berdiri"""
        patterns = [
            r"(?:didirikan|founded|berdiri)[\s:]*(\d{1,2}\s+\w+\s+\d{4})",
            r"(?:tanggal|date)[\s:]*(\d{1,2}/\d{1,2}/\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Unknown"

    @staticmethod
    def _extract_ideology(text: str) -> str:
        """Ekstrak ideologi"""
        patterns = [
            r"(?:ideologi|ideology)[\s:]*([^\n]+)",
            r"(?:Pancasila|pancasila)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if ":" in pattern else match.group(0)
        return "Unknown"

    @staticmethod
    def _extract_legal_basis(text: str) -> str:
        """Ekstrak dasar hukum"""
        patterns = [
            r"(?:dasar hukum|legal basis)[\s:]*([^\n]+(?:\n[^\n]+)*)",
            r"(?:UUD|UU|Peraturan|Keputusan)[\s\w\d\-\.\/]+",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "Unknown"

    @staticmethod
    def _extract_objectives(text: str) -> str:
        """Ekstrak tujuan organisasi"""
        patterns = [
            r"(?:tujuan|objectives|maksud)[\s:]*([^\n]+(?:\n[^\n]+)*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Unknown"
