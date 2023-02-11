
#SELECT * FROM query_log ORDER BY query_id DESC

SELECT LENGTH(chunk_text), * from document_chunk where doc_chunk_id IN (19840, 19514, 19799, 19766, 19763, 19769, 19781, 19844, 19775, 19821)

#DELETE FROM document_chunk WHERE doc_id = 5644


/*
5644

17184 - 9 = 17175

SELECT count(*)
FROM document_chunk
WHERE doc_chunk_ID IN (19826,19827,19828,19829,19830,19831,19832,19833,19834)

SELECT GROUP_CONCAT(doc_chunk_id)
FROM document_chunk
WHERE doc_id = 5644

SELECT domain_id, dc.doc_id, doc_uri, doc_text, chunk_text, LENGTH(chunk_text), doc_chunk_id
FROM document_chunk dc
JOIN document d ON dc.doc_id = d.doc_id
WHERE LENGTH(chunk_text) > 2000
and domain_id = 16

document_chunk
SET chunk_text = SUBSTRING(chunk_text, LENGTH(chunk_text) - 700 + 1, 700)
WHERE doc_chunk_id IN (19055, 18447, 19047)

SELECT * FROM query_log ORDER BY query_id DESC
LIMIT 10

SELECT domain_id, LENGTH(chunk_text), doc_chunk_id
FROM document_chunk dc
JOIN document d ON dc.doc_id = d.doc_id
WHERE LENGTH(chunk_text) > 2000
ORDER BY domain_id

SELECT *
FROM document_chunk
WHERE doc_chunk_id IN (18696, 18449, 18718, 18705, 18906, 18714, 18711, 18683, 18719, 18702)



*/