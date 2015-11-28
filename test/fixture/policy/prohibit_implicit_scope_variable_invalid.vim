" Prohibit implicit scope variables
let explicit_global_var = 101

redir => output
redir END

" Prohibit implicit builtin variables
let count = 110

function! ImplicitGlobalFunc(param)
    " Make it easy to fix missing a:
    echo param
endfunction
call ImplicitGlobalFunc(0)

function! autoload#ImplicitGlobalAutoloadFunc(param)
    echo autoload#AnotherImplicitGlobalAutoloadFunc(param)
endfunction
call autoload#ImplicitGlobalAutoloadFunc(1)
