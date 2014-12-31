call dict.DotFunctionCall()
call dict['SubscriptFunctionCall']()
call dict['SubscriptDynamicFunctionCall' + 0]()

let list_slice[0:1] = [99, 99]
let dict['subscript_var'] = 10
let dict.dot_var = 10
let curry_{'name'} = 10
