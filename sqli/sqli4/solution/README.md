# sqli4 - DropLite: intended solution

The search route in `app/app.py` builds its query by concatenation:

    SELECT id, name, size FROM files WHERE name LIKE '%<q>%'

The results page prints how many files match, and nothing in the index
is named "zzz...", so a term of the form

    zzz' OR (SELECT unicode(substr(content,N,1)) FROM files
            WHERE name='quarterly-keys.txt') < M --

returns all files (count > 0) when the Nth character of the target
file's content has a code below M, and no files otherwise. Binary
searching M recovers that character's code; stepping N across the file
reconstructs `quarterly-keys.txt` (the flag) character by character.

## Reference exploit

    python solve.py [http://host:8033]
