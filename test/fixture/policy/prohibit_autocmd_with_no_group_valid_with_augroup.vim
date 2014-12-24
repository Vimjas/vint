aug my_group
	au!
	au BufNewFile * echo 'foo'
aug END

augroup my_group
	autocmd!
	autocmd BufNewFile * echo 'foo'
augroup END
