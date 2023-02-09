UPDATE document_chunk
SET chunk_text = SUBSTRING(chunk_text, LENGTH(chunk_text) - 700 + 1, 700)
WHERE doc_chunk_id IN (19055, 18447, 19047)
