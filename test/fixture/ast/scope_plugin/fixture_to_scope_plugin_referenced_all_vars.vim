let g:explicit_global_var = 101
let b:buffer_local_var = 102
let w:window_local_var = 103
let t:tab_local_var = 104
let s:script_local_var = 105
let implicit_global_var = 106
let $ENV_VAR = 107
let @" = 108
let &opt_var = 109
let v:count = 110

echo g:explicit_global_var
echo b:buffer_local_var
echo w:window_local_var
echo t:tab_local_var
echo s:script_local_var
echo implicit_global_var
echo g:implicit_global_var
echo $ENV_VAR
echo @"
echo &opt_var
echo v:count
echo count
echo g:
echo b:
echo w:
echo t:
echo v:

call filter(g:dict, 'v:key ==# v:val')
