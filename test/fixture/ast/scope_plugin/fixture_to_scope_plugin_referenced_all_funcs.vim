function! g:ExplicitGlobalFunc()
endfunction

function! s:ScriptLocalFunc()
endfunction

function! ImplicitGlobalFunc()
endfunction


call g:ExplicitGlobalFunc()
call s:ScriptLocalFunc()
call ImplicitGlobalFunc()
call g:ImplicitGlobalFunc()
