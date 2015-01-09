" Global-like variables should not be warned
let g:explicit_global_var = 101
let b:buffer_local_var = 102
let w:window_local_var = 103
let t:tab_local_var = 104
let implicit_global_var = 106
let $ENV_VAR = 107
let @" = 108
let &opt_var = 109
let v:count = 110

" Script-local variables should be used
let s:script_local_var = 105
echo s:script_local_var

function! s:ScriptLocalFunc()
endfunction
call s:ScriptLocalFunc()

redir => l:redit_variable
redir END
echo l:redit_variable

function! g:FuncContext(param_var, param_func, param_member)
    " Parameter should be used
    call a:param_func(a:param_var[a:param_member])

    " Function-local variables should be used
    let l:explicit_func_local_var = 106
    echo l:explicit_func_local_var

    let implicit_func_local_var = 107
    echo implicit_func_local_var

    function! ImplicitGlobalFunc()
    endfunction
    call ImplicitGlobalFunc()
endfunction

" redir variable should be used
redir => l:redit_variable
