echo s:undeclared_var1

function! MyFuncWithNoRange(param1, param2, ...)
    " a:firstline and a:lastline can use when range attribute is set
    echo a:firstline
    echo a:lastline
endfunction

function! MyFunc(param1, param2, ...)
    echo l:undeclared_var2
    echo undeclared_var3
    echo a:undeclared_param
    echo s:undeclared_var1
endfunction

call s:UndeclaredFunc()
