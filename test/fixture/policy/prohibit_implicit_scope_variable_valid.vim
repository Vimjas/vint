" Allow explicit scope variables on declaring and referencing
let g:explicit_global_var = 101
echo g:explicit_global_var

let b:buffer_local_var = 102
echo b:buffer_local_var

let w:window_local_var = 103
echo w:window_local_var

let t:tab_local_var = 104
echo t:tab_local_var

let s:script_local_var = 105
echo s:script_local_var

let v:count = 110
echo v:count

let &opt_var = 109
echo &opt_var

echo $ENV_VAR
let $ENV_VAR = 107

echo @"
let @" = 108

function! g:ExplicitGlobalFunc()
endfunction
call g:ExplicitGlobalFunc()

function! s:ScriptLocalFunc()
endfunction
call s:ScriptLocalFunc()

function! g:autoload#AutoloadFunc()
endfunction
call g:autoload#AutoloadFunc()

" We can call buffer/window/tab local function references
call b:BufferLocalFunc()
call w:WindowLocalFunc()
call t:TabLocalFunc()

function! g:FuncContext(param)
    echo a:0
    echo a:000
    echo a:param

    " Allow symbol tables
    echo a:
    echo l:
endfunction


" Allow symbol tables
echo g:
echo b:
echo w:
echo t:
echo v:

" Allow to omit g: from function names (#136)
function! ImplicitGlobalFunc()
endfunction
call ImplicitGlobalFunc()

function! autoload#ImplicitGlobalAutoloadFunc()
endfunction
call autoload#ImplicitGlobalAutoloadFunc()
