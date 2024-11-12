CREATE OR REPLACE FUNCTION array_undup(ANYARRAY)
RETURNS ANYARRAY
LANGUAGE SQL
AS $$
SELECT ARRAY(
    SELECT DISTINCT $1[i]
    FROM generate_series(
        array_lower($1,1),
        array_upper($1,1)
    ) AS i
);
$$;