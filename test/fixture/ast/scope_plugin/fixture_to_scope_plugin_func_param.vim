function! g:FunctionWithNoParams()
endfunction

function! g:FunctionWithOneParam(param)
endfunction

function! g:FunctionWithTwoParams(param1, param2)
endfunction

function! g:FunctionWithVarParams(...)
endfunction

function! g:FunctionWithParamsAndVarParams(param_var1, ...)
endfunction

function! g:FunctionWithRange(param) range
    " a:firstline and a:lastline is declared implicitly.
endfunction

function! g:FunctionWithDict() dict
    " self is declared implicitly.
endfunction
