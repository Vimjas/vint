" Script-local variables should be used
let s:script_local_var = 105

function! s:ScriptLocalFunc()
endfunction

function! g:FuncContext(param_var, param_func)
    " Parameter should be used

    " Function-local variables should be used
    let l:explicit_func_local_var = 106
    let implicit_func_local_var = 107
endfunction
