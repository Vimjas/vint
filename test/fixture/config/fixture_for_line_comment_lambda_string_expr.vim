echo 'report me because I have no line config comments'

" vint: next-line -ProhibitStringPolicy
call map([], '"do not report me"')

echo 'report me because I have no line config comments, but the previous line have it'

" vint: next-line -ProhibitStringPolicy
call map(
    \ [],
    \ '"report me because I have no line config comments, but the parent node have it"'
    \)
