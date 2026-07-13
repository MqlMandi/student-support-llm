import docx
from backend.utils.document_parser import parse_file
from backend.utils.chunker import chunk_text
from backend.utils.embedder import generate_embedding
from backend.scripts.ingest_faq import main
from backend.database import get_chroma_client

def test_parse_txt(tmp_path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello world")
    assert parse_file(str(txt_file)) == "Hello world"

def test_parse_docx(tmp_path):
    docx_file = tmp_path / "test.docx"
    doc = docx.Document()
    doc.add_paragraph("Hello docx")
    doc.save(str(docx_file))
    assert parse_file(str(docx_file)).strip() == "Hello docx"

def test_chunk_text():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) == 3
    assert len(chunks[0]) == 500

def test_generate_embedding():
    emb = generate_embedding("Test embedding")
    assert len(emb) > 0

def test_integration_ingest_faq(tmp_path):
    txt_file = tmp_path / "faq.txt"
    txt_file.write_text("This is a university FAQ document. The university is great.")
    
    main(str(tmp_path))
    
    client = get_chroma_client()
    collection = client.get_collection("university_faq")
    assert collection.count() > 0
