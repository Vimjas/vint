function! g:FunctionWithNoParams()
endfunction

function! g:FunctionWithOneParam(param1)
endfunction

function! g:FunctionWithTwoParams(param1, param2)
endfunction

function! g:FunctionWithVarParams(...)
endfunction

function! g:FunctionWithParamsAndVarParams(param1, ...)
endfunction

function! g:FunctionWithRange(param1) range
    " a:firstline and a:lastline is declared implicitly.
endfunction
