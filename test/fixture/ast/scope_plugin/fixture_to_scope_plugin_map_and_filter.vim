call map(s:list, 'v:val . "suffix"')
call filter(s:dict, 'v:key ==# "a"')
