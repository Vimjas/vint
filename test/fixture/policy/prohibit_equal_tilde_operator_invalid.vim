" ignorecase-sensitive operators are prohibited with alpha-only on both sides.
echo 'abc' == 'Abc'
echo 'abc' != 'Abc'
echo 'abc' > 'Abc'
echo 'abc' >= 'Abc'
echo 'abc' < 'Abc'
echo 'abc' <= 'Abc'
echo 'abc' =~ 'Abc'
echo 'abc' !~ 'Abc'
echo 'abc' is 'Abc'
echo 'abc' isnot 'Abc'

let i = 0
" ignorecase-sensitive operators are prohibited with alpha on one side.
echo i == 'Abc'
echo i != 'Abc'
echo i > 'Abc'
echo i >= 'Abc'
echo i < 'Abc'
echo i <= 'Abc'
echo i =~ 'Abc'
echo i !~ 'Abc'
echo i is 'Abc'
echo i isnot 'Abc'

" prohibited with alpha on one side only.
echo 'abc' == '...'
echo '...' == 'abc'
