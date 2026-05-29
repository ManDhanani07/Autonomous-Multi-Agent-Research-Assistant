"""
Citation and Bibliography Manager Module
=========================================
Handles generation of academic citations in APA 7th, IEEE, and MLA 9th styles.
Also outputs structured BibTeX records and manages exportable bibliography (.bib) files.
"""

import re
import os
import urllib.parse
from datetime import datetime

class CitationManager:
    def __init__(self, sources: list = None):
        """
        Initializes the CitationManager with a list of standardized sources.
        Each source should be a dict containing:
          - 'type': 'academic' | 'pdf' | 'web'
          - 'title': str
          - 'authors': list of str (optional)
          - 'year': int or str (optional)
          - 'url': str (optional)
          - 'venue': str (optional, e.g. journal name, website name, or PDF Library)
          - 'doi': str (optional)
        """
        self.sources = []
        if sources:
            for s in sources:
                self.add_source(s)

    def add_source(self, source: dict):
        """Standardizes and adds a source to the bibliography."""
        if not isinstance(source, dict) or not source.get("title"):
            return

        url = source.get("url") or ""
        doi = source.get("doi") or ""
        if url and not doi:
            # Attempt to extract DOI from URL
            doi = self.extract_doi(url)

        title = source.get("title", "").strip()
        # Clean title if it contains PDF library markers
        title_clean = title.replace("[PDF Library] ", "").strip()

        # Sanitize authors
        raw_authors = source.get("authors")
        authors = []
        if isinstance(raw_authors, list):
            authors = [str(a).strip() for a in raw_authors if str(a).strip()]
        elif isinstance(raw_authors, str) and raw_authors.strip():
            # If comma-separated or similar
            authors = [a.strip() for a in re.split(r',|and', raw_authors) if a.strip()]

        year = source.get("year")
        if year is None:
            year = "n.d."
        else:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = str(year).strip() or "n.d."

        self.sources.append({
            "type": source.get("type") or ("pdf" if "pdf" in url.lower() else "academic"),
            "title": title_clean,
            "authors": authors,
            "year": year,
            "url": url,
            "venue": source.get("venue") or source.get("source") or ("PDF Library" if "static/uploaded_pdfs" in url else ""),
            "doi": doi
        })

    @staticmethod
    def extract_doi(url: str) -> str:
        """Extracts standard DOI (e.g. 10.1109/fiot.2018.8325598) from a URL."""
        if not url:
            return ""
        # Search for DOI pattern: 10.xxxx/yyyy
        match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', url)
        if match:
            return match.group(1).rstrip('.')
        return ""

    @staticmethod
    def clean_name_initials(name: str) -> dict:
        """Parses a full author name into Last Name and Initials."""
        parts = [p.strip() for p in name.split() if p.strip()]
        if not parts:
            return {"last": "Unknown", "initials": "", "first_name": ""}
        
        if len(parts) == 1:
            return {"last": parts[0], "initials": "", "first_name": parts[0]}

        last = parts[-1]
        initials = []
        for p in parts[:-1]:
            p_clean = re.sub(r'[^a-zA-Z]', '', p)
            if p_clean:
                initials.append(f"{p_clean[0].upper()}.")
        return {
            "last": last,
            "initials": " ".join(initials),
            "first_name": parts[0]
        }

    def format_apa_authors(self, authors: list) -> str:
        """Formats author list in APA 7th style: Last, F. M."""
        if not authors:
            return ""
        
        apa_names = []
        for a in authors:
            parsed = self.clean_name_initials(a)
            if parsed["initials"]:
                apa_names.append(f"{parsed['last']}, {parsed['initials']}")
            else:
                apa_names.append(parsed['last'])

        if len(apa_names) == 1:
            return apa_names[0]
        if len(apa_names) == 2:
            return f"{apa_names[0]}, & {apa_names[1]}"
        if len(apa_names) <= 7:
            return ", ".join(apa_names[:-1]) + f", & {apa_names[-1]}"
        # If > 7, conciliate with et al or list up to 7 and use ellipsis
        return ", ".join(apa_names[:6]) + ", ... & " + apa_names[-1]

    def format_ieee_authors(self, authors: list) -> str:
        """Formats author list in IEEE style: F. M. Last."""
        if not authors:
            return ""
        
        ieee_names = []
        for a in authors:
            parsed = self.clean_name_initials(a)
            if parsed["initials"]:
                ieee_names.append(f"{parsed['initials']} {parsed['last']}")
            else:
                ieee_names.append(parsed['last'])

        if len(ieee_names) > 3:
            return f"{ieee_names[0]} et al."
        if len(ieee_names) == 1:
            return ieee_names[0]
        if len(ieee_names) == 2:
            return f"{ieee_names[0]} and {ieee_names[1]}"
        return f"{ieee_names[0]}, {ieee_names[1]}, and {ieee_names[2]}"

    def format_mla_authors(self, authors: list) -> str:
        """Formats author list in MLA 9th style."""
        if not authors:
            return ""
        
        parsed_first = self.clean_name_initials(authors[0])
        first_author_mla = f"{parsed_first['last']}, {parsed_first['first_name']}"
        if parsed_first["initials"] and parsed_first["initials"] != f"{parsed_first['first_name'][0]}.":
            first_author_mla += f" {parsed_first['initials'].replace(parsed_first['first_name'][0]+'.', '').strip()}"

        if len(authors) > 2:
            return f"{first_author_mla}, et al."
        if len(authors) == 1:
            return first_author_mla
        
        # 2 authors
        parsed_sec = self.clean_name_initials(authors[1])
        sec_name = f"{parsed_sec['first_name']} {parsed_sec['last']}"
        return f"{first_author_mla}, and {sec_name}"

    def get_apa_citation(self, source: dict) -> str:
        """Generates an APA 7th edition citation string."""
        authors_str = self.format_apa_authors(source["authors"])
        year = source["year"]
        title = source["title"]
        venue = source["venue"]
        url = source["url"]
        doi = source["doi"]

        citation = ""
        if authors_str:
            citation += f"{authors_str} "
        else:
            citation += f"{title}. "

        citation += f"({year}). "
        
        if authors_str:
            citation += f"{title}. "

        if venue:
            citation += f"*{venue}*. "

        if doi:
            citation += f"https://doi.org/{doi}"
        elif url:
            if url.startswith("http"):
                citation += url
            else:
                # PDF library local reference
                citation += f"Retrieved from PDF library."
        else:
            citation = citation.strip()
        
        return citation.strip()

    def get_ieee_citation(self, source: dict) -> str:
        """Generates an IEEE citation string."""
        authors_str = self.format_ieee_authors(source["authors"])
        year = source["year"]
        title = source["title"]
        venue = source["venue"]
        url = source["url"]
        doi = source["doi"]

        citation = ""
        if authors_str:
            citation += f"{authors_str}, "
        
        citation += f'"{title},"'
        
        if venue:
            citation += f" *{venue}*,"
            
        if year != "n.d.":
            citation += f" {year}."
        else:
            citation += " n.d."

        if doi:
            citation += f" doi: {doi}."
        elif url:
            if url.startswith("http"):
                citation += f" [Online]. Available: {url}."
            else:
                # PDF library
                citation += f" [Online]. Available: PDF library."
        
        return citation.strip()

    def get_mla_citation(self, source: dict) -> str:
        """Generates an MLA 9th edition citation string."""
        authors_str = self.format_mla_authors(source["authors"])
        year = source["year"]
        title = source["title"]
        venue = source["venue"]
        url = source["url"]
        doi = source["doi"]

        citation = ""
        if authors_str:
            citation += f"{authors_str}. "
        
        citation += f'"{title}." '
        
        if venue:
            citation += f"*{venue}*, "
            
        if year != "n.d.":
            citation += f"{year}, "

        if doi:
            citation += f"https://doi.org/{doi}."
        elif url:
            if url.startswith("http"):
                citation += f"{url}."
            else:
                citation += "PDF library."
        else:
            if citation.endswith(", "):
                citation = citation[:-2] + "."
        
        return citation.strip()

    def generate_cite_key(self, source: dict) -> str:
        """Generates a unique BibTeX citation key."""
        authors = source["authors"]
        year = source["year"]
        title = source["title"]

        # First author's last name
        if authors:
            last_name = self.clean_name_initials(authors[0])["last"]
        else:
            last_name = "ref"

        # Sanitize last name
        last_name = re.sub(r'[^a-zA-Z0-9]', '', last_name).lower()
        if not last_name:
            last_name = "ref"

        # Sanitize year
        year_str = str(year)
        if year_str == "n.d.":
            year_str = "nd"

        # First keyword of title
        words = [w for w in title.split() if len(w) > 3]
        if not words:
            words = title.split()
        first_word = words[0] if words else "doc"
        first_word = re.sub(r'[^a-zA-Z0-9]', '', first_word).lower()

        return f"{last_name}{year_str}{first_word}"

    def get_bibtex_citation(self, source: dict) -> str:
        """Generates a BibTeX record string."""
        cite_key = self.generate_cite_key(source)
        title = source["title"]
        year = source["year"]
        url = source["url"]
        doi = source["doi"]
        venue = source["venue"]
        authors = source["authors"]

        # Format authors as 'Author and Author'
        author_field = " and ".join(authors) if authors else "Unknown"

        entry_type = "article"
        if source["type"] == "pdf":
            entry_type = "misc"
        elif source["type"] == "web":
            entry_type = "online"

        bib = f"@{entry_type}{{{cite_key},\n"
        bib += f"  author    = {{{author_field}}},\n"
        bib += f"  title     = {{{title}}},\n"
        
        if venue:
            if entry_type == "online":
                bib += f"  organization = {{{venue}}},\n"
            elif entry_type == "misc":
                bib += f"  howpublished = {{{venue}}},\n"
            else:
                bib += f"  journal   = {{{venue}}},\n"
                
        if year != "n.d.":
            bib += f"  year      = {{{year}}},\n"
            
        if doi:
            bib += f"  doi       = {{{doi}}},\n"
            
        if url:
            bib += f"  url       = {{{url}}},\n"
            
        if entry_type == "online":
            # Add today's date as access date
            today = datetime.now().strftime("%Y-%m-%d")
            bib += f"  urldate   = {{{today}}},\n"

        # Strip trailing comma and close brace
        bib = bib.rstrip(",\n") + "\n}"
        return bib

    def generate_references_section(self, style: str = "IEEE") -> str:
        """Compiles the references list in markdown format."""
        if not self.sources:
            return ""

        lines = [f"## 8. References"]
        for idx, s in enumerate(self.sources, start=1):
            if style.upper() == "IEEE":
                citation = self.get_ieee_citation(s)
                # Formats like [1] Citation
                lines.append(f"{idx}. {citation}")
            elif style.upper() == "APA":
                citation = self.get_apa_citation(s)
                lines.append(f"{idx}. {citation}")
            elif style.upper() == "MLA":
                citation = self.get_mla_citation(s)
                lines.append(f"{idx}. {citation}")
            else:
                lines.append(f"{idx}. {s['title']}")

        return "\n".join(lines)

    def generate_bibtex_file_content(self) -> str:
        """Compiles all sources into a single BibTeX file content string."""
        records = []
        for s in self.sources:
            records.append(self.get_bibtex_citation(s))
        return "\n\n".join(records)

    def save_bibtex_file(self, topic: str, target_dir: str) -> str:
        """Saves BibTeX bibliography to disk and returns absolute path."""
        os.makedirs(target_dir, exist_ok=True)
        # Sanitize filename
        safe_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic).strip('_')
        filename = f"{safe_topic}.bib"
        filepath = os.path.join(target_dir, filename)
        
        content = self.generate_bibtex_file_content()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return filepath
