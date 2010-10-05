-- Bug #2634, dev.monetdb.org/bugzilla
-- Tue Oct  5 11:46:49 EDT 2010

-- To run:
--	1. Create MonetDB datbase test with user test.
-- 	2. mclient -l sql -u test -d test < bug.2634.sql
--

CREATE TABLE "test"."tbl1" (
        "id"          int           NOT NULL,
        "id1"         int           NOT NULL,
        "id2"         int           NOT NULL
)
;

CREATE TABLE "test"."tbl2" (
        "id"          int           NOT NULL,
        "title"       varchar(10)
)
;

INSERT INTO test.tbl1 VALUES (1,1,1)
;
INSERT INTO test.tbl1 VALUES (2,2,2)
;
INSERT INTO test.tbl2 VALUES (1, 'one')
;
INSERT INTO test.tbl2 VALUES (2, 'two')
;
INSERT INTO test.tbl2 VALUES (3, 'three')
;

--
-- ERROR = !MALException:group.refine:Operation failed
--         !ERROR: CTrefine: both BATs must have the same cardinality and their heads must form a 1-1 match.
--
SELECT
	tbl1.id,
	tbl1.id1,
	tbl1.id2
FROM
	test.tbl1 INNER JOIN test.tbl2 
		ON (tbl1.id1 = tbl2.id)
ORDER BY
	tbl2.title ASC,
	tbl1.id1 ASC
LIMIT 1
;

DROP TABLE "test"."tbl2";
DROP TABLE "test"."tbl1";
