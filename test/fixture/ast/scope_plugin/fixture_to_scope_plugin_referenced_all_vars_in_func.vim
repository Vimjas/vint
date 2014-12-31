function! g:FunctionWithNoParams()
    echo a:
    echo l:
    echo a:0
    echo a:000
endfunction

function! g:FunctionWithOneParam(param)
    echo a:param
endfunction

function! g:FunctionWithTwoParams(param1, param2)
    echo a:param1
    echo a:param2
endfunction

function! g:FunctionWithVarParams(...)
    echo a:000[0]
endfunction

function! g:FunctionWithParamsAndVarParams(param_var, ...)
    echo a:param_var
endfunction

function! g:FunctionWithRange(param_with_range) range
    echo a:param_with_range
    echo a:firstline
    echo a:lastline
endfunction
