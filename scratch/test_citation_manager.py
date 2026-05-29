"""
Unit Test for tools/citation_manager.py
======================================
Validates APA, IEEE, MLA, and BibTeX citation formatting.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.citation_manager import CitationManager

def test_academic_citation():
    print("\n--- Test Academic Citation ---")
    source = {
        "type": "academic",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
        "year": 2017,
        "url": "https://arxiv.org/abs/1706.03762",
        "venue": "Advances in Neural Information Processing Systems",
    }
    cm = CitationManager([source])
    s = cm.sources[0]

    # Verify DOI extraction and year conversion
    assert s["year"] == 2017
    assert s["doi"] == "" # No DOI in URL
    
    apa = cm.get_apa_citation(s)
    print("APA:", apa)
    assert "Vaswani, A." in apa
    assert "(2017)" in apa
    assert "*Advances in Neural Information Processing Systems*" in apa
    assert "https://arxiv.org/abs/1706.03762" in apa
    
    ieee = cm.get_ieee_citation(s)
    print("IEEE:", ieee)
    assert "A. Vaswani" in ieee
    assert "Attention Is All You Need" in ieee
    
    mla = cm.get_mla_citation(s)
    print("MLA:", mla)
    assert "Vaswani, Ashish, et al." in mla
    
    bib = cm.get_bibtex_citation(s)
    print("BibTeX:\n" + bib)
    assert "@article{vaswani2017attention" in bib or "@article{vaswani2017attention" in bib.lower()
    print("[PASS] Academic citation tests successfully completed.")

def test_pdf_citation():
    print("\n--- Test PDF Citation ---")
    source = {
        "type": "pdf",
        "title": "Internet of Things Review of Smart Systems",
        "authors": ["K. Shafique", "B. A. Khawaja"],
        "year": 2020,
        "url": "/app/static/uploaded_pdfs/IoT_Smart_Systems.pdf",
        "venue": "PDF Library"
    }
    cm = CitationManager([source])
    s = cm.sources[0]
    
    apa = cm.get_apa_citation(s)
    print("APA:", apa)
    assert "Retrieved from PDF library." in apa
    
    ieee = cm.get_ieee_citation(s)
    print("IEEE:", ieee)
    assert "[Online]. Available: PDF library." in ieee
    
    bib = cm.get_bibtex_citation(s)
    print("BibTeX:\n" + bib)
    assert "@misc{shafique2020internet" in bib or "@misc{shafique2020internet" in bib.lower()
    print("[PASS] PDF citation tests successfully completed.")

def test_web_citation():
    print("\n--- Test Web Citation ---")
    source = {
        "type": "web",
        "title": "Gemini 3.5 Flash Documentation",
        "authors": ["Google DeepMind"],
        "year": "n.d.",
        "url": "https://deepmind.google/gemini",
        "venue": "deepmind.google"
    }
    cm = CitationManager([source])
    s = cm.sources[0]
    
    apa = cm.get_apa_citation(s)
    print("APA:", apa)
    assert "(n.d.)" in apa
    
    bib = cm.get_bibtex_citation(s)
    print("BibTeX:\n" + bib)
    assert "@online{deepmindndgemini" in bib
    print("[PASS] Web citation tests successfully completed.")

def test_doi_extraction():
    print("\n--- Test DOI Extraction ---")
    url = "https://doi.org/10.1109/fiot.2018.8325598"
    doi = CitationManager.extract_doi(url)
    print("Extracted DOI:", doi)
    assert doi == "10.1109/fiot.2018.8325598"
    
    url_no_doi = "https://example.com/paper.pdf"
    assert CitationManager.extract_doi(url_no_doi) == ""
    print("[PASS] DOI extraction tests successfully completed.")

if __name__ == "__main__":
    print("=== Testing Citation Manager ===")
    test_academic_citation()
    test_pdf_citation()
    test_web_citation()
    test_doi_extraction()
    print("\n=== ALL CITATION TESTS PASSED ===")
