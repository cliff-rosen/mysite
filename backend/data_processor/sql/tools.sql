SELECT doc_uri, length(d.doc_text), doc_text
FROM document d
WHERE domain_id = 10

SELECT doc_uri, length(dc.chunk_text)
FROM document d
JOIN document_chunk dc ON d.doc_id = dc.doc_id
WHERE domain_id = 10

SELECT *
FROM document d
WHERE domain_id = 10
 AND doc_uri = "http://www.pureti.com/benefits/"

SELECT domain_id, COUNT(*)
FROM document d
JOIN document_chunk dc ON d.doc_id = dc.doc_id
GROUP BY domain_id

SELECT domain_id, COUNT(*)
FROM document d
GROUP BY domain_id

SELECT *
FROM document
WHERE domain_id = 10
ORDER BY doc_id

SELECT *
FROM query_log
ORDER BY query_timestamp DESC
LIMIT 20
