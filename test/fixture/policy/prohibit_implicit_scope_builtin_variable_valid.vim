" Allow variables that is not builtin variable and do not have imlicit scope.
let g:explicit_global_var = 101
echo g:explicit_global_var

let implicit_global_var = 101
echo implicit_global_var

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

let char = 110
echo char

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

    let l:explicit_func_local_var = 110
    echo l:explicit_func_local_var

    let implicit_func_local_var = 111
    echo implicit_func_local_var
endfunction


" Allow symbol tables
echo g:
echo b:
echo w:
echo t:
echo v:
