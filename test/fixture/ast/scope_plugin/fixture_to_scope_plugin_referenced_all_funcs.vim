function! g:ExplicitGlobalFunc()
endfunction

function! b:BufferLocalFunc()
endfunction

function! w:WindowLocalFunc()
endfunction

function! t:TabLocalFunc()
endfunction

function! s:ScriptLocalFunc()
endfunction

function! ImplicitGlobalFunc()
endfunction


call g:ExplicitGlobalFunc()
call b:BufferLocalFunc()
call w:WindowLocalFunc()
call t:TabLocalFunc()
call s:ScriptLocalFunc()
call ImplicitGlobalFunc()
call g:ImplicitGlobalFunc()
