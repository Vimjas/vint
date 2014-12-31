function! s:MyFunc(param)
    echo param
    echo a:1
    echo a:firstline
    echo a:lastline
endfunction


function! s:MyFuncWithRange(param1, param2, param3, ...)
    echo a:18
    echo a:19
    echo a:20
endfunction
