function! s:FuncContext()
    " There are not function local variables but be builtin variables.
    " See :help local-variable
    let count = 100
    echo count
endfunction
