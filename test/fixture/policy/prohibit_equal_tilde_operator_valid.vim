" Case-sensitive operators are allowed
echo 'abc' ==# 'Abc'
echo 'abc' !=# 'Abc'
echo 'abc' ># 'Abc'
echo 'abc' >=# 'Abc'
echo 'abc' <# 'Abc'
echo 'abc' <=# 'Abc'
echo 'abc' =~# 'Abc'
echo 'abc' !~# 'Abc'
echo 'abc' is# 'Abc'
echo 'abc' isnot# 'Abc'

" Case-insensitive operators are allowed
echo 'abc' ==? 'Abc'
echo 'abc' !=? 'Abc'
echo 'abc' >? 'Abc'
echo 'abc' >=? 'Abc'
echo 'abc' <? 'Abc'
echo 'abc' <=? 'Abc'
echo 'abc' =~? 'Abc'
echo 'abc' !~? 'Abc'
echo 'abc' is? 'Abc'
echo 'abc' isnot? 'Abc'

let i = 0
" 'ignorecase'-sensitive operators without string comparison are allowed
echo i == 1
echo i != 1
echo i > 1
echo i >= 1
echo i < 1
echo i <= 1
echo i is 1
echo i isnot 1
