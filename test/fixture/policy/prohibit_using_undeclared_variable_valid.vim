" Can use declared variables
echo g:declared_on_other_var1
echo b:declared_on_other_var2
echo w:declared_on_other_var3
echo t:declared_on_other_var4
echo declared_on_other_var5
echo v:declared_on_other_var6
echo &declared_on_other_var7

call g:DeclaredOnOtherFunc1()
call DeclaredOnOtherFunc2()
call localtime() " built-in function

" Declare variables
let g:declared_var1 = 0
let b:declared_var2 = 0
let w:declared_var3 = 0
let t:declared_var4 = 0
let s:declared_var5 = 0
let declared_var6 = 0

function! MyFunc(param1, param2, ...) range
    " Prepare function local variables
    let l:explicit_func_local_var = 0
    let implicit_func_local_var = 0

    " Use prepared function local variables
    echo l:explicit_func_local_var
    echo implicit_func_local_var

    " Use prepared built-in function local variables
    echo a:000
    echo a:000[1]
    echo a:0
    echo a:param1
    echo a:param2
    echo a:firstline
    echo a:lastline

    " Use prepared variables
    echo g:declared_var1
    echo b:declared_var2
    echo w:declared_var3
    echo t:declared_var4
    echo s:declared_var5
    echo g:declared_var6

    " Use prepared variables
    echo g:declared_on_other_var1
    echo b:declared_on_other_var2
    echo w:declared_on_other_var3
    echo t:declared_on_other_var4
    echo v:declared_on_other_var6
    echo &declared_on_other_var7

    call g:DeclaredOnOtherFunc1()
    call DeclaredOnOtherFunc2()
    call localtime() " built-in function
endfunction

call MyFunc()
