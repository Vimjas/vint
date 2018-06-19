" Prohibit implicit scope variables
let implicit_global_var = 101

redir => output
redir END

function! ImplicitGlobalFunc(param)
    " Make it easy to fix missing a:
    echo param
endfunction

" Implicit global variable 'i'
for i in [1, 2, 3]
endfor

call { -> implicit_global_var_in_lambda }()
