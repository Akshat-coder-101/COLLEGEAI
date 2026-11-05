import io
import fitz
import pytest
from app.services.document_service import DocumentService


def create_sample_pdf(title: str, text: str) -> bytes:
    """Helper to generate an in-memory PDF using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), f"Title: {title}\n\n{text}", fontsize=12)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_pdf_extraction_service(tmp_path):
    text_sample = "Superconductivity was observed below the critical transition temperature Tc = 93 K in YBCO."
    pdf_bytes = create_sample_pdf("High Tc Research", text_sample)
    
    file_path = tmp_path / "sample_paper.pdf"
    file_path.write_bytes(pdf_bytes)

    extracted = DocumentService.extract_pdf_content(str(file_path))
    assert extracted["page_count"] >= 1
    assert "Superconductivity was observed" in extracted["full_text"]
    assert "93 K" in extracted["full_text"]


def test_duplicate_document_detection_via_hash():
    content1 = b"%PDF-1.4 test binary stream A"
    content2 = b"%PDF-1.4 test binary stream A"
    content3 = b"%PDF-1.4 test binary stream B"

    hash1 = DocumentService.calculate_file_hash(content1)
    hash2 = DocumentService.calculate_file_hash(content2)
    hash3 = DocumentService.calculate_file_hash(content3)

    assert hash1 == hash2
    assert hash1 != hash3


def test_document_upload_and_duplicate_prevention(client):
    # 1. Create project
    proj_res = client.post("/api/v1/research", json={
        "title": "Doc Project",
        "question": "Testing PDF Upload"
    })
    project_id = proj_res.json()["id"]

    pdf_bytes = create_sample_pdf("First Document", "Empirical finding: lattice strain equals 0.02 delta.")

    # 2. Upload file
    upload_res = client.post(
        f"/api/v1/research/{project_id}/documents",
        files=[("files", ("sample1.pdf", pdf_bytes, "application/pdf"))]
    )
    assert upload_res.status_code == 201
    assert len(upload_res.json()["uploaded"]) == 1
    doc_id = upload_res.json()["uploaded"][0]["id"]

    # 3. Upload same file again -> should be detected as duplicate!
    dup_res = client.post(
        f"/api/v1/research/{project_id}/documents",
        files=[("files", ("sample1_copy.pdf", pdf_bytes, "application/pdf"))]
    )
    assert dup_res.status_code == 201
    assert len(dup_res.json()["duplicates"]) == 1
    assert "sample1_copy.pdf" in dup_res.json()["duplicates"]

    # 4. List documents
    list_docs = client.get(f"/api/v1/research/{project_id}/documents")
    assert list_docs.status_code == 200
    assert len(list_docs.json()) == 1

    # 5. Delete document
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 204

    # 6. Reject non-PDF file
    bad_upload = client.post(
        f"/api/v1/research/{project_id}/documents",
        files=[("files", ("script.sh", b"echo hello", "text/plain"))]
    )
    assert bad_upload.status_code == 400
