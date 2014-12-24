au! my_group
au my_group BufNewFile * echo 'foo'

autocmd! my_group
autocmd my_group BufNewFile * echo 'foo'
