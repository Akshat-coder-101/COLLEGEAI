import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import ResearchProject, Document, Source
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.config import settings

router = APIRouter(tags=["Document Management"])


@router.post("/research/{project_id}/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents(
    project_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    uploaded_docs = []
    duplicate_names = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file.filename}'. Only PDF documents are supported."
            )

        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File '{file.filename}' exceeds maximum allowed upload size ({settings.MAX_UPLOAD_SIZE} bytes)."
            )

        file_hash = DocumentService.calculate_file_hash(content)

        # Check for duplicate document in the same project
        existing_doc = db.query(Document).filter(
            Document.project_id == project_id,
            Document.file_hash == file_hash
        ).first()

        if existing_doc:
            duplicate_names.append(file.filename)
            continue

        # Save to disk
        project_upload_dir = Path(settings.UPLOAD_DIRECTORY) / project_id
        project_upload_dir.mkdir(parents=True, exist_ok=True)
        dest_path = project_upload_dir / file.filename

        with open(dest_path, "wb") as f:
            f.write(content)

        # Extract text and page count
        extraction_data = DocumentService.extract_pdf_content(str(dest_path))

        doc_entity = Document(
            project_id=project_id,
            filename=file.filename,
            file_path=str(dest_path),
            file_size=len(content),
            file_hash=file_hash,
            page_count=extraction_data["page_count"],
            extracted_text=extraction_data["full_text"]
        )
        db.add(doc_entity)
        db.flush()

        # Create Source entity
        source = Source(
            project_id=project_id,
            document_id=doc_entity.id,
            source_type="uploaded_document",
            citation_label=f"{file.filename} (Uploaded PDF, {doc_entity.page_count} pages)",
            metadata_info={"filename": file.filename, "size": len(content), "pages": doc_entity.page_count}
        )
        db.add(source)
        uploaded_docs.append(doc_entity)

    db.commit()

    return DocumentUploadResponse(
        uploaded=[DocumentResponse.model_validate(d) for d in uploaded_docs],
        duplicates=duplicate_names,
        message=f"Processed {len(files)} files: {len(uploaded_docs)} uploaded, {len(duplicate_names)} duplicate(s) skipped."
    )


@router.get("/research/{project_id}/documents", response_model=List[DocumentResponse])
def list_project_documents(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    docs = db.query(Document).filter(Document.project_id == project_id).all()
    return docs


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clean up physical file if present
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return None


@router.get("/documents/{document_id}")
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "projectId": doc.project_id,
        "filename": doc.filename,
        "fileSize": doc.file_size,
        "pageCount": doc.page_count,
        "isConfidential": bool(doc.is_confidential),
        "fileUrl": f"/api/v1/documents/{doc.id}/file",
        "downloadUrl": f"/api/v1/documents/{doc.id}/download",
        "extractedTextSnippet": (doc.extracted_text or "")[:500] + "..." if len(doc.extracted_text or "") > 500 else doc.extracted_text,
        "createdAt": doc.created_at.isoformat() if doc.created_at else None
    }


@router.get("/documents/{document_id}/file")
def view_document_pdf(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail=f"Physical file missing on server: {doc.filename}")

    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{doc.filename}"'}
    )


@router.get("/documents/{document_id}/download")
def download_document_pdf(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail=f"Physical file missing on server: {doc.filename}")

    return FileResponse(
        path=doc.file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'}
    )

