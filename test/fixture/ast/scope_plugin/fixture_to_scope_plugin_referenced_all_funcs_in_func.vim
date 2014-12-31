function! FuncContext()
    function! l:ExplicitFuncLocalFunc()
    endfunction

    function! ImplicitFuncLocalFunc()
    endfunction

    call l:ExplicitFuncLocalFunc()
    call ExplicitFuncLocalFunc()

    call l:ImplicitFuncLocalFunc()
    call ImplicitFuncLocalFunc()
endfunction
