
INSERT INTO document 
(
	domain_id,
	doc_uri,
	doc_title,
	doc_text
)
SELECT 	
 	11,
	doc_uri,
	doc_title,
	doc_text
FROM document
WHERE domain_id = 10

INSERT INTO document_chunk
(
	doc_id, chunk_text, chunk_embedding
)
SELECT d.doc_id, chunk.chunk_text, chunk.chunk_embedding 
FROM (
	SELECT doc_id, chunk_text, chunk_embedding
	FROM	document_chunk 
	WHERE doc_id >= 3369 AND doc_id < 3579
	) AS chunk
JOIN (
	SELECT distinct doc_id, doc_uri
	FROM document
	WHERE doc_id >= 3369 AND doc_id < 3579
	) AS doc1 ON chunk.doc_id = doc1.doc_id
JOIN (
	SELECT distinct doc_id, doc_uri
	FROM document
	WHERE doc_id >= 3579
	) AS d ON doc1.doc_uri = d.doc_uri

first pdf: 3834
535 chunks
209 records IN document WITH domain_id = 9
3787
209
3578
209
3369
max chunk id 13153 is 3578

