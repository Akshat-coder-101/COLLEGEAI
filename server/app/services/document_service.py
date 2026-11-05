import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DocumentService:
    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 hash of file content for duplicate detection."""
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        return hasher.hexdigest()

    @staticmethod
    def extract_pdf_content(file_path: str) -> Dict[str, Any]:
        """
        Extracts structured text from PDF file.
        Uses PyMuPDF (fitz) if available, with pypdf as fallback.
        Preserves page indices and paragraph structures.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        pages_data: List[Dict[str, Any]] = []
        total_text_parts: List[str] = []

        # Try PyMuPDF first
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text") or ""
                pages_data.append({
                    "page_number": page_num + 1,
                    "text": text.strip()
                })
                total_text_parts.append(text)
            doc.close()

            return {
                "page_count": page_count,
                "pages": pages_data,
                "full_text": "\n\n".join(total_text_parts).strip(),
                "extractor": "PyMuPDF"
            }
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed or not available ({e}). Trying pypdf fallback.")

        # Fallback to pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_data.append({
                    "page_number": idx + 1,
                    "text": text.strip()
                })
                total_text_parts.append(text)

            return {
                "page_count": page_count,
                "pages": pages_data,
                "full_text": "\n\n".join(total_text_parts).strip(),
                "extractor": "pypdf"
            }
        except Exception as e:
            logger.error(f"pypdf extraction failed as well: {e}")
            raise RuntimeError(f"Unable to extract text from PDF: {e}")

    @staticmethod
    def extract_evidence_snippets(pages_data: List[Dict[str, Any]], query_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Finds exact matching paragraphs and assigns page references for source traceability.
        """
        snippets = []
        for page in pages_data:
            page_no = page["page_number"]
            paragraphs = [p.strip() for p in page["text"].split("\n\n") if len(p.strip()) > 30]
            
            for p_idx, para in enumerate(paragraphs):
                para_lower = para.lower()
                matches = sum(1 for kw in query_keywords if kw.lower() in para_lower)
                if matches > 0 or len(snippets) < 3:
                    snippets.append({
                        "location_reference": f"Page {page_no}, Paragraph {p_idx + 1}",
                        "text": para,
                        "relevance": matches
                    })
        return snippets
