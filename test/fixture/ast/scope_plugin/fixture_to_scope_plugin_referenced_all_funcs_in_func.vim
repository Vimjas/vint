function! FuncContext()
    function! g:ExplicitGlobalFunc()
    endfunction

    function! ImplicitGlobalFunc()
    endfunction

    function! s:ExplicitScriptLocalFunc()
    endfunction

    call g:ExplicitGlobalFunc()
    call ImplicitGlobalFunc()
    call s:ExplicitScriptLocalFunc()
endfunction
