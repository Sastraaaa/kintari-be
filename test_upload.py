"""
Script untuk test upload file PDF ke API dan ekstraksi data HIPMI
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
PDF_FILE = "PO HIPMI DISAIN BARU (05072024) (1).pdf"


def test_upload_document():
    """Test upload dokumen HIPMI"""
    print("=" * 60)
    print("🚀 Testing: Upload Dokumen HIPMI")
    print("=" * 60)

    file_path = Path(PDF_FILE)
    if not file_path.exists():
        print(f"❌ File tidak ditemukan: {PDF_FILE}")
        return None

    print(f"📄 File: {PDF_FILE}")
    print(f"📏 Size: {file_path.stat().st_size / 1024:.2f} KB")

    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/organization/upload", files=files)

    print(f"\n✅ Status: {response.status_code}")
    data = response.json()
    print(f"📋 Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    return data.get("organization_id") if response.status_code == 200 else None


def test_get_latest_organization():
    """Test ambil data organisasi terbaru"""
    print("\n" + "=" * 60)
    print("📊 Testing: Get Latest Organization Data")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/organization/latest")

    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"📋 Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    return data.get("data", {}).get("id") if response.status_code == 200 else None


def test_chat_query():
    """Test chat query berbasis HIPMI"""
    print("\n" + "=" * 60)
    print("💬 Testing: Chat Query")
    print("=" * 60)

    query = "Apa itu HIPMI dan apa tujuannya?"
    print(f"❓ Query: {query}")

    payload = {"query": query, "context": None}

    response = requests.post(
        f"{BASE_URL}/api/chat/query",
        json=payload,
        headers={"Content-Type": "application/json"},
    )

    print(f"\n✅ Status: {response.status_code}")
    data = response.json()
    print(f"📋 Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_stats_overview():
    """Test statistik overview"""
    print("\n" + "=" * 60)
    print("📈 Testing: Stats Overview")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/stats/overview")

    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"📋 Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_health_check():
    """Test health check"""
    print("\n" + "=" * 60)
    print("🏥 Testing: Health Check")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/health")

    print(f"✅ Status: {response.status_code}")
    print(f"📋 Response: {response.json()}")


if __name__ == "__main__":
    print("\n" + "🔧 KINTARI BACKEND API - TEST SUITE" + "\n")

    # Test health check
    test_health_check()

    # Test upload document
    org_id = test_upload_document()

    # Test get latest organization
    test_get_latest_organization()

    # Test chat query
    test_chat_query()

    # Test stats
    test_stats_overview()

    print("\n" + "=" * 60)
    print("✅ TEST SUITE SELESAI!")
    print("=" * 60)
    print("\n📚 Dokumentasi API: http://localhost:8000/docs")
    print("🔗 Alternatif Docs: http://localhost:8000/redoc\n")
