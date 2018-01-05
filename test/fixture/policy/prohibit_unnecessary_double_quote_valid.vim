" Single quote literal should not be prohibited
echo ''
echo 'foo'

" Double quote literal should not be prohibited when it contains escape sequence such as line break
echo "\001"
echo "\xff"
echo "\uffff"
echo "\b"
echo "\e"
echo "\f"
echo "\n"
echo "\t"
echo "\\"
echo "\""
echo "\<xxx>"

" Double quote literal should not be prohibited too
echo "'"

" String literal should not be prohibited
echo map([], '""')
echo map([], 'map(v:val, "x")')
