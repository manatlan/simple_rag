# -*- coding: utf-8 -*-
import re
from typing import List

def _split_paragraph(text: str, chunk_size: int) -> List[str]:
    """Splits a single paragraph into smaller chunks by words if it's too long."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    current_chunk = ""
    words = text.split(' ')
    for word in words:
        if len(current_chunk) + len(word) + 1 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word
        else:
            current_chunk += (' ' + word) if current_chunk else word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def split_markdown(markdown_text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits a markdown text by headers and paragraphs, handling oversized paragraphs and overlap.
    """
    header_splits = re.split(r'(^#+\s.*)', markdown_text, flags=re.MULTILINE)
    final_chunks = []

    def process_content(content: str, header: str = ""):
        paragraphs = content.split('\n\n')
        current_chunk_paragraphs = []

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            # Handle oversized paragraphs
            effective_chunk_size = chunk_size - len(header) - 2 if header else chunk_size
            if len(p) > effective_chunk_size:
                if current_chunk_paragraphs:
                    # Finalize and add the chunk before the long paragraph
                    final_chunk_text = "\n\n".join(current_chunk_paragraphs)
                    final_chunks.append((header + "\n\n" + final_chunk_text) if header else final_chunk_text)

                # Split the long paragraph and add its chunks
                sub_chunks = _split_paragraph(p, effective_chunk_size)
                for sub_chunk in sub_chunks:
                    final_chunks.append((header + "\n\n" + sub_chunk) if header else sub_chunk)

                # Use the end of the last sub-chunk for overlap
                current_chunk_paragraphs = [final_chunks[-1][-overlap:]]
                continue

            # Check if adding the new paragraph will exceed the chunk size
            temp_chunk_text = "\n\n".join(current_chunk_paragraphs + [p])
            temp_full_chunk = (header + "\n\n" + temp_chunk_text) if header else temp_chunk_text

            if len(temp_full_chunk) > chunk_size:
                if current_chunk_paragraphs:
                    final_chunk_text = "\n\n".join(current_chunk_paragraphs)
                    final_chunks.append((header + "\n\n" + final_chunk_text) if header else final_chunk_text)
                    # Simple overlap: just start new chunk with the current paragraph
                    current_chunk_paragraphs = [p]
                else: # current paragraph is larger than chunk size
                     current_chunk_paragraphs = [p]

            else:
                current_chunk_paragraphs.append(p)

        if current_chunk_paragraphs:
            final_chunk_text = "\n\n".join(current_chunk_paragraphs)
            final_chunks.append((header + "\n\n" + final_chunk_text) if header else final_chunk_text)

    if header_splits[0].strip():
        process_content(header_splits[0].strip())

    for i in range(1, len(header_splits), 2):
        header = header_splits[i].strip()
        content = header_splits[i+1].strip()
        process_content(content, header=header)

    return final_chunks
