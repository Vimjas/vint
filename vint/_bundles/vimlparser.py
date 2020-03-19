#!/usr/bin/env python3
# usage: python3 vimlparser.py [--neovim] foo.vim

import sys
import re


def main():
    use_neovim = sys.argv[1] == "--neovim"

    r = StringReader(viml_readfile(sys.argv[-1]))
    p = VimLParser(use_neovim)
    c = Compiler()
    try:
        for line in c.compile(p.parse(r)):
            print(line)
    except VimLParserException as e:
        print(e)
        sys.exit(1)


class VimLParserException(Exception):
    pass


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


pat_vim2py = {
    "[0-9a-zA-Z]": "[0-9a-zA-Z]",
    "[@*!=><&~#]": "[@*!=><&~#]",
    "\\<ARGOPT\\>": "\\bARGOPT\\b",
    "\\<BANG\\>": "\\bBANG\\b",
    "\\<EDITCMD\\>": "\\bEDITCMD\\b",
    "\\<NOTRLCOM\\>": "\\bNOTRLCOM\\b",
    "\\<TRLBAR\\>": "\\bTRLBAR\\b",
    "\\<USECTRLV\\>": "\\bUSECTRLV\\b",
    "\\<USERCMD\\>": "\\bUSERCMD\\b",
    "\\<\\(XFILE\\|FILES\\|FILE1\\)\\>": "\\b(XFILE|FILES|FILE1)\\b",
    "\\S": "\\S",
    "\\a": "[A-Za-z]",
    "\\d": "\\d",
    "\\h": "[A-Za-z_]",
    "\\s": "\\s",
    "\\v^d%[elete][lp]$": "^d(elete|elet|ele|el|e)[lp]$",
    "\\v^s%(c[^sr][^i][^p]|g|i[^mlg]|I|r[^e])":
        "^s(c[^sr][^i][^p]|g|i[^mlg]|I|r[^e])",
    "\\w": "[0-9A-Za-z_]",
    "\\w\\|[:#]": "[0-9A-Za-z_]|[:#]",
    "\\x": "[0-9A-Fa-f]",
    "^++": r"^\+\+",
    "^++bad=\\(keep\\|drop\\|.\\)\\>": "^\\+\\+bad=(keep|drop|.)\\b",
    "^++bad=drop": "^\\+\\+bad=drop",
    "^++bad=keep": "^\\+\\+bad=keep",
    "^++bin\\>": "^\\+\\+bin\\b",
    "^++edit\\>": "^\\+\\+edit\\b",
    "^++enc=\\S": "^\\+\\+enc=\\S",
    "^++encoding=\\S": "^\\+\\+encoding=\\S",
    "^++ff=\\(dos\\|unix\\|mac\\)\\>": "^\\+\\+ff=(dos|unix|mac)\\b",
    "^++fileformat=\\(dos\\|unix\\|mac\\)\\>":
        "^\\+\\+fileformat=(dos|unix|mac)\\b",
    "^++nobin\\>": "^\\+\\+nobin\\b",
    "^[A-Z]": "^[A-Z]",
    "^\\$\\w\\+": "^\\$[0-9A-Za-z_]+",
    "^\\(!\\|global\\|vglobal\\)$": "^(!|global|vglobal)$",
    "^\\(WHILE\\|FOR\\)$": "^(WHILE|FOR)$",
    "^\\(vimgrep\\|vimgrepadd\\|lvimgrep\\|lvimgrepadd\\)$":
        "^(vimgrep|vimgrepadd|lvimgrep|lvimgrepadd)$",
    "^\\d": "^\\d",
    "^\\h": "^[A-Za-z_]",
    "^\\s": "^\\s",
    "^\\s*\\\\": "^\\s*\\\\",
    "^[ \\t]$": "^[ \\t]$",
    "^[A-Za-z]$": "^[A-Za-z]$",
    "^[0-9A-Za-z]$": "^[0-9A-Za-z]$",
    "^[0-9]$": "^[0-9]$",
    "^[0-9A-Fa-f]$": "^[0-9A-Fa-f]$",
    "^[0-9A-Za-z_]$": "^[0-9A-Za-z_]$",
    "^[A-Za-z_]$": "^[A-Za-z_]$",
    "^[0-9A-Za-z_:#]$": "^[0-9A-Za-z_:#]$",
    "^[A-Za-z_][0-9A-Za-z_]*$": "^[A-Za-z_][0-9A-Za-z_]*$",
    "^[A-Z]$": "^[A-Z]$",
    "^[a-z]$": "^[a-z]$",
    "^[vgslabwt]:$\\|^\\([vgslabwt]:\\)\\?[A-Za-z_][0-9A-Za-z_#]*$":
        "^[vgslabwt]:$|^([vgslabwt]:)?[A-Za-z_][0-9A-Za-z_#]*$",
    "^[0-7]$": "^[0-7]$",
    "^[0-9A-Fa-f][0-9A-Fa-f]$": "^[0-9A-Fa-f][0-9A-Fa-f]$",
    r"^\.[0-9A-Fa-f]$": r"^\.[0-9A-Fa-f]$",
    "^[0-9A-Fa-f][^0-9A-Fa-f]$": "^[0-9A-Fa-f][^0-9A-Fa-f]$",
    "^[^a-z]\\S\\+$": "^[^a-z]\\S\\+$",
}


def viml_add(lst, item):
    lst.append(item)


def viml_call(func, *args):
    func(*args)


def viml_char2nr(c):
    return ord(c)


def viml_empty(obj):
    return len(obj) == 0


def viml_equalci(a, b):
    return a.lower() == b.lower()


def viml_eqreg(s, reg):
    return re.search(pat_vim2py[reg], s, re.IGNORECASE)


def viml_eqregh(s, reg):
    return re.search(pat_vim2py[reg], s)


def viml_eqregq(s, reg):
    return re.search(pat_vim2py[reg], s, re.IGNORECASE)


def viml_escape(s, chars):
    r = ""
    for c in s:
        if c in chars:
            r += "\\" + c
        else:
            r += c
    return r


def viml_extend(obj, item):
    obj.extend(item)


def viml_insert(lst, item, idx=0):
    lst.insert(idx, item)


def viml_join(lst, sep):
    return sep.join(lst)


def viml_keys(obj):
    return obj.keys()


def viml_len(obj):
    if type(obj) is str:
        if sys.version_info < (3, 0):
            b = bytes(obj)
        else:
            b = bytes(obj, "utf8")
        return len(b)
    return len(obj)


def viml_printf(*args):
    if len(args) == 1:
        return args[0]
    else:
        return args[0] % args[1:]


def viml_range(start, end=None):
    if end is None:
        return range(start)
    else:
        return range(start, end + 1)


def viml_readfile(path):
    lines = []
    f = open(path)
    for line in f.readlines():
        lines.append(line.rstrip("\r\n"))
    f.close()
    return lines


def viml_remove(lst, idx):
    del lst[idx]


def viml_split(s, sep):
    if sep == "\\zs":
        return s
    raise VimLParserException("NotImplemented")


def viml_str2nr(s, base=10):
    return int(s, base)


def viml_string(obj):
    return str(obj)


def viml_has_key(obj, key):
    return key in obj


def viml_stridx(a, b):
    return a.find(b)


NIL = []
TRUE = 1
FALSE = 0
NODE_TOPLEVEL = 1
NODE_COMMENT = 2
NODE_EXCMD = 3
NODE_FUNCTION = 4
NODE_ENDFUNCTION = 5
NODE_DELFUNCTION = 6
NODE_RETURN = 7
NODE_EXCALL = 8
NODE_LET = 9
NODE_UNLET = 10
NODE_LOCKVAR = 11
NODE_UNLOCKVAR = 12
NODE_IF = 13
NODE_ELSEIF = 14
NODE_ELSE = 15
NODE_ENDIF = 16
NODE_WHILE = 17
NODE_ENDWHILE = 18
NODE_FOR = 19
NODE_ENDFOR = 20
NODE_CONTINUE = 21
NODE_BREAK = 22
NODE_TRY = 23
NODE_CATCH = 24
NODE_FINALLY = 25
NODE_ENDTRY = 26
NODE_THROW = 27
NODE_ECHO = 28
NODE_ECHON = 29
NODE_ECHOHL = 30
NODE_ECHOMSG = 31
NODE_ECHOERR = 32
NODE_EXECUTE = 33
NODE_TERNARY = 34
NODE_OR = 35
NODE_AND = 36
NODE_EQUAL = 37
NODE_EQUALCI = 38
NODE_EQUALCS = 39
NODE_NEQUAL = 40
NODE_NEQUALCI = 41
NODE_NEQUALCS = 42
NODE_GREATER = 43
NODE_GREATERCI = 44
NODE_GREATERCS = 45
NODE_GEQUAL = 46
NODE_GEQUALCI = 47
NODE_GEQUALCS = 48
NODE_SMALLER = 49
NODE_SMALLERCI = 50
NODE_SMALLERCS = 51
NODE_SEQUAL = 52
NODE_SEQUALCI = 53
NODE_SEQUALCS = 54
NODE_MATCH = 55
NODE_MATCHCI = 56
NODE_MATCHCS = 57
NODE_NOMATCH = 58
NODE_NOMATCHCI = 59
NODE_NOMATCHCS = 60
NODE_IS = 61
NODE_ISCI = 62
NODE_ISCS = 63
NODE_ISNOT = 64
NODE_ISNOTCI = 65
NODE_ISNOTCS = 66
NODE_ADD = 67
NODE_SUBTRACT = 68
NODE_CONCAT = 69
NODE_MULTIPLY = 70
NODE_DIVIDE = 71
NODE_REMAINDER = 72
NODE_NOT = 73
NODE_MINUS = 74
NODE_PLUS = 75
NODE_SUBSCRIPT = 76
NODE_SLICE = 77
NODE_CALL = 78
NODE_DOT = 79
NODE_NUMBER = 80
NODE_STRING = 81
NODE_LIST = 82
NODE_DICT = 83
NODE_OPTION = 85
NODE_IDENTIFIER = 86
NODE_CURLYNAME = 87
NODE_ENV = 88
NODE_REG = 89
NODE_CURLYNAMEPART = 90
NODE_CURLYNAMEEXPR = 91
NODE_LAMBDA = 92
NODE_BLOB = 93
NODE_CONST = 94
NODE_EVAL = 95
NODE_HEREDOC = 96
NODE_METHOD = 97
TOKEN_EOF = 1
TOKEN_EOL = 2
TOKEN_SPACE = 3
TOKEN_OROR = 4
TOKEN_ANDAND = 5
TOKEN_EQEQ = 6
TOKEN_EQEQCI = 7
TOKEN_EQEQCS = 8
TOKEN_NEQ = 9
TOKEN_NEQCI = 10
TOKEN_NEQCS = 11
TOKEN_GT = 12
TOKEN_GTCI = 13
TOKEN_GTCS = 14
TOKEN_GTEQ = 15
TOKEN_GTEQCI = 16
TOKEN_GTEQCS = 17
TOKEN_LT = 18
TOKEN_LTCI = 19
TOKEN_LTCS = 20
TOKEN_LTEQ = 21
TOKEN_LTEQCI = 22
TOKEN_LTEQCS = 23
TOKEN_MATCH = 24
TOKEN_MATCHCI = 25
TOKEN_MATCHCS = 26
TOKEN_NOMATCH = 27
TOKEN_NOMATCHCI = 28
TOKEN_NOMATCHCS = 29
TOKEN_IS = 30
TOKEN_ISCI = 31
TOKEN_ISCS = 32
TOKEN_ISNOT = 33
TOKEN_ISNOTCI = 34
TOKEN_ISNOTCS = 35
TOKEN_PLUS = 36
TOKEN_MINUS = 37
TOKEN_DOT = 38
TOKEN_STAR = 39
TOKEN_SLASH = 40
TOKEN_PERCENT = 41
TOKEN_NOT = 42
TOKEN_QUESTION = 43
TOKEN_COLON = 44
TOKEN_POPEN = 45
TOKEN_PCLOSE = 46
TOKEN_SQOPEN = 47
TOKEN_SQCLOSE = 48
TOKEN_COPEN = 49
TOKEN_CCLOSE = 50
TOKEN_COMMA = 51
TOKEN_NUMBER = 52
TOKEN_SQUOTE = 53
TOKEN_DQUOTE = 54
TOKEN_OPTION = 55
TOKEN_IDENTIFIER = 56
TOKEN_ENV = 57
TOKEN_REG = 58
TOKEN_EQ = 59
TOKEN_OR = 60
TOKEN_SEMICOLON = 61
TOKEN_BACKTICK = 62
TOKEN_DOTDOTDOT = 63
TOKEN_SHARP = 64
TOKEN_ARROW = 65
TOKEN_BLOB = 66
TOKEN_LITCOPEN = 67
TOKEN_DOTDOT = 68
TOKEN_HEREDOC = 69
MAX_FUNC_ARGS = 20


def isalpha(c):
    return viml_eqregh(c, "^[A-Za-z]$")


def isalnum(c):
    return viml_eqregh(c, "^[0-9A-Za-z]$")


def isdigit(c):
    return viml_eqregh(c, "^[0-9]$")


def isodigit(c):
    return viml_eqregh(c, "^[0-7]$")


def isxdigit(c):
    return viml_eqregh(c, "^[0-9A-Fa-f]$")


def iswordc(c):
    return viml_eqregh(c, "^[0-9A-Za-z_]$")


def iswordc1(c):
    return viml_eqregh(c, "^[A-Za-z_]$")


def iswhite(c):
    return viml_eqregh(c, "^[ \\t]$")


def isnamec(c):
    return viml_eqregh(c, "^[0-9A-Za-z_:#]$")


def isnamec1(c):
    return viml_eqregh(c, "^[A-Za-z_]$")


def isargname(s):
    return viml_eqregh(s, "^[A-Za-z_][0-9A-Za-z_]*$")


def isvarname(s):
    return viml_eqregh(s, "^[vgslabwt]:$\\|^\\([vgslabwt]:\\)\\?[A-Za-z_][0-9A-Za-z_#]*$")


# FIXME:
def isidc(c):
    return viml_eqregh(c, "^[0-9A-Za-z_]$")


def isupper(c):
    return viml_eqregh(c, "^[A-Z]$")


def islower(c):
    return viml_eqregh(c, "^[a-z]$")


def ExArg():
    ea = AttributeDict({})
    ea.forceit = FALSE
    ea.addr_count = 0
    ea.line1 = 0
    ea.line2 = 0
    ea.flags = 0
    ea.do_ecmd_cmd = ""
    ea.do_ecmd_lnum = 0
    ea.append = 0
    ea.usefilter = FALSE
    ea.amount = 0
    ea.regname = 0
    ea.force_bin = 0
    ea.read_edit = 0
    ea.force_ff = 0
    ea.force_enc = 0
    ea.bad_char = 0
    ea.linepos = AttributeDict({})
    ea.cmdpos = []
    ea.argpos = []
    ea.cmd = AttributeDict({})
    ea.modifiers = []
    ea.range = []
    ea.argopt = AttributeDict({})
    ea.argcmd = AttributeDict({})
    return ea


# struct node {
#   int     type
#   pos     pos
#   node    left
#   node    right
#   node    cond
#   node    rest
#   node[]  list
#   node[]  rlist
#   node[]  default_args
#   node[]  body
#   string  op
#   string  str
#   int     depth
#   variant value
# }
# TOPLEVEL .body
# COMMENT .str
# EXCMD .ea .str
# FUNCTION .ea .body .left .rlist .default_args .attr .endfunction
# ENDFUNCTION .ea
# DELFUNCTION .ea .left
# RETURN .ea .left
# EXCALL .ea .left
# LET .ea .op .left .list .rest .right
# CONST .ea .op .left .list .rest .right
# UNLET .ea .list
# LOCKVAR .ea .depth .list
# UNLOCKVAR .ea .depth .list
# IF .ea .body .cond .elseif .else .endif
# ELSEIF .ea .body .cond
# ELSE .ea .body
# ENDIF .ea
# WHILE .ea .body .cond .endwhile
# ENDWHILE .ea
# FOR .ea .body .left .list .rest .right .endfor
# ENDFOR .ea
# CONTINUE .ea
# BREAK .ea
# TRY .ea .body .catch .finally .endtry
# CATCH .ea .body .pattern
# FINALLY .ea .body
# ENDTRY .ea
# THROW .ea .left
# EVAL .ea .left
# ECHO .ea .list
# ECHON .ea .list
# ECHOHL .ea .str
# ECHOMSG .ea .list
# ECHOERR .ea .list
# EXECUTE .ea .list
# TERNARY .cond .left .right
# OR .left .right
# AND .left .right
# EQUAL .left .right
# EQUALCI .left .right
# EQUALCS .left .right
# NEQUAL .left .right
# NEQUALCI .left .right
# NEQUALCS .left .right
# GREATER .left .right
# GREATERCI .left .right
# GREATERCS .left .right
# GEQUAL .left .right
# GEQUALCI .left .right
# GEQUALCS .left .right
# SMALLER .left .right
# SMALLERCI .left .right
# SMALLERCS .left .right
# SEQUAL .left .right
# SEQUALCI .left .right
# SEQUALCS .left .right
# MATCH .left .right
# MATCHCI .left .right
# MATCHCS .left .right
# NOMATCH .left .right
# NOMATCHCI .left .right
# NOMATCHCS .left .right
# IS .left .right
# ISCI .left .right
# ISCS .left .right
# ISNOT .left .right
# ISNOTCI .left .right
# ISNOTCS .left .right
# ADD .left .right
# SUBTRACT .left .right
# CONCAT .left .right
# MULTIPLY .left .right
# DIVIDE .left .right
# REMAINDER .left .right
# NOT .left
# MINUS .left
# PLUS .left
# SUBSCRIPT .left .right
# SLICE .left .rlist
# METHOD .left .right
# CALL .left .rlist
# DOT .left .right
# NUMBER .value
# STRING .value
# LIST .value
# DICT .value
# BLOB .value
# NESTING .left
# OPTION .value
# IDENTIFIER .value
# CURLYNAME .value
# ENV .value
# REG .value
# CURLYNAMEPART .value
# CURLYNAMEEXPR .value
# LAMBDA .rlist .left
# HEREDOC .rlist .op .body
def Node(type):
    return AttributeDict({"type": type})


def Err(msg, pos):
    return viml_printf("vimlparser: %s: line %d col %d", msg, pos.lnum, pos.col)


class VimLParser:

    def __init__(self, *a000):
        if viml_len(a000) > 0:
            self.neovim = a000[0]
        else:
            self.neovim = 0
        self.find_command_cache = AttributeDict({})

    def push_context(self, node):
        viml_insert(self.context, node)

    def pop_context(self):
        viml_remove(self.context, 0)

    def find_context(self, type):
        i = 0
        for node in self.context:
            if node.type == type:
                return i
            i += 1
        return -1

    def add_node(self, node):
        viml_add(self.context[0].body, node)

    def check_missing_endfunction(self, ends, pos):
        if self.context[0].type == NODE_FUNCTION:
            raise VimLParserException(Err(viml_printf("E126: Missing :endfunction:    %s", ends), pos))

    def check_missing_endif(self, ends, pos):
        if self.context[0].type == NODE_IF or self.context[0].type == NODE_ELSEIF or self.context[0].type == NODE_ELSE:
            raise VimLParserException(Err(viml_printf("E171: Missing :endif:    %s", ends), pos))

    def check_missing_endtry(self, ends, pos):
        if self.context[0].type == NODE_TRY or self.context[0].type == NODE_CATCH or self.context[0].type == NODE_FINALLY:
            raise VimLParserException(Err(viml_printf("E600: Missing :endtry:    %s", ends), pos))

    def check_missing_endwhile(self, ends, pos):
        if self.context[0].type == NODE_WHILE:
            raise VimLParserException(Err(viml_printf("E170: Missing :endwhile:    %s", ends), pos))

    def check_missing_endfor(self, ends, pos):
        if self.context[0].type == NODE_FOR:
            raise VimLParserException(Err(viml_printf("E170: Missing :endfor:    %s", ends), pos))

    def parse(self, reader):
        self.reader = reader
        self.context = []
        toplevel = Node(NODE_TOPLEVEL)
        toplevel.pos = self.reader.getpos()
        toplevel.body = []
        self.push_context(toplevel)
        while self.reader.peek() != "<EOF>":
            self.parse_one_cmd()
        self.check_missing_endfunction("TOPLEVEL", self.reader.getpos())
        self.check_missing_endif("TOPLEVEL", self.reader.getpos())
        self.check_missing_endtry("TOPLEVEL", self.reader.getpos())
        self.check_missing_endwhile("TOPLEVEL", self.reader.getpos())
        self.check_missing_endfor("TOPLEVEL", self.reader.getpos())
        self.pop_context()
        return toplevel

    def parse_one_cmd(self):
        self.ea = ExArg()
        if self.reader.peekn(2) == "#!":
            self.parse_hashbang()
            self.reader.get()
            return
        self.reader.skip_white_and_colon()
        if self.reader.peekn(1) == "":
            self.reader.get()
            return
        if self.reader.peekn(1) == "\"":
            self.parse_comment()
            self.reader.get()
            return
        self.ea.linepos = self.reader.getpos()
        self.parse_command_modifiers()
        self.parse_range()
        self.parse_command()
        self.parse_trail()

    # FIXME:
    def parse_command_modifiers(self):
        modifiers = []
        while TRUE:
            pos = self.reader.tell()
            d = ""
            if isdigit(self.reader.peekn(1)):
                d = self.reader.read_digit()
                self.reader.skip_white()
            k = self.reader.read_alpha()
            c = self.reader.peekn(1)
            self.reader.skip_white()
            if viml_stridx("aboveleft", k) == 0 and viml_len(k) >= 3:
                # abo\%[veleft]
                viml_add(modifiers, AttributeDict({"name": "aboveleft"}))
            elif viml_stridx("belowright", k) == 0 and viml_len(k) >= 3:
                # bel\%[owright]
                viml_add(modifiers, AttributeDict({"name": "belowright"}))
            elif viml_stridx("browse", k) == 0 and viml_len(k) >= 3:
                # bro\%[wse]
                viml_add(modifiers, AttributeDict({"name": "browse"}))
            elif viml_stridx("botright", k) == 0 and viml_len(k) >= 2:
                # bo\%[tright]
                viml_add(modifiers, AttributeDict({"name": "botright"}))
            elif viml_stridx("confirm", k) == 0 and viml_len(k) >= 4:
                # conf\%[irm]
                viml_add(modifiers, AttributeDict({"name": "confirm"}))
            elif viml_stridx("keepmarks", k) == 0 and viml_len(k) >= 3:
                # kee\%[pmarks]
                viml_add(modifiers, AttributeDict({"name": "keepmarks"}))
            elif viml_stridx("keepalt", k) == 0 and viml_len(k) >= 5:
                # keepa\%[lt]
                viml_add(modifiers, AttributeDict({"name": "keepalt"}))
            elif viml_stridx("keepjumps", k) == 0 and viml_len(k) >= 5:
                # keepj\%[umps]
                viml_add(modifiers, AttributeDict({"name": "keepjumps"}))
            elif viml_stridx("keeppatterns", k) == 0 and viml_len(k) >= 5:
                # keepp\%[atterns]
                viml_add(modifiers, AttributeDict({"name": "keeppatterns"}))
            elif viml_stridx("hide", k) == 0 and viml_len(k) >= 3:
                # hid\%[e]
                if self.ends_excmds(c):
                    break
                viml_add(modifiers, AttributeDict({"name": "hide"}))
            elif viml_stridx("lockmarks", k) == 0 and viml_len(k) >= 3:
                # loc\%[kmarks]
                viml_add(modifiers, AttributeDict({"name": "lockmarks"}))
            elif viml_stridx("leftabove", k) == 0 and viml_len(k) >= 5:
                # lefta\%[bove]
                viml_add(modifiers, AttributeDict({"name": "leftabove"}))
            elif viml_stridx("noautocmd", k) == 0 and viml_len(k) >= 3:
                # noa\%[utocmd]
                viml_add(modifiers, AttributeDict({"name": "noautocmd"}))
            elif viml_stridx("noswapfile", k) == 0 and viml_len(k) >= 3:
                # :nos\%[wapfile]
                viml_add(modifiers, AttributeDict({"name": "noswapfile"}))
            elif viml_stridx("rightbelow", k) == 0 and viml_len(k) >= 6:
                # rightb\%[elow]
                viml_add(modifiers, AttributeDict({"name": "rightbelow"}))
            elif viml_stridx("sandbox", k) == 0 and viml_len(k) >= 3:
                # san\%[dbox]
                viml_add(modifiers, AttributeDict({"name": "sandbox"}))
            elif viml_stridx("silent", k) == 0 and viml_len(k) >= 3:
                # sil\%[ent]
                if c == "!":
                    self.reader.get()
                    viml_add(modifiers, AttributeDict({"name": "silent", "bang": 1}))
                else:
                    viml_add(modifiers, AttributeDict({"name": "silent", "bang": 0}))
            elif k == "tab":
                # tab
                if d != "":
                    viml_add(modifiers, AttributeDict({"name": "tab", "count": viml_str2nr(d, 10)}))
                else:
                    viml_add(modifiers, AttributeDict({"name": "tab"}))
            elif viml_stridx("topleft", k) == 0 and viml_len(k) >= 2:
                # to\%[pleft]
                viml_add(modifiers, AttributeDict({"name": "topleft"}))
            elif viml_stridx("unsilent", k) == 0 and viml_len(k) >= 3:
                # uns\%[ilent]
                viml_add(modifiers, AttributeDict({"name": "unsilent"}))
            elif viml_stridx("vertical", k) == 0 and viml_len(k) >= 4:
                # vert\%[ical]
                viml_add(modifiers, AttributeDict({"name": "vertical"}))
            elif viml_stridx("verbose", k) == 0 and viml_len(k) >= 4:
                # verb\%[ose]
                if d != "":
                    viml_add(modifiers, AttributeDict({"name": "verbose", "count": viml_str2nr(d, 10)}))
                else:
                    viml_add(modifiers, AttributeDict({"name": "verbose", "count": 1}))
            else:
                self.reader.seek_set(pos)
                break
        self.ea.modifiers = modifiers

    # FIXME:
    def parse_range(self):
        tokens = []
        while TRUE:
            while TRUE:
                self.reader.skip_white()
                c = self.reader.peekn(1)
                if c == "":
                    break
                if c == ".":
                    viml_add(tokens, self.reader.getn(1))
                elif c == "$":
                    viml_add(tokens, self.reader.getn(1))
                elif c == "'":
                    self.reader.getn(1)
                    m = self.reader.getn(1)
                    if m == "":
                        break
                    viml_add(tokens, "'" + m)
                elif c == "/":
                    self.reader.getn(1)
                    pattern, _ = self.parse_pattern(c)
                    viml_add(tokens, pattern)
                elif c == "?":
                    self.reader.getn(1)
                    pattern, _ = self.parse_pattern(c)
                    viml_add(tokens, pattern)
                elif c == "\\":
                    m = self.reader.p(1)
                    if m == "&" or m == "?" or m == "/":
                        self.reader.seek_cur(2)
                        viml_add(tokens, "\\" + m)
                    else:
                        raise VimLParserException(Err("E10: \\\\ should be followed by /, ? or &", self.reader.getpos()))
                elif isdigit(c):
                    viml_add(tokens, self.reader.read_digit())
                while TRUE:
                    self.reader.skip_white()
                    if self.reader.peekn(1) == "":
                        break
                    n = self.reader.read_integer()
                    if n == "":
                        break
                    viml_add(tokens, n)
                if self.reader.p(0) != "/" and self.reader.p(0) != "?":
                    break
            if self.reader.peekn(1) == "%":
                viml_add(tokens, self.reader.getn(1))
            elif self.reader.peekn(1) == "*":
                # && &cpoptions !~ '\*'
                viml_add(tokens, self.reader.getn(1))
            if self.reader.peekn(1) == ";":
                viml_add(tokens, self.reader.getn(1))
                continue
            elif self.reader.peekn(1) == ",":
                viml_add(tokens, self.reader.getn(1))
                continue
            break
        self.ea.range = tokens

    # FIXME:
    def parse_pattern(self, delimiter):
        pattern = ""
        endc = ""
        inbracket = 0
        while TRUE:
            c = self.reader.getn(1)
            if c == "":
                break
            if c == delimiter and inbracket == 0:
                endc = c
                break
            pattern += c
            if c == "\\":
                c = self.reader.peekn(1)
                if c == "":
                    raise VimLParserException(Err("E682: Invalid search pattern or delimiter", self.reader.getpos()))
                self.reader.getn(1)
                pattern += c
            elif c == "[":
                inbracket += 1
            elif c == "]":
                inbracket -= 1
        return [pattern, endc]

    def parse_command(self):
        self.reader.skip_white_and_colon()
        self.ea.cmdpos = self.reader.getpos()
        if self.reader.peekn(1) == "" or self.reader.peekn(1) == "\"":
            if not viml_empty(self.ea.modifiers) or not viml_empty(self.ea.range):
                self.parse_cmd_modifier_range()
            return
        self.ea.cmd = self.find_command()
        if self.ea.cmd is NIL:
            self.reader.setpos(self.ea.cmdpos)
            raise VimLParserException(Err(viml_printf("E492: Not an editor command: %s", self.reader.peekline()), self.ea.cmdpos))
        if self.reader.peekn(1) == "!" and self.ea.cmd.name != "substitute" and self.ea.cmd.name != "smagic" and self.ea.cmd.name != "snomagic":
            self.reader.getn(1)
            self.ea.forceit = TRUE
        else:
            self.ea.forceit = FALSE
        if not viml_eqregh(self.ea.cmd.flags, "\\<BANG\\>") and self.ea.forceit and not viml_eqregh(self.ea.cmd.flags, "\\<USERCMD\\>"):
            raise VimLParserException(Err("E477: No ! allowed", self.ea.cmdpos))
        if self.ea.cmd.name != "!":
            self.reader.skip_white()
        self.ea.argpos = self.reader.getpos()
        if viml_eqregh(self.ea.cmd.flags, "\\<ARGOPT\\>"):
            self.parse_argopt()
        if self.ea.cmd.name == "write" or self.ea.cmd.name == "update":
            if self.reader.p(0) == ">":
                if self.reader.p(1) != ">":
                    raise VimLParserException(Err("E494: Use w or w>>", self.ea.cmdpos))
                self.reader.seek_cur(2)
                self.reader.skip_white()
                self.ea.append = 1
            elif self.reader.peekn(1) == "!" and self.ea.cmd.name == "write":
                self.reader.getn(1)
                self.ea.usefilter = TRUE
        if self.ea.cmd.name == "read":
            if self.ea.forceit:
                self.ea.usefilter = TRUE
                self.ea.forceit = FALSE
            elif self.reader.peekn(1) == "!":
                self.reader.getn(1)
                self.ea.usefilter = TRUE
        if self.ea.cmd.name == "<" or self.ea.cmd.name == ">":
            self.ea.amount = 1
            while self.reader.peekn(1) == self.ea.cmd.name:
                self.reader.getn(1)
                self.ea.amount += 1
            self.reader.skip_white()
        if viml_eqregh(self.ea.cmd.flags, "\\<EDITCMD\\>") and not self.ea.usefilter:
            self.parse_argcmd()
        self._parse_command(self.ea.cmd.parser)

    # TODO: self[a:parser]
    def _parse_command(self, parser):
        if parser == "parse_cmd_append":
            self.parse_cmd_append()
        elif parser == "parse_cmd_break":
            self.parse_cmd_break()
        elif parser == "parse_cmd_call":
            self.parse_cmd_call()
        elif parser == "parse_cmd_catch":
            self.parse_cmd_catch()
        elif parser == "parse_cmd_common":
            self.parse_cmd_common()
        elif parser == "parse_cmd_continue":
            self.parse_cmd_continue()
        elif parser == "parse_cmd_delfunction":
            self.parse_cmd_delfunction()
        elif parser == "parse_cmd_echo":
            self.parse_cmd_echo()
        elif parser == "parse_cmd_echoerr":
            self.parse_cmd_echoerr()
        elif parser == "parse_cmd_echohl":
            self.parse_cmd_echohl()
        elif parser == "parse_cmd_echomsg":
            self.parse_cmd_echomsg()
        elif parser == "parse_cmd_echon":
            self.parse_cmd_echon()
        elif parser == "parse_cmd_else":
            self.parse_cmd_else()
        elif parser == "parse_cmd_elseif":
            self.parse_cmd_elseif()
        elif parser == "parse_cmd_endfor":
            self.parse_cmd_endfor()
        elif parser == "parse_cmd_endfunction":
            self.parse_cmd_endfunction()
        elif parser == "parse_cmd_endif":
            self.parse_cmd_endif()
        elif parser == "parse_cmd_endtry":
            self.parse_cmd_endtry()
        elif parser == "parse_cmd_endwhile":
            self.parse_cmd_endwhile()
        elif parser == "parse_cmd_execute":
            self.parse_cmd_execute()
        elif parser == "parse_cmd_finally":
            self.parse_cmd_finally()
        elif parser == "parse_cmd_finish":
            self.parse_cmd_finish()
        elif parser == "parse_cmd_for":
            self.parse_cmd_for()
        elif parser == "parse_cmd_function":
            self.parse_cmd_function()
        elif parser == "parse_cmd_if":
            self.parse_cmd_if()
        elif parser == "parse_cmd_insert":
            self.parse_cmd_insert()
        elif parser == "parse_cmd_let":
            self.parse_cmd_let()
        elif parser == "parse_cmd_const":
            self.parse_cmd_const()
        elif parser == "parse_cmd_loadkeymap":
            self.parse_cmd_loadkeymap()
        elif parser == "parse_cmd_lockvar":
            self.parse_cmd_lockvar()
        elif parser == "parse_cmd_lua":
            self.parse_cmd_lua()
        elif parser == "parse_cmd_modifier_range":
            self.parse_cmd_modifier_range()
        elif parser == "parse_cmd_mzscheme":
            self.parse_cmd_mzscheme()
        elif parser == "parse_cmd_perl":
            self.parse_cmd_perl()
        elif parser == "parse_cmd_python":
            self.parse_cmd_python()
        elif parser == "parse_cmd_python3":
            self.parse_cmd_python3()
        elif parser == "parse_cmd_return":
            self.parse_cmd_return()
        elif parser == "parse_cmd_ruby":
            self.parse_cmd_ruby()
        elif parser == "parse_cmd_tcl":
            self.parse_cmd_tcl()
        elif parser == "parse_cmd_throw":
            self.parse_cmd_throw()
        elif parser == "parse_cmd_eval":
            self.parse_cmd_eval()
        elif parser == "parse_cmd_try":
            self.parse_cmd_try()
        elif parser == "parse_cmd_unlet":
            self.parse_cmd_unlet()
        elif parser == "parse_cmd_unlockvar":
            self.parse_cmd_unlockvar()
        elif parser == "parse_cmd_usercmd":
            self.parse_cmd_usercmd()
        elif parser == "parse_cmd_while":
            self.parse_cmd_while()
        elif parser == "parse_wincmd":
            self.parse_wincmd()
        elif parser == "parse_cmd_syntax":
            self.parse_cmd_syntax()
        else:
            raise VimLParserException(viml_printf("unknown parser: %s", viml_string(parser)))

    def find_command(self):
        c = self.reader.peekn(1)
        name = ""
        if c == "k":
            self.reader.getn(1)
            name = "k"
        elif c == "s" and viml_eqregh(self.reader.peekn(5), "\\v^s%(c[^sr][^i][^p]|g|i[^mlg]|I|r[^e])"):
            self.reader.getn(1)
            name = "substitute"
        elif viml_eqregh(c, "[@*!=><&~#]"):
            self.reader.getn(1)
            name = c
        elif self.reader.peekn(2) == "py":
            name = self.reader.read_alnum()
        else:
            pos = self.reader.tell()
            name = self.reader.read_alpha()
            if name != "del" and viml_eqregh(name, "\\v^d%[elete][lp]$"):
                self.reader.seek_set(pos)
                name = self.reader.getn(viml_len(name) - 1)
        if name == "":
            return NIL
        if viml_has_key(self.find_command_cache, name):
            return self.find_command_cache[name]
        cmd = NIL
        for x in self.builtin_commands:
            if viml_stridx(x.name, name) == 0 and viml_len(name) >= x.minlen:
                del cmd
                cmd = x
                break
        if self.neovim:
            for x in self.neovim_additional_commands:
                if viml_stridx(x.name, name) == 0 and viml_len(name) >= x.minlen:
                    del cmd
                    cmd = x
                    break
            for x in self.neovim_removed_commands:
                if viml_stridx(x.name, name) == 0 and viml_len(name) >= x.minlen:
                    del cmd
                    cmd = NIL
                    break
        # FIXME: user defined command
        if (cmd is NIL or cmd.name == "Print") and viml_eqregh(name, "^[A-Z]"):
            name += self.reader.read_alnum()
            del cmd
            cmd = AttributeDict({"name": name, "flags": "USERCMD", "parser": "parse_cmd_usercmd"})
        self.find_command_cache[name] = cmd
        return cmd

    # TODO:
    def parse_hashbang(self):
        self.reader.getn(-1)

    # TODO:
    # ++opt=val
    def parse_argopt(self):
        while self.reader.p(0) == "+" and self.reader.p(1) == "+":
            s = self.reader.peekn(20)
            if viml_eqregh(s, "^++bin\\>"):
                self.reader.getn(5)
                self.ea.force_bin = 1
            elif viml_eqregh(s, "^++nobin\\>"):
                self.reader.getn(7)
                self.ea.force_bin = 2
            elif viml_eqregh(s, "^++edit\\>"):
                self.reader.getn(6)
                self.ea.read_edit = 1
            elif viml_eqregh(s, "^++ff=\\(dos\\|unix\\|mac\\)\\>"):
                self.reader.getn(5)
                self.ea.force_ff = self.reader.read_alpha()
            elif viml_eqregh(s, "^++fileformat=\\(dos\\|unix\\|mac\\)\\>"):
                self.reader.getn(13)
                self.ea.force_ff = self.reader.read_alpha()
            elif viml_eqregh(s, "^++enc=\\S"):
                self.reader.getn(6)
                self.ea.force_enc = self.reader.read_nonwhite()
            elif viml_eqregh(s, "^++encoding=\\S"):
                self.reader.getn(11)
                self.ea.force_enc = self.reader.read_nonwhite()
            elif viml_eqregh(s, "^++bad=\\(keep\\|drop\\|.\\)\\>"):
                self.reader.getn(6)
                if viml_eqregh(s, "^++bad=keep"):
                    self.ea.bad_char = self.reader.getn(4)
                elif viml_eqregh(s, "^++bad=drop"):
                    self.ea.bad_char = self.reader.getn(4)
                else:
                    self.ea.bad_char = self.reader.getn(1)
            elif viml_eqregh(s, "^++"):
                raise VimLParserException(Err("E474: Invalid Argument", self.reader.getpos()))
            else:
                break
            self.reader.skip_white()

    # TODO:
    # +command
    def parse_argcmd(self):
        if self.reader.peekn(1) == "+":
            self.reader.getn(1)
            if self.reader.peekn(1) == " ":
                self.ea.do_ecmd_cmd = "$"
            else:
                self.ea.do_ecmd_cmd = self.read_cmdarg()

    def read_cmdarg(self):
        r = ""
        while TRUE:
            c = self.reader.peekn(1)
            if c == "" or iswhite(c):
                break
            self.reader.getn(1)
            if c == "\\":
                c = self.reader.getn(1)
            r += c
        return r

    def parse_comment(self):
        npos = self.reader.getpos()
        c = self.reader.get()
        if c != "\"":
            raise VimLParserException(Err(viml_printf("unexpected character: %s", c), npos))
        node = Node(NODE_COMMENT)
        node.pos = npos
        node.str = self.reader.getn(-1)
        self.add_node(node)

    def parse_trail(self):
        self.reader.skip_white()
        c = self.reader.peek()
        if c == "<EOF>":
            # pass
            pass
        elif c == "<EOL>":
            self.reader.get()
        elif c == "|":
            self.reader.get()
        elif c == "\"":
            self.parse_comment()
            self.reader.get()
        else:
            raise VimLParserException(Err(viml_printf("E488: Trailing characters: %s", c), self.reader.getpos()))

    # modifier or range only command line
    def parse_cmd_modifier_range(self):
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = self.reader.getstr(self.ea.linepos, self.reader.getpos())
        self.add_node(node)

    # TODO:
    def parse_cmd_common(self):
        end = self.reader.getpos()
        if viml_eqregh(self.ea.cmd.flags, "\\<TRLBAR\\>") and not self.ea.usefilter:
            end = self.separate_nextcmd()
        elif self.ea.cmd.name == "!" or self.ea.cmd.name == "global" or self.ea.cmd.name == "vglobal" or self.ea.usefilter:
            while TRUE:
                end = self.reader.getpos()
                if self.reader.getn(1) == "":
                    break
        else:
            while TRUE:
                end = self.reader.getpos()
                if self.reader.getn(1) == "":
                    break
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = self.reader.getstr(self.ea.linepos, end)
        self.add_node(node)

    def separate_nextcmd(self):
        if self.ea.cmd.name == "vimgrep" or self.ea.cmd.name == "vimgrepadd" or self.ea.cmd.name == "lvimgrep" or self.ea.cmd.name == "lvimgrepadd":
            self.skip_vimgrep_pat()
        pc = ""
        end = self.reader.getpos()
        nospend = end
        while TRUE:
            end = self.reader.getpos()
            if not iswhite(pc):
                nospend = end
            c = self.reader.peek()
            if c == "<EOF>" or c == "<EOL>":
                break
            elif c == "\x16":
                # <C-V>
                self.reader.get()
                end = self.reader.getpos()
                nospend = self.reader.getpos()
                c = self.reader.peek()
                if c == "<EOF>" or c == "<EOL>":
                    break
                self.reader.get()
            elif self.reader.peekn(2) == "`=" and viml_eqregh(self.ea.cmd.flags, "\\<\\(XFILE\\|FILES\\|FILE1\\)\\>"):
                self.reader.getn(2)
                self.parse_expr()
                c = self.reader.peekn(1)
                if c != "`":
                    raise VimLParserException(Err(viml_printf("unexpected character: %s", c), self.reader.getpos()))
                self.reader.getn(1)
            elif c == "|" or c == "\n" or c == "\"" and not viml_eqregh(self.ea.cmd.flags, "\\<NOTRLCOM\\>") and (self.ea.cmd.name != "@" and self.ea.cmd.name != "*" or self.reader.getpos() != self.ea.argpos) and (self.ea.cmd.name != "redir" or self.reader.getpos().i != self.ea.argpos.i + 1 or pc != "@"):
                has_cpo_bar = FALSE
                # &cpoptions =~ 'b'
                if (not has_cpo_bar or not viml_eqregh(self.ea.cmd.flags, "\\<USECTRLV\\>")) and pc == "\\":
                    self.reader.get()
                else:
                    break
            else:
                self.reader.get()
            pc = c
        if not viml_eqregh(self.ea.cmd.flags, "\\<NOTRLCOM\\>"):
            end = nospend
        return end

    # FIXME
    def skip_vimgrep_pat(self):
        if self.reader.peekn(1) == "":
            # pass
            pass
        elif isidc(self.reader.peekn(1)):
            # :vimgrep pattern fname
            self.reader.read_nonwhite()
        else:
            # :vimgrep /pattern/[g][j] fname
            c = self.reader.getn(1)
            _, endc = self.parse_pattern(c)
            if c != endc:
                return
            while self.reader.p(0) == "g" or self.reader.p(0) == "j":
                self.reader.getn(1)

    def parse_cmd_append(self):
        self.reader.setpos(self.ea.linepos)
        cmdline = self.reader.readline()
        lines = [cmdline]
        m = "."
        while TRUE:
            if self.reader.peek() == "<EOF>":
                break
            line = self.reader.getn(-1)
            viml_add(lines, line)
            if line == m:
                break
            self.reader.get()
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = viml_join(lines, "\n")
        self.add_node(node)

    def parse_cmd_insert(self):
        self.parse_cmd_append()

    def parse_cmd_loadkeymap(self):
        self.reader.setpos(self.ea.linepos)
        cmdline = self.reader.readline()
        lines = [cmdline]
        while TRUE:
            if self.reader.peek() == "<EOF>":
                break
            line = self.reader.readline()
            viml_add(lines, line)
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = viml_join(lines, "\n")
        self.add_node(node)

    def parse_cmd_lua(self):
        lines = []
        self.reader.skip_white()
        if self.reader.peekn(2) == "<<":
            self.reader.getn(2)
            self.reader.skip_white()
            m = self.reader.readline()
            if m == "":
                m = "."
            self.reader.setpos(self.ea.linepos)
            cmdline = self.reader.getn(-1)
            lines = [cmdline]
            self.reader.get()
            while TRUE:
                if self.reader.peek() == "<EOF>":
                    break
                line = self.reader.getn(-1)
                viml_add(lines, line)
                if line == m:
                    break
                self.reader.get()
        else:
            self.reader.setpos(self.ea.linepos)
            cmdline = self.reader.getn(-1)
            lines = [cmdline]
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = viml_join(lines, "\n")
        self.add_node(node)

    def parse_cmd_mzscheme(self):
        self.parse_cmd_lua()

    def parse_cmd_perl(self):
        self.parse_cmd_lua()

    def parse_cmd_python(self):
        self.parse_cmd_lua()

    def parse_cmd_python3(self):
        self.parse_cmd_lua()

    def parse_cmd_ruby(self):
        self.parse_cmd_lua()

    def parse_cmd_tcl(self):
        self.parse_cmd_lua()

    def parse_cmd_finish(self):
        self.parse_cmd_common()
        if self.context[0].type == NODE_TOPLEVEL:
            self.reader.seek_end(0)

    # FIXME
    def parse_cmd_usercmd(self):
        self.parse_cmd_common()

    def parse_cmd_function(self):
        pos = self.reader.tell()
        self.reader.skip_white()
        # :function
        if self.ends_excmds(self.reader.peek()):
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        # :function /pattern
        if self.reader.peekn(1) == "/":
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        left = self.parse_lvalue_func()
        self.reader.skip_white()
        if left.type == NODE_IDENTIFIER:
            s = left.value
            ss = viml_split(s, "\\zs")
            if ss[0] != "<" and ss[0] != "_" and not isupper(ss[0]) and viml_stridx(s, ":") == -1 and viml_stridx(s, "#") == -1:
                raise VimLParserException(Err(viml_printf("E128: Function name must start with a capital or contain a colon: %s", s), left.pos))
        # :function {name}
        if self.reader.peekn(1) != "(":
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        # :function[!] {name}([arguments]) [range] [abort] [dict] [closure]
        node = Node(NODE_FUNCTION)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.left = left
        node.rlist = []
        node.default_args = []
        node.attr = AttributeDict({"range": 0, "abort": 0, "dict": 0, "closure": 0})
        node.endfunction = NIL
        self.reader.getn(1)
        tokenizer = ExprTokenizer(self.reader)
        if tokenizer.peek().type == TOKEN_PCLOSE:
            tokenizer.get()
        else:
            named = AttributeDict({})
            while TRUE:
                varnode = Node(NODE_IDENTIFIER)
                token = tokenizer.get()
                if token.type == TOKEN_IDENTIFIER:
                    if not isargname(token.value) or token.value == "firstline" or token.value == "lastline":
                        raise VimLParserException(Err(viml_printf("E125: Illegal argument: %s", token.value), token.pos))
                    elif viml_has_key(named, token.value):
                        raise VimLParserException(Err(viml_printf("E853: Duplicate argument name: %s", token.value), token.pos))
                    named[token.value] = 1
                    varnode.pos = token.pos
                    varnode.value = token.value
                    viml_add(node.rlist, varnode)
                    if tokenizer.peek().type == TOKEN_EQ:
                        tokenizer.get()
                        viml_add(node.default_args, self.parse_expr())
                    elif viml_len(node.default_args) > 0:
                        raise VimLParserException(Err("E989: Non-default argument follows default argument", varnode.pos))
                    # XXX: Vim doesn't skip white space before comma.  F(a ,b) => E475
                    if iswhite(self.reader.p(0)) and tokenizer.peek().type == TOKEN_COMMA:
                        raise VimLParserException(Err("E475: Invalid argument: White space is not allowed before comma", self.reader.getpos()))
                    token = tokenizer.get()
                    if token.type == TOKEN_COMMA:
                        # XXX: Vim allows last comma.  F(a, b, ) => OK
                        if tokenizer.peek().type == TOKEN_PCLOSE:
                            tokenizer.get()
                            break
                    elif token.type == TOKEN_PCLOSE:
                        break
                    else:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                elif token.type == TOKEN_DOTDOTDOT:
                    varnode.pos = token.pos
                    varnode.value = token.value
                    viml_add(node.rlist, varnode)
                    token = tokenizer.get()
                    if token.type == TOKEN_PCLOSE:
                        break
                    else:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                else:
                    raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        while TRUE:
            self.reader.skip_white()
            epos = self.reader.getpos()
            key = self.reader.read_alpha()
            if key == "":
                break
            elif key == "range":
                node.attr.range = TRUE
            elif key == "abort":
                node.attr.abort = TRUE
            elif key == "dict":
                node.attr.dict = TRUE
            elif key == "closure":
                node.attr.closure = TRUE
            else:
                raise VimLParserException(Err(viml_printf("unexpected token: %s", key), epos))
        self.add_node(node)
        self.push_context(node)

    def parse_cmd_endfunction(self):
        self.check_missing_endif("ENDFUNCTION", self.ea.cmdpos)
        self.check_missing_endtry("ENDFUNCTION", self.ea.cmdpos)
        self.check_missing_endwhile("ENDFUNCTION", self.ea.cmdpos)
        self.check_missing_endfor("ENDFUNCTION", self.ea.cmdpos)
        if self.context[0].type != NODE_FUNCTION:
            raise VimLParserException(Err("E193: :endfunction not inside a function", self.ea.cmdpos))
        self.reader.getn(-1)
        node = Node(NODE_ENDFUNCTION)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.context[0].endfunction = node
        self.pop_context()

    def parse_cmd_delfunction(self):
        node = Node(NODE_DELFUNCTION)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.left = self.parse_lvalue_func()
        self.add_node(node)

    def parse_cmd_return(self):
        if self.find_context(NODE_FUNCTION) == -1:
            raise VimLParserException(Err("E133: :return not inside a function", self.ea.cmdpos))
        node = Node(NODE_RETURN)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.left = NIL
        self.reader.skip_white()
        c = self.reader.peek()
        if c == "\"" or not self.ends_excmds(c):
            node.left = self.parse_expr()
        self.add_node(node)

    def parse_cmd_call(self):
        node = Node(NODE_EXCALL)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.reader.skip_white()
        c = self.reader.peek()
        if self.ends_excmds(c):
            raise VimLParserException(Err("E471: Argument required", self.reader.getpos()))
        node.left = self.parse_expr()
        if node.left.type != NODE_CALL:
            raise VimLParserException(Err("Not an function call", node.left.pos))
        self.add_node(node)

    def parse_heredoc(self):
        node = Node(NODE_HEREDOC)
        node.pos = self.ea.cmdpos
        node.op = ""
        node.rlist = []
        node.body = []
        while TRUE:
            self.reader.skip_white()
            key = self.reader.read_word()
            if key == "":
                break
            if not islower(key[0]):
                node.op = key
                break
            else:
                viml_add(node.rlist, key)
        if node.op == "":
            raise VimLParserException(Err("E172: Missing marker", self.reader.getpos()))
        self.parse_trail()
        while TRUE:
            if self.reader.peek() == "<EOF>":
                break
            line = self.reader.getn(-1)
            if line == node.op:
                return node
            viml_add(node.body, line)
            self.reader.get()
        raise VimLParserException(Err(viml_printf("E990: Missing end marker '%s'", node.op), self.reader.getpos()))

    def parse_cmd_let(self):
        pos = self.reader.tell()
        self.reader.skip_white()
        # :let
        if self.ends_excmds(self.reader.peek()):
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        lhs = self.parse_letlhs()
        self.reader.skip_white()
        s1 = self.reader.peekn(1)
        s2 = self.reader.peekn(2)
        # TODO check scriptversion?
        if s2 == "..":
            s2 = self.reader.peekn(3)
        elif s2 == "=<":
            s2 = self.reader.peekn(3)
        # :let {var-name} ..
        if self.ends_excmds(s1) or s2 != "+=" and s2 != "-=" and s2 != ".=" and s2 != "..=" and s2 != "*=" and s2 != "/=" and s2 != "%=" and s2 != "=<<" and s1 != "=":
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        # :let left op right
        node = Node(NODE_LET)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.op = ""
        node.left = lhs.left
        node.list = lhs.list
        node.rest = lhs.rest
        node.right = NIL
        if s2 == "+=" or s2 == "-=" or s2 == ".=" or s2 == "..=" or s2 == "*=" or s2 == "/=" or s2 == "%=":
            self.reader.getn(viml_len(s2))
            node.op = s2
        elif s2 == "=<<":
            self.reader.getn(viml_len(s2))
            self.reader.skip_white()
            node.op = s2
            node.right = self.parse_heredoc()
            self.add_node(node)
            return
        elif s1 == "=":
            self.reader.getn(1)
            node.op = s1
        else:
            raise VimLParserException("NOT REACHED")
        node.right = self.parse_expr()
        self.add_node(node)

    def parse_cmd_const(self):
        pos = self.reader.tell()
        self.reader.skip_white()
        # :const
        if self.ends_excmds(self.reader.peek()):
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        lhs = self.parse_constlhs()
        self.reader.skip_white()
        s1 = self.reader.peekn(1)
        # :const {var-name}
        if self.ends_excmds(s1) or s1 != "=":
            self.reader.seek_set(pos)
            self.parse_cmd_common()
            return
        # :const left op right
        node = Node(NODE_CONST)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.reader.getn(1)
        node.op = s1
        node.left = lhs.left
        node.list = lhs.list
        node.rest = lhs.rest
        node.right = self.parse_expr()
        self.add_node(node)

    def parse_cmd_unlet(self):
        node = Node(NODE_UNLET)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_lvaluelist()
        self.add_node(node)

    def parse_cmd_lockvar(self):
        node = Node(NODE_LOCKVAR)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.depth = NIL
        node.list = []
        self.reader.skip_white()
        if isdigit(self.reader.peekn(1)):
            node.depth = viml_str2nr(self.reader.read_digit(), 10)
        node.list = self.parse_lvaluelist()
        self.add_node(node)

    def parse_cmd_unlockvar(self):
        node = Node(NODE_UNLOCKVAR)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.depth = NIL
        node.list = []
        self.reader.skip_white()
        if isdigit(self.reader.peekn(1)):
            node.depth = viml_str2nr(self.reader.read_digit(), 10)
        node.list = self.parse_lvaluelist()
        self.add_node(node)

    def parse_cmd_if(self):
        node = Node(NODE_IF)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.cond = self.parse_expr()
        node.elseif = []
        node.else_ = NIL
        node.endif = NIL
        self.add_node(node)
        self.push_context(node)

    def parse_cmd_elseif(self):
        if self.context[0].type != NODE_IF and self.context[0].type != NODE_ELSEIF:
            raise VimLParserException(Err("E582: :elseif without :if", self.ea.cmdpos))
        if self.context[0].type != NODE_IF:
            self.pop_context()
        node = Node(NODE_ELSEIF)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.cond = self.parse_expr()
        viml_add(self.context[0].elseif, node)
        self.push_context(node)

    def parse_cmd_else(self):
        if self.context[0].type != NODE_IF and self.context[0].type != NODE_ELSEIF:
            raise VimLParserException(Err("E581: :else without :if", self.ea.cmdpos))
        if self.context[0].type != NODE_IF:
            self.pop_context()
        node = Node(NODE_ELSE)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        self.context[0].else_ = node
        self.push_context(node)

    def parse_cmd_endif(self):
        if self.context[0].type != NODE_IF and self.context[0].type != NODE_ELSEIF and self.context[0].type != NODE_ELSE:
            raise VimLParserException(Err("E580: :endif without :if", self.ea.cmdpos))
        if self.context[0].type != NODE_IF:
            self.pop_context()
        node = Node(NODE_ENDIF)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.context[0].endif = node
        self.pop_context()

    def parse_cmd_while(self):
        node = Node(NODE_WHILE)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.cond = self.parse_expr()
        node.endwhile = NIL
        self.add_node(node)
        self.push_context(node)

    def parse_cmd_endwhile(self):
        if self.context[0].type != NODE_WHILE:
            raise VimLParserException(Err("E588: :endwhile without :while", self.ea.cmdpos))
        node = Node(NODE_ENDWHILE)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.context[0].endwhile = node
        self.pop_context()

    def parse_cmd_for(self):
        node = Node(NODE_FOR)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.left = NIL
        node.right = NIL
        node.endfor = NIL
        lhs = self.parse_letlhs()
        node.left = lhs.left
        node.list = lhs.list
        node.rest = lhs.rest
        self.reader.skip_white()
        epos = self.reader.getpos()
        if self.reader.read_alpha() != "in":
            raise VimLParserException(Err("Missing \"in\" after :for", epos))
        node.right = self.parse_expr()
        self.add_node(node)
        self.push_context(node)

    def parse_cmd_endfor(self):
        if self.context[0].type != NODE_FOR:
            raise VimLParserException(Err("E588: :endfor without :for", self.ea.cmdpos))
        node = Node(NODE_ENDFOR)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.context[0].endfor = node
        self.pop_context()

    def parse_cmd_continue(self):
        if self.find_context(NODE_WHILE) == -1 and self.find_context(NODE_FOR) == -1:
            raise VimLParserException(Err("E586: :continue without :while or :for", self.ea.cmdpos))
        node = Node(NODE_CONTINUE)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.add_node(node)

    def parse_cmd_break(self):
        if self.find_context(NODE_WHILE) == -1 and self.find_context(NODE_FOR) == -1:
            raise VimLParserException(Err("E587: :break without :while or :for", self.ea.cmdpos))
        node = Node(NODE_BREAK)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.add_node(node)

    def parse_cmd_try(self):
        node = Node(NODE_TRY)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.catch = []
        node.finally_ = NIL
        node.endtry = NIL
        self.add_node(node)
        self.push_context(node)

    def parse_cmd_catch(self):
        if self.context[0].type == NODE_FINALLY:
            raise VimLParserException(Err("E604: :catch after :finally", self.ea.cmdpos))
        elif self.context[0].type != NODE_TRY and self.context[0].type != NODE_CATCH:
            raise VimLParserException(Err("E603: :catch without :try", self.ea.cmdpos))
        if self.context[0].type != NODE_TRY:
            self.pop_context()
        node = Node(NODE_CATCH)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        node.pattern = NIL
        self.reader.skip_white()
        if not self.ends_excmds(self.reader.peek()):
            node.pattern, _ = self.parse_pattern(self.reader.get())
        viml_add(self.context[0].catch, node)
        self.push_context(node)

    def parse_cmd_finally(self):
        if self.context[0].type != NODE_TRY and self.context[0].type != NODE_CATCH:
            raise VimLParserException(Err("E606: :finally without :try", self.ea.cmdpos))
        if self.context[0].type != NODE_TRY:
            self.pop_context()
        node = Node(NODE_FINALLY)
        node.pos = self.ea.cmdpos
        node.body = []
        node.ea = self.ea
        self.context[0].finally_ = node
        self.push_context(node)

    def parse_cmd_endtry(self):
        if self.context[0].type != NODE_TRY and self.context[0].type != NODE_CATCH and self.context[0].type != NODE_FINALLY:
            raise VimLParserException(Err("E602: :endtry without :try", self.ea.cmdpos))
        if self.context[0].type != NODE_TRY:
            self.pop_context()
        node = Node(NODE_ENDTRY)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        self.context[0].endtry = node
        self.pop_context()

    def parse_cmd_throw(self):
        node = Node(NODE_THROW)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.left = self.parse_expr()
        self.add_node(node)

    def parse_cmd_eval(self):
        node = Node(NODE_EVAL)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.left = self.parse_expr()
        self.add_node(node)

    def parse_cmd_echo(self):
        node = Node(NODE_ECHO)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_exprlist()
        self.add_node(node)

    def parse_cmd_echon(self):
        node = Node(NODE_ECHON)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_exprlist()
        self.add_node(node)

    def parse_cmd_echohl(self):
        node = Node(NODE_ECHOHL)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = ""
        while not self.ends_excmds(self.reader.peek()):
            node.str += self.reader.get()
        self.add_node(node)

    def parse_cmd_echomsg(self):
        node = Node(NODE_ECHOMSG)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_exprlist()
        self.add_node(node)

    def parse_cmd_echoerr(self):
        node = Node(NODE_ECHOERR)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_exprlist()
        self.add_node(node)

    def parse_cmd_execute(self):
        node = Node(NODE_EXECUTE)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.list = self.parse_exprlist()
        self.add_node(node)

    def parse_expr(self):
        return ExprParser(self.reader).parse()

    def parse_exprlist(self):
        list = []
        while TRUE:
            self.reader.skip_white()
            c = self.reader.peek()
            if c != "\"" and self.ends_excmds(c):
                break
            node = self.parse_expr()
            viml_add(list, node)
        return list

    def parse_lvalue_func(self):
        p = LvalueParser(self.reader)
        node = p.parse()
        if node.type == NODE_IDENTIFIER or node.type == NODE_CURLYNAME or node.type == NODE_SUBSCRIPT or node.type == NODE_DOT or node.type == NODE_OPTION or node.type == NODE_ENV or node.type == NODE_REG:
            return node
        raise VimLParserException(Err("Invalid Expression", node.pos))

    # FIXME:
    def parse_lvalue(self):
        p = LvalueParser(self.reader)
        node = p.parse()
        if node.type == NODE_IDENTIFIER:
            if not isvarname(node.value):
                raise VimLParserException(Err(viml_printf("E461: Illegal variable name: %s", node.value), node.pos))
        if node.type == NODE_IDENTIFIER or node.type == NODE_CURLYNAME or node.type == NODE_SUBSCRIPT or node.type == NODE_SLICE or node.type == NODE_DOT or node.type == NODE_OPTION or node.type == NODE_ENV or node.type == NODE_REG:
            return node
        raise VimLParserException(Err("Invalid Expression", node.pos))

    # TODO: merge with s:VimLParser.parse_lvalue()
    def parse_constlvalue(self):
        p = LvalueParser(self.reader)
        node = p.parse()
        if node.type == NODE_IDENTIFIER:
            if not isvarname(node.value):
                raise VimLParserException(Err(viml_printf("E461: Illegal variable name: %s", node.value), node.pos))
        if node.type == NODE_IDENTIFIER or node.type == NODE_CURLYNAME:
            return node
        elif node.type == NODE_SUBSCRIPT or node.type == NODE_SLICE or node.type == NODE_DOT:
            raise VimLParserException(Err("E996: Cannot lock a list or dict", node.pos))
        elif node.type == NODE_OPTION:
            raise VimLParserException(Err("E996: Cannot lock an option", node.pos))
        elif node.type == NODE_ENV:
            raise VimLParserException(Err("E996: Cannot lock an environment variable", node.pos))
        elif node.type == NODE_REG:
            raise VimLParserException(Err("E996: Cannot lock a register", node.pos))
        raise VimLParserException(Err("Invalid Expression", node.pos))

    def parse_lvaluelist(self):
        list = []
        node = self.parse_expr()
        viml_add(list, node)
        while TRUE:
            self.reader.skip_white()
            if self.ends_excmds(self.reader.peek()):
                break
            node = self.parse_lvalue()
            viml_add(list, node)
        return list

    # FIXME:
    def parse_letlhs(self):
        lhs = AttributeDict({"left": NIL, "list": NIL, "rest": NIL})
        tokenizer = ExprTokenizer(self.reader)
        if tokenizer.peek().type == TOKEN_SQOPEN:
            tokenizer.get()
            lhs.list = []
            while TRUE:
                node = self.parse_lvalue()
                viml_add(lhs.list, node)
                token = tokenizer.get()
                if token.type == TOKEN_SQCLOSE:
                    break
                elif token.type == TOKEN_COMMA:
                    continue
                elif token.type == TOKEN_SEMICOLON:
                    node = self.parse_lvalue()
                    lhs.rest = node
                    token = tokenizer.get()
                    if token.type == TOKEN_SQCLOSE:
                        break
                    else:
                        raise VimLParserException(Err(viml_printf("E475 Invalid argument: %s", token.value), token.pos))
                else:
                    raise VimLParserException(Err(viml_printf("E475 Invalid argument: %s", token.value), token.pos))
        else:
            lhs.left = self.parse_lvalue()
        return lhs

    # TODO: merge with s:VimLParser.parse_letlhs() ?
    def parse_constlhs(self):
        lhs = AttributeDict({"left": NIL, "list": NIL, "rest": NIL})
        tokenizer = ExprTokenizer(self.reader)
        if tokenizer.peek().type == TOKEN_SQOPEN:
            tokenizer.get()
            lhs.list = []
            while TRUE:
                node = self.parse_lvalue()
                viml_add(lhs.list, node)
                token = tokenizer.get()
                if token.type == TOKEN_SQCLOSE:
                    break
                elif token.type == TOKEN_COMMA:
                    continue
                elif token.type == TOKEN_SEMICOLON:
                    node = self.parse_lvalue()
                    lhs.rest = node
                    token = tokenizer.get()
                    if token.type == TOKEN_SQCLOSE:
                        break
                    else:
                        raise VimLParserException(Err(viml_printf("E475 Invalid argument: %s", token.value), token.pos))
                else:
                    raise VimLParserException(Err(viml_printf("E475 Invalid argument: %s", token.value), token.pos))
        else:
            lhs.left = self.parse_constlvalue()
        return lhs

    def ends_excmds(self, c):
        return c == "" or c == "|" or c == "\"" or c == "<EOF>" or c == "<EOL>"

    # FIXME: validate argument
    def parse_wincmd(self):
        c = self.reader.getn(1)
        if c == "":
            raise VimLParserException(Err("E471: Argument required", self.reader.getpos()))
        elif c == "g" or c == "\x07":
            # <C-G>
            c2 = self.reader.getn(1)
            if c2 == "" or iswhite(c2):
                raise VimLParserException(Err("E474: Invalid Argument", self.reader.getpos()))
        end = self.reader.getpos()
        self.reader.skip_white()
        if not self.ends_excmds(self.reader.peek()):
            raise VimLParserException(Err("E474: Invalid Argument", self.reader.getpos()))
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = self.reader.getstr(self.ea.linepos, end)
        self.add_node(node)

    # FIXME: validate argument
    def parse_cmd_syntax(self):
        end = self.reader.getpos()
        while TRUE:
            end = self.reader.getpos()
            c = self.reader.peek()
            if c == "/" or c == "'" or c == "\"":
                self.reader.getn(1)
                self.parse_pattern(c)
            elif c == "=":
                self.reader.getn(1)
                self.parse_pattern(" ")
            elif self.ends_excmds(c):
                break
            self.reader.getn(1)
        node = Node(NODE_EXCMD)
        node.pos = self.ea.cmdpos
        node.ea = self.ea
        node.str = self.reader.getstr(self.ea.linepos, end)
        self.add_node(node)
    neovim_additional_commands = [AttributeDict({"name": "rshada", "minlen": 3, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "wshada", "minlen": 3, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"})]
    neovim_removed_commands = [AttributeDict({"name": "Print", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "fixdel", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "helpfind", "minlen": 5, "flags": "EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "open", "minlen": 1, "flags": "RANGE|BANG|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "shell", "minlen": 2, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tearoff", "minlen": 2, "flags": "NEEDARG|EXTRA|TRLBAR|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "gvim", "minlen": 2, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR|CMDWIN", "parser": "parse_cmd_common"})]
    # To find new builtin_commands, run the below script.
    # $ scripts/update_builtin_commands.sh /path/to/vim/src/ex_cmds.h
    builtin_commands = [AttributeDict({"name": "append", "minlen": 1, "flags": "BANG|RANGE|ZEROR|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_append"}), AttributeDict({"name": "abbreviate", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "abclear", "minlen": 3, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "aboveleft", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "all", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "amenu", "minlen": 2, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "anoremenu", "minlen": 2, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "args", "minlen": 2, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "argadd", "minlen": 4, "flags": "BANG|NEEDARG|RANGE|NOTADR|ZEROR|FILES|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "argdelete", "minlen": 4, "flags": "BANG|RANGE|NOTADR|FILES|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "argedit", "minlen": 4, "flags": "BANG|NEEDARG|RANGE|NOTADR|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "argdo", "minlen": 5, "flags": "BANG|NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "argglobal", "minlen": 4, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "arglocal", "minlen": 4, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "argument", "minlen": 4, "flags": "BANG|RANGE|NOTADR|COUNT|EXTRA|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ascii", "minlen": 2, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "autocmd", "minlen": 2, "flags": "BANG|EXTRA|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "augroup", "minlen": 3, "flags": "BANG|WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "aunmenu", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "buffer", "minlen": 1, "flags": "BANG|RANGE|NOTADR|BUFNAME|BUFUNL|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "bNext", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ball", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "badd", "minlen": 3, "flags": "NEEDARG|FILE1|EDITCMD|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "bdelete", "minlen": 2, "flags": "BANG|RANGE|NOTADR|BUFNAME|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "behave", "minlen": 2, "flags": "NEEDARG|WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "belowright", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "bfirst", "minlen": 2, "flags": "BANG|RANGE|NOTADR|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "blast", "minlen": 2, "flags": "BANG|RANGE|NOTADR|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "bmodified", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "bnext", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "botright", "minlen": 2, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "bprevious", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "brewind", "minlen": 2, "flags": "BANG|RANGE|NOTADR|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "break", "minlen": 4, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_break"}), AttributeDict({"name": "breakadd", "minlen": 6, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "breakdel", "minlen": 6, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "breaklist", "minlen": 6, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "browse", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "bufdo", "minlen": 5, "flags": "BANG|NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "buffers", "minlen": 7, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "bunload", "minlen": 3, "flags": "BANG|RANGE|NOTADR|BUFNAME|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "bwipeout", "minlen": 2, "flags": "BANG|RANGE|NOTADR|BUFNAME|BUFUNL|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "change", "minlen": 1, "flags": "BANG|WHOLEFOLD|RANGE|COUNT|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "cNext", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cNfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cabbrev", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cabclear", "minlen": 4, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "caddbuffer", "minlen": 3, "flags": "RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "caddexpr", "minlen": 5, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "caddfile", "minlen": 5, "flags": "TRLBAR|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "call", "minlen": 3, "flags": "RANGE|NEEDARG|EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_call"}), AttributeDict({"name": "catch", "minlen": 3, "flags": "EXTRA|SBOXOK|CMDWIN", "parser": "parse_cmd_catch"}), AttributeDict({"name": "cbuffer", "minlen": 2, "flags": "BANG|RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cc", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cclose", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cd", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "center", "minlen": 2, "flags": "TRLBAR|RANGE|WHOLEFOLD|EXTRA|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "cexpr", "minlen": 3, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cfile", "minlen": 2, "flags": "TRLBAR|FILE1|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cfirst", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cgetbuffer", "minlen": 5, "flags": "RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cgetexpr", "minlen": 5, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cgetfile", "minlen": 2, "flags": "TRLBAR|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "changes", "minlen": 7, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "chdir", "minlen": 3, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "checkpath", "minlen": 3, "flags": "TRLBAR|BANG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "checktime", "minlen": 6, "flags": "RANGE|NOTADR|BUFNAME|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "clist", "minlen": 2, "flags": "BANG|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "clast", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "close", "minlen": 3, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cmapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cmenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnext", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnewer", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnoremap", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnoreabbrev", "minlen": 6, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cnoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "copy", "minlen": 2, "flags": "RANGE|WHOLEFOLD|EXTRA|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "colder", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "colorscheme", "minlen": 4, "flags": "WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "command", "minlen": 3, "flags": "EXTRA|BANG|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "comclear", "minlen": 4, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "compiler", "minlen": 4, "flags": "BANG|TRLBAR|WORD1|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "continue", "minlen": 3, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_continue"}), AttributeDict({"name": "confirm", "minlen": 4, "flags": "NEEDARG|EXTRA|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "copen", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "cprevious", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cpfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cquit", "minlen": 2, "flags": "TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "crewind", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "cscope", "minlen": 2, "flags": "EXTRA|NOTRLCOM|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "cstag", "minlen": 3, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "cunmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cunabbrev", "minlen": 4, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "cwindow", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "delete", "minlen": 1, "flags": "RANGE|WHOLEFOLD|REGSTR|COUNT|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "delmarks", "minlen": 4, "flags": "BANG|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "debug", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "debuggreedy", "minlen": 6, "flags": "RANGE|NOTADR|ZEROR|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "delcommand", "minlen": 4, "flags": "NEEDARG|WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "delfunction", "minlen": 4, "flags": "BANG|NEEDARG|WORD1|CMDWIN", "parser": "parse_cmd_delfunction"}), AttributeDict({"name": "diffupdate", "minlen": 3, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffget", "minlen": 5, "flags": "RANGE|EXTRA|TRLBAR|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffoff", "minlen": 5, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffpatch", "minlen": 5, "flags": "EXTRA|FILE1|TRLBAR|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffput", "minlen": 6, "flags": "RANGE|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffsplit", "minlen": 5, "flags": "EXTRA|FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "diffthis", "minlen": 5, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "digraphs", "minlen": 3, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "display", "minlen": 2, "flags": "EXTRA|NOTRLCOM|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "djump", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "dlist", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "doautocmd", "minlen": 2, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "doautoall", "minlen": 7, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "drop", "minlen": 2, "flags": "FILES|EDITCMD|NEEDARG|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "dsearch", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "dsplit", "minlen": 3, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "edit", "minlen": 1, "flags": "BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "earlier", "minlen": 2, "flags": "TRLBAR|EXTRA|NOSPC|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "echo", "minlen": 2, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_echo"}), AttributeDict({"name": "echoerr", "minlen": 5, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_echoerr"}), AttributeDict({"name": "echohl", "minlen": 5, "flags": "EXTRA|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_echohl"}), AttributeDict({"name": "echomsg", "minlen": 5, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_echomsg"}), AttributeDict({"name": "echon", "minlen": 5, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_echon"}), AttributeDict({"name": "else", "minlen": 2, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_else"}), AttributeDict({"name": "elseif", "minlen": 5, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_elseif"}), AttributeDict({"name": "emenu", "minlen": 2, "flags": "NEEDARG|EXTRA|TRLBAR|NOTRLCOM|RANGE|NOTADR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "endif", "minlen": 2, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_endif"}), AttributeDict({"name": "endfor", "minlen": 5, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_endfor"}), AttributeDict({"name": "endfunction", "minlen": 4, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_endfunction"}), AttributeDict({"name": "endtry", "minlen": 4, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_endtry"}), AttributeDict({"name": "endwhile", "minlen": 4, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_endwhile"}), AttributeDict({"name": "enew", "minlen": 3, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "eval", "minlen": 2, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_eval"}), AttributeDict({"name": "ex", "minlen": 2, "flags": "BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "execute", "minlen": 3, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_execute"}), AttributeDict({"name": "exit", "minlen": 3, "flags": "RANGE|WHOLEFOLD|BANG|FILE1|ARGOPT|DFLALL|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "exusage", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "file", "minlen": 1, "flags": "RANGE|NOTADR|ZEROR|BANG|FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "files", "minlen": 5, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "filetype", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "find", "minlen": 3, "flags": "RANGE|NOTADR|BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "finally", "minlen": 4, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_finally"}), AttributeDict({"name": "finish", "minlen": 4, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_finish"}), AttributeDict({"name": "first", "minlen": 3, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "fixdel", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "fold", "minlen": 2, "flags": "RANGE|WHOLEFOLD|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "foldclose", "minlen": 5, "flags": "RANGE|BANG|WHOLEFOLD|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "folddoopen", "minlen": 5, "flags": "RANGE|DFLALL|NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "folddoclosed", "minlen": 7, "flags": "RANGE|DFLALL|NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "foldopen", "minlen": 5, "flags": "RANGE|BANG|WHOLEFOLD|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "for", "minlen": 3, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_for"}), AttributeDict({"name": "function", "minlen": 2, "flags": "EXTRA|BANG|CMDWIN", "parser": "parse_cmd_function"}), AttributeDict({"name": "global", "minlen": 1, "flags": "RANGE|WHOLEFOLD|BANG|EXTRA|DFLALL|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "goto", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "grep", "minlen": 2, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "grepadd", "minlen": 5, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "gui", "minlen": 2, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "gvim", "minlen": 2, "flags": "BANG|FILES|EDITCMD|ARGOPT|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "hardcopy", "minlen": 2, "flags": "RANGE|COUNT|EXTRA|TRLBAR|DFLALL|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "help", "minlen": 1, "flags": "BANG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "helpfind", "minlen": 5, "flags": "EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "helpgrep", "minlen": 5, "flags": "EXTRA|NOTRLCOM|NEEDARG", "parser": "parse_cmd_common"}), AttributeDict({"name": "helptags", "minlen": 5, "flags": "NEEDARG|FILES|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "highlight", "minlen": 2, "flags": "BANG|EXTRA|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "hide", "minlen": 3, "flags": "BANG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "history", "minlen": 3, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "insert", "minlen": 1, "flags": "BANG|RANGE|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_insert"}), AttributeDict({"name": "iabbrev", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "iabclear", "minlen": 4, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "if", "minlen": 2, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_if"}), AttributeDict({"name": "ijump", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "ilist", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "imap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "imapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "imenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "inoremap", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "inoreabbrev", "minlen": 6, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "inoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "intro", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "isearch", "minlen": 2, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "isplit", "minlen": 3, "flags": "BANG|RANGE|DFLALL|WHOLEFOLD|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "iunmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "iunabbrev", "minlen": 4, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "iunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "join", "minlen": 1, "flags": "BANG|RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "jumps", "minlen": 2, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "k", "minlen": 1, "flags": "RANGE|WORD1|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "keepalt", "minlen": 5, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "keepmarks", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "keepjumps", "minlen": 5, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "keeppatterns", "minlen": 5, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "lNext", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lNfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "list", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "laddexpr", "minlen": 3, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "laddbuffer", "minlen": 5, "flags": "RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "laddfile", "minlen": 5, "flags": "TRLBAR|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "last", "minlen": 2, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "language", "minlen": 3, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "later", "minlen": 3, "flags": "TRLBAR|EXTRA|NOSPC|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lbuffer", "minlen": 2, "flags": "BANG|RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lcd", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lchdir", "minlen": 3, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lclose", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lcscope", "minlen": 3, "flags": "EXTRA|NOTRLCOM|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "left", "minlen": 2, "flags": "TRLBAR|RANGE|WHOLEFOLD|EXTRA|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "leftabove", "minlen": 5, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "let", "minlen": 3, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_let"}), AttributeDict({"name": "const", "minlen": 4, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_const"}), AttributeDict({"name": "lexpr", "minlen": 3, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lfile", "minlen": 2, "flags": "TRLBAR|FILE1|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lfirst", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lgetbuffer", "minlen": 5, "flags": "RANGE|NOTADR|WORD1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lgetexpr", "minlen": 5, "flags": "NEEDARG|WORD1|NOTRLCOM|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lgetfile", "minlen": 2, "flags": "TRLBAR|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "lgrep", "minlen": 3, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "lgrepadd", "minlen": 6, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "lhelpgrep", "minlen": 2, "flags": "EXTRA|NOTRLCOM|NEEDARG", "parser": "parse_cmd_common"}), AttributeDict({"name": "ll", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "llast", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "list", "minlen": 3, "flags": "BANG|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lmake", "minlen": 4, "flags": "BANG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "lmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lmapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lnext", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lnewer", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lnfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lnoremap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "loadkeymap", "minlen": 5, "flags": "CMDWIN", "parser": "parse_cmd_loadkeymap"}), AttributeDict({"name": "loadview", "minlen": 2, "flags": "FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lockmarks", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "lockvar", "minlen": 5, "flags": "BANG|EXTRA|NEEDARG|SBOXOK|CMDWIN", "parser": "parse_cmd_lockvar"}), AttributeDict({"name": "lolder", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lopen", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "lprevious", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lpfile", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "lrewind", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR|BANG", "parser": "parse_cmd_common"}), AttributeDict({"name": "ls", "minlen": 2, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "ltag", "minlen": 2, "flags": "NOTADR|TRLBAR|BANG|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "lunmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lua", "minlen": 3, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_lua"}), AttributeDict({"name": "luado", "minlen": 4, "flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "luafile", "minlen": 4, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "lvimgrep", "minlen": 2, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "lvimgrepadd", "minlen": 9, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "lwindow", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "move", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "mark", "minlen": 2, "flags": "RANGE|WORD1|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "make", "minlen": 3, "flags": "BANG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "map", "minlen": 3, "flags": "BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "mapclear", "minlen": 4, "flags": "EXTRA|BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "marks", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "match", "minlen": 3, "flags": "RANGE|NOTADR|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "menu", "minlen": 2, "flags": "RANGE|NOTADR|ZEROR|BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "menutranslate", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "messages", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "mkexrc", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "mksession", "minlen": 3, "flags": "BANG|FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "mkspell", "minlen": 4, "flags": "BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "mkvimrc", "minlen": 3, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "mkview", "minlen": 5, "flags": "BANG|FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "mode", "minlen": 3, "flags": "WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "mzscheme", "minlen": 2, "flags": "RANGE|EXTRA|DFLALL|NEEDARG|CMDWIN|SBOXOK", "parser": "parse_cmd_mzscheme"}), AttributeDict({"name": "mzfile", "minlen": 3, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nbclose", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nbkey", "minlen": 2, "flags": "EXTRA|NOTADR|NEEDARG", "parser": "parse_cmd_common"}), AttributeDict({"name": "nbstart", "minlen": 3, "flags": "WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "next", "minlen": 1, "flags": "RANGE|NOTADR|BANG|FILES|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "new", "minlen": 3, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "nmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nmapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nmenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nnoremap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nnoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "noautocmd", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "noremap", "minlen": 2, "flags": "BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nohlsearch", "minlen": 3, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "noreabbrev", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "noremenu", "minlen": 6, "flags": "RANGE|NOTADR|ZEROR|BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "normal", "minlen": 4, "flags": "RANGE|BANG|EXTRA|NEEDARG|NOTRLCOM|USECTRLV|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "number", "minlen": 2, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nunmap", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "nunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "oldfiles", "minlen": 2, "flags": "BANG|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "open", "minlen": 1, "flags": "RANGE|BANG|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "omap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "omapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "omenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "only", "minlen": 2, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "onoremap", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "onoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "options", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ounmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "ounmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "ownsyntax", "minlen": 2, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "pclose", "minlen": 2, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "pedit", "minlen": 3, "flags": "BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "perl", "minlen": 2, "flags": "RANGE|EXTRA|DFLALL|NEEDARG|SBOXOK|CMDWIN", "parser": "parse_cmd_perl"}), AttributeDict({"name": "print", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN|SBOXOK", "parser": "parse_cmd_common"}), AttributeDict({"name": "profdel", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "profile", "minlen": 4, "flags": "BANG|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "promptfind", "minlen": 3, "flags": "EXTRA|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "promptrepl", "minlen": 7, "flags": "EXTRA|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "perldo", "minlen": 5, "flags": "RANGE|EXTRA|DFLALL|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "pop", "minlen": 2, "flags": "RANGE|NOTADR|BANG|COUNT|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "popup", "minlen": 4, "flags": "NEEDARG|EXTRA|BANG|TRLBAR|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "ppop", "minlen": 2, "flags": "RANGE|NOTADR|BANG|COUNT|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "preserve", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "previous", "minlen": 4, "flags": "EXTRA|RANGE|NOTADR|COUNT|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "psearch", "minlen": 2, "flags": "BANG|RANGE|WHOLEFOLD|DFLALL|EXTRA", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptag", "minlen": 2, "flags": "RANGE|NOTADR|BANG|WORD1|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptNext", "minlen": 3, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptfirst", "minlen": 3, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptjump", "minlen": 3, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptlast", "minlen": 3, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptnext", "minlen": 3, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptprevious", "minlen": 3, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptrewind", "minlen": 3, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "ptselect", "minlen": 3, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "put", "minlen": 2, "flags": "RANGE|WHOLEFOLD|BANG|REGSTR|TRLBAR|ZEROR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "pwd", "minlen": 2, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "py3", "minlen": 3, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_python3"}), AttributeDict({"name": "python3", "minlen": 7, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_python3"}), AttributeDict({"name": "py3file", "minlen": 4, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "python", "minlen": 2, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_python"}), AttributeDict({"name": "pyfile", "minlen": 3, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "pydo", "minlen": 3, "flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "py3do", "minlen": 4, "flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "quit", "minlen": 1, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "quitall", "minlen": 5, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "qall", "minlen": 2, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "read", "minlen": 1, "flags": "BANG|RANGE|WHOLEFOLD|FILE1|ARGOPT|TRLBAR|ZEROR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "recover", "minlen": 3, "flags": "BANG|FILE1|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "redo", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "redir", "minlen": 4, "flags": "BANG|FILES|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "redraw", "minlen": 4, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "redrawstatus", "minlen": 7, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "registers", "minlen": 3, "flags": "EXTRA|NOTRLCOM|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "resize", "minlen": 3, "flags": "RANGE|NOTADR|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "retab", "minlen": 3, "flags": "TRLBAR|RANGE|WHOLEFOLD|DFLALL|BANG|WORD1|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "return", "minlen": 4, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_return"}), AttributeDict({"name": "rewind", "minlen": 3, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "right", "minlen": 2, "flags": "TRLBAR|RANGE|WHOLEFOLD|EXTRA|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "rightbelow", "minlen": 6, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "ruby", "minlen": 3, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_ruby"}), AttributeDict({"name": "rubydo", "minlen": 5, "flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "rubyfile", "minlen": 5, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "rundo", "minlen": 4, "flags": "NEEDARG|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "runtime", "minlen": 2, "flags": "BANG|NEEDARG|FILES|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "rviminfo", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "substitute", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sNext", "minlen": 2, "flags": "EXTRA|RANGE|NOTADR|COUNT|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sandbox", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "sargument", "minlen": 2, "flags": "BANG|RANGE|NOTADR|COUNT|EXTRA|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sall", "minlen": 3, "flags": "BANG|RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "saveas", "minlen": 3, "flags": "BANG|DFLALL|FILE1|ARGOPT|CMDWIN|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbuffer", "minlen": 2, "flags": "BANG|RANGE|NOTADR|BUFNAME|BUFUNL|COUNT|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbNext", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sball", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbfirst", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sblast", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbmodified", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbnext", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbprevious", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sbrewind", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "scriptnames", "minlen": 3, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "scriptencoding", "minlen": 7, "flags": "WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "scscope", "minlen": 3, "flags": "EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "set", "minlen": 2, "flags": "TRLBAR|EXTRA|CMDWIN|SBOXOK", "parser": "parse_cmd_common"}), AttributeDict({"name": "setfiletype", "minlen": 4, "flags": "TRLBAR|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "setglobal", "minlen": 4, "flags": "TRLBAR|EXTRA|CMDWIN|SBOXOK", "parser": "parse_cmd_common"}), AttributeDict({"name": "setlocal", "minlen": 4, "flags": "TRLBAR|EXTRA|CMDWIN|SBOXOK", "parser": "parse_cmd_common"}), AttributeDict({"name": "sfind", "minlen": 2, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sfirst", "minlen": 4, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "shell", "minlen": 2, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "simalt", "minlen": 3, "flags": "NEEDARG|WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sign", "minlen": 3, "flags": "NEEDARG|RANGE|NOTADR|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "silent", "minlen": 3, "flags": "NEEDARG|EXTRA|BANG|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sleep", "minlen": 2, "flags": "RANGE|NOTADR|COUNT|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "slast", "minlen": 3, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "smagic", "minlen": 2, "flags": "RANGE|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "smap", "minlen": 4, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "smapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "smenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "snext", "minlen": 2, "flags": "RANGE|NOTADR|BANG|FILES|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sniff", "minlen": 3, "flags": "EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "snomagic", "minlen": 3, "flags": "RANGE|WHOLEFOLD|EXTRA|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "snoremap", "minlen": 4, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "snoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sort", "minlen": 3, "flags": "RANGE|DFLALL|WHOLEFOLD|BANG|EXTRA|NOTRLCOM|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "source", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "spelldump", "minlen": 6, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "spellgood", "minlen": 3, "flags": "BANG|RANGE|NOTADR|NEEDARG|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "spellinfo", "minlen": 6, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "spellrepall", "minlen": 6, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "spellundo", "minlen": 6, "flags": "BANG|RANGE|NOTADR|NEEDARG|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "spellwrong", "minlen": 6, "flags": "BANG|RANGE|NOTADR|NEEDARG|EXTRA|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "split", "minlen": 2, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sprevious", "minlen": 3, "flags": "EXTRA|RANGE|NOTADR|COUNT|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "srewind", "minlen": 3, "flags": "EXTRA|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "stop", "minlen": 2, "flags": "TRLBAR|BANG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "stag", "minlen": 3, "flags": "RANGE|NOTADR|BANG|WORD1|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "startinsert", "minlen": 4, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "startgreplace", "minlen": 6, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "startreplace", "minlen": 6, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "stopinsert", "minlen": 5, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "stjump", "minlen": 3, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "stselect", "minlen": 3, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "sunhide", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "sunmap", "minlen": 4, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "suspend", "minlen": 3, "flags": "TRLBAR|BANG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "sview", "minlen": 2, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "swapname", "minlen": 2, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "syntax", "minlen": 2, "flags": "EXTRA|NOTRLCOM|CMDWIN", "parser": "parse_cmd_syntax"}), AttributeDict({"name": "syntime", "minlen": 5, "flags": "NEEDARG|WORD1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "syncbind", "minlen": 4, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "t", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "tNext", "minlen": 2, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabNext", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabclose", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabdo", "minlen": 4, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabedit", "minlen": 4, "flags": "BANG|FILE1|RANGE|NOTADR|ZEROR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabfind", "minlen": 4, "flags": "BANG|FILE1|RANGE|NOTADR|ZEROR|EDITCMD|ARGOPT|NEEDARG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabfirst", "minlen": 6, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tablast", "minlen": 4, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabmove", "minlen": 4, "flags": "RANGE|NOTADR|ZEROR|EXTRA|NOSPC|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabnew", "minlen": 6, "flags": "BANG|FILE1|RANGE|NOTADR|ZEROR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabnext", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabonly", "minlen": 4, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabprevious", "minlen": 4, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabrewind", "minlen": 4, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tabs", "minlen": 4, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tab", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "tag", "minlen": 2, "flags": "RANGE|NOTADR|BANG|WORD1|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tags", "minlen": 4, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tcl", "minlen": 2, "flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_tcl"}), AttributeDict({"name": "tcldo", "minlen": 4, "flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tclfile", "minlen": 4, "flags": "RANGE|FILE1|NEEDARG|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tearoff", "minlen": 2, "flags": "NEEDARG|EXTRA|TRLBAR|NOTRLCOM|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tfirst", "minlen": 2, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "throw", "minlen": 2, "flags": "EXTRA|NEEDARG|SBOXOK|CMDWIN", "parser": "parse_cmd_throw"}), AttributeDict({"name": "tjump", "minlen": 2, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "tlast", "minlen": 2, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "tmenu", "minlen": 2, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "tnext", "minlen": 2, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "topleft", "minlen": 2, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "tprevious", "minlen": 2, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "trewind", "minlen": 2, "flags": "RANGE|NOTADR|BANG|TRLBAR|ZEROR", "parser": "parse_cmd_common"}), AttributeDict({"name": "try", "minlen": 3, "flags": "TRLBAR|SBOXOK|CMDWIN", "parser": "parse_cmd_try"}), AttributeDict({"name": "tselect", "minlen": 2, "flags": "BANG|TRLBAR|WORD1", "parser": "parse_cmd_common"}), AttributeDict({"name": "tunmenu", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "undo", "minlen": 1, "flags": "RANGE|NOTADR|COUNT|ZEROR|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "undojoin", "minlen": 5, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "undolist", "minlen": 5, "flags": "TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "unabbreviate", "minlen": 3, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "unhide", "minlen": 3, "flags": "RANGE|NOTADR|COUNT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "unlet", "minlen": 3, "flags": "BANG|EXTRA|NEEDARG|SBOXOK|CMDWIN", "parser": "parse_cmd_unlet"}), AttributeDict({"name": "unlockvar", "minlen": 4, "flags": "BANG|EXTRA|NEEDARG|SBOXOK|CMDWIN", "parser": "parse_cmd_unlockvar"}), AttributeDict({"name": "unmap", "minlen": 3, "flags": "BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "unmenu", "minlen": 4, "flags": "BANG|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "unsilent", "minlen": 3, "flags": "NEEDARG|EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "update", "minlen": 2, "flags": "RANGE|WHOLEFOLD|BANG|FILE1|ARGOPT|DFLALL|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "vglobal", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|DFLALL|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "version", "minlen": 2, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "verbose", "minlen": 4, "flags": "NEEDARG|RANGE|NOTADR|EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vertical", "minlen": 4, "flags": "NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "vimgrep", "minlen": 3, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "vimgrepadd", "minlen": 8, "flags": "RANGE|NOTADR|BANG|NEEDARG|EXTRA|NOTRLCOM|TRLBAR|XFILE", "parser": "parse_cmd_common"}), AttributeDict({"name": "visual", "minlen": 2, "flags": "BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "viusage", "minlen": 3, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "view", "minlen": 3, "flags": "BANG|FILE1|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "vmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vmapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vmenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vnew", "minlen": 3, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "vnoremap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vnoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vsplit", "minlen": 2, "flags": "BANG|FILE1|RANGE|NOTADR|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "vunmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "vunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "windo", "minlen": 5, "flags": "BANG|NEEDARG|EXTRA|NOTRLCOM", "parser": "parse_cmd_common"}), AttributeDict({"name": "write", "minlen": 1, "flags": "RANGE|WHOLEFOLD|BANG|FILE1|ARGOPT|DFLALL|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "wNext", "minlen": 2, "flags": "RANGE|WHOLEFOLD|NOTADR|BANG|FILE1|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wall", "minlen": 2, "flags": "BANG|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "while", "minlen": 2, "flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "parser": "parse_cmd_while"}), AttributeDict({"name": "winsize", "minlen": 2, "flags": "EXTRA|NEEDARG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wincmd", "minlen": 4, "flags": "NEEDARG|WORD1|RANGE|NOTADR", "parser": "parse_wincmd"}), AttributeDict({"name": "winpos", "minlen": 4, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "wnext", "minlen": 2, "flags": "RANGE|NOTADR|BANG|FILE1|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wprevious", "minlen": 2, "flags": "RANGE|NOTADR|BANG|FILE1|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wq", "minlen": 2, "flags": "RANGE|WHOLEFOLD|BANG|FILE1|ARGOPT|DFLALL|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wqall", "minlen": 3, "flags": "BANG|FILE1|ARGOPT|DFLALL|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "wsverb", "minlen": 2, "flags": "EXTRA|NOTADR|NEEDARG", "parser": "parse_cmd_common"}), AttributeDict({"name": "wundo", "minlen": 2, "flags": "BANG|NEEDARG|FILE1", "parser": "parse_cmd_common"}), AttributeDict({"name": "wviminfo", "minlen": 2, "flags": "BANG|FILE1|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xit", "minlen": 1, "flags": "RANGE|WHOLEFOLD|BANG|FILE1|ARGOPT|DFLALL|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xall", "minlen": 2, "flags": "BANG|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "xmapclear", "minlen": 5, "flags": "EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xmenu", "minlen": 3, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xnoremap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xnoremenu", "minlen": 7, "flags": "RANGE|NOTADR|ZEROR|EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xunmap", "minlen": 2, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "xunmenu", "minlen": 5, "flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "yank", "minlen": 1, "flags": "RANGE|WHOLEFOLD|REGSTR|COUNT|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "z", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "!", "minlen": 1, "flags": "RANGE|WHOLEFOLD|BANG|FILES|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "#", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "&", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "*", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "<", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "=", "minlen": 1, "flags": "RANGE|TRLBAR|DFLALL|EXFLAGS|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": ">", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"name": "@", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "Next", "minlen": 1, "flags": "EXTRA|RANGE|NOTADR|COUNT|BANG|EDITCMD|ARGOPT|TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "Print", "minlen": 1, "flags": "RANGE|WHOLEFOLD|COUNT|EXFLAGS|TRLBAR|CMDWIN", "parser": "parse_cmd_common"}), AttributeDict({"name": "X", "minlen": 1, "flags": "TRLBAR", "parser": "parse_cmd_common"}), AttributeDict({"name": "~", "minlen": 1, "flags": "RANGE|WHOLEFOLD|EXTRA|CMDWIN|MODIFY", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR", "minlen": 3, "name": "cbottom", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|NEEDARG|EXTRA|NOTRLCOM|RANGE|NOTADR|DFLALL", "minlen": 3, "name": "cdo", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|NEEDARG|EXTRA|NOTRLCOM|RANGE|NOTADR|DFLALL", "minlen": 3, "name": "cfdo", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR", "minlen": 3, "name": "chistory", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR|CMDWIN", "minlen": 3, "name": "clearjumps", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|NEEDARG|EXTRA|NOTRLCOM", "minlen": 4, "name": "filter", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|NOTADR|COUNT|TRLBAR", "minlen": 5, "name": "helpclose", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR", "minlen": 3, "name": "lbottom", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|NEEDARG|EXTRA|NOTRLCOM|RANGE|NOTADR|DFLALL", "minlen": 2, "name": "ldo", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|NEEDARG|EXTRA|NOTRLCOM|RANGE|NOTADR|DFLALL", "minlen": 3, "name": "lfdo", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR", "minlen": 3, "name": "lhistory", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|EXTRA|TRLBAR|CMDWIN", "minlen": 3, "name": "llist", "parser": "parse_cmd_common"}), AttributeDict({"flags": "NEEDARG|EXTRA|NOTRLCOM", "minlen": 3, "name": "noswapfile", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|FILE1|NEEDARG|TRLBAR|SBOXOK|CMDWIN", "minlen": 2, "name": "packadd", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|TRLBAR|SBOXOK|CMDWIN", "minlen": 5, "name": "packloadall", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR|CMDWIN|SBOXOK", "minlen": 3, "name": "smile", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "minlen": 3, "name": "pyx", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|DFLALL|EXTRA|NEEDARG|CMDWIN", "minlen": 4, "name": "pyxdo", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|EXTRA|NEEDARG|CMDWIN", "minlen": 7, "name": "pythonx", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|FILE1|NEEDARG|CMDWIN", "minlen": 4, "name": "pyxfile", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|BANG|FILES|CMDWIN", "minlen": 3, "name": "terminal", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "minlen": 3, "name": "tmap", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|TRLBAR|CMDWIN", "minlen": 5, "name": "tmapclear", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "minlen": 3, "name": "tnoremap", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|TRLBAR|NOTRLCOM|USECTRLV|CMDWIN", "minlen": 5, "name": "tunmap", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 4, "name": "cabove", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 3, "name": "cafter", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 3, "name": "cbefore", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 4, "name": "cbelow", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|NOTRLCOM|SBOXOK|CMDWIN", "minlen": 4, "name": "const", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 3, "name": "labove", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 3, "name": "lafter", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 3, "name": "lbefore", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|COUNT|TRLBAR", "minlen": 4, "name": "lbelow", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR|CMDWIN", "minlen": 7, "name": "redrawtabline", "parser": "parse_cmd_common"}), AttributeDict({"flags": "WORD1|TRLBAR|CMDWIN", "minlen": 7, "name": "scriptversion", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|FILE1|TRLBAR|CMDWIN", "minlen": 2, "name": "tcd", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|FILE1|TRLBAR|CMDWIN", "minlen": 3, "name": "tchdir", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|ZEROR|EXTRA|TRLBAR|NOTRLCOM|CTRLV|CMDWIN", "minlen": 3, "name": "tlmenu", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|ZEROR|EXTRA|TRLBAR|NOTRLCOM|CTRLV|CMDWIN", "minlen": 3, "name": "tlnoremenu", "parser": "parse_cmd_common"}), AttributeDict({"flags": "RANGE|ZEROR|EXTRA|TRLBAR|NOTRLCOM|CTRLV|CMDWIN", "minlen": 3, "name": "tlunmenu", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|TRLBAR|CMDWIN", "minlen": 2, "name": "xrestore", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|BANG|SBOXOK|CMDWIN", "minlen": 3, "name": "def", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|NEEDARG|TRLBAR|CMDWIN", "minlen": 4, "name": "disassemble", "parser": "parse_cmd_common"}), AttributeDict({"flags": "TRLBAR|CMDWIN", "minlen": 4, "name": "enddef", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|NOTRLCOM", "minlen": 3, "name": "export", "parser": "parse_cmd_common"}), AttributeDict({"flags": "EXTRA|NOTRLCOM", "minlen": 3, "name": "import", "parser": "parse_cmd_common"}), AttributeDict({"flags": "BANG|RANGE|NEEDARG|EXTRA|TRLBAR", "minlen": 7, "name": "spellrare", "parser": "parse_cmd_common"}), AttributeDict({"flags": "", "minlen": 4, "name": "vim9script", "parser": "parse_cmd_common"})]
    # To find new builtin_functions, run the below script.
    # $ scripts/update_builtin_functions.sh /path/to/vim/src/evalfunc.c
    builtin_functions = [AttributeDict({"name": "abs", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "acos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "add", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "and", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "append", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_LAST"}), AttributeDict({"name": "appendbufline", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_LAST"}), AttributeDict({"name": "argc", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "argidx", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "arglistid", "min_argc": 0, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "argv", "min_argc": 0, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "asin", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_beeps", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_equal", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "assert_equalfile", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_exception", "min_argc": 1, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "assert_fails", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_false", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_inrange", "min_argc": 3, "max_argc": 4, "argtype": "FEARG_3"}), AttributeDict({"name": "assert_match", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "assert_notequal", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "assert_notmatch", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "assert_report", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "assert_true", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "atan", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "atan2", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "balloon_gettext", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "balloon_show", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "balloon_split", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "browse", "min_argc": 4, "max_argc": 4, "argtype": "0"}), AttributeDict({"name": "browsedir", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "bufadd", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufexists", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "buffer_exists", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "buffer_name", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "buffer_number", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "buflisted", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufload", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufloaded", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufname", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufnr", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "bufwinid", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "bufwinnr", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "byte2line", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "byteidx", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "byteidxcomp", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "call", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "ceil", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_canread", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_close", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_close_in", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_evalexpr", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_evalraw", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_getbufnr", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_getjob", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_info", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_log", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_logfile", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_open", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_read", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_readblob", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_readraw", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_sendexpr", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_sendraw", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_setoptions", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "ch_status", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "changenr", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "char2nr", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "chdir", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "cindent", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "clearmatches", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "col", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "complete", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "complete_add", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "complete_check", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "complete_info", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "confirm", "min_argc": 1, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "copy", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "cos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "cosh", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "count", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "cscope_connection", "min_argc": 0, "max_argc": 3, "argtype": "0"}), AttributeDict({"name": "cursor", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "debugbreak", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "deepcopy", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "delete", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "deletebufline", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "did_filetype", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "diff_filler", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "diff_hlID", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "echoraw", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "empty", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "environ", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "escape", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "eval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "eventhandler", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "executable", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "execute", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "exepath", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "exists", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "exp", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "expand", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "expandcmd", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "extend", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "feedkeys", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "file_readable", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "filereadable", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "filewritable", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "filter", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "finddir", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "findfile", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "float2nr", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "floor", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "fmod", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "fnameescape", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "fnamemodify", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "foldclosed", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "foldclosedend", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "foldlevel", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "foldtext", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "foldtextresult", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "foreground", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "funcref", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "function", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "garbagecollect", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "get", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "getbufinfo", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "getbufline", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "getbufvar", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "getchangelist", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getchar", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "getcharmod", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcharsearch", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcmdline", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcmdpos", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcmdtype", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcmdwintype", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcompletion", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "getcurpos", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getcwd", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "getenv", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getfontname", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "getfperm", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getfsize", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getftime", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getftype", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getimstatus", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getjumplist", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "getline", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "getloclist", "min_argc": 1, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "getmatches", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "getmousepos", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getpid", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getpos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getqflist", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "getreg", "min_argc": 0, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "getregtype", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "gettabinfo", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "gettabvar", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "gettabwinvar", "min_argc": 3, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "gettagstack", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getwininfo", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getwinpos", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "getwinposx", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getwinposy", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "getwinvar", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "glob", "min_argc": 1, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "glob2regpat", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "globpath", "min_argc": 2, "max_argc": 5, "argtype": "FEARG_2"}), AttributeDict({"name": "has", "min_argc": 1, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "has_key", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "haslocaldir", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "hasmapto", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "highlightID", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "highlight_exists", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "histadd", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "histdel", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "histget", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "histnr", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "hlID", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "hlexists", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "hostname", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "iconv", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "indent", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "index", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "input", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "inputdialog", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "inputlist", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "inputrestore", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "inputsave", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "inputsecret", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "insert", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "interrupt", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "invert", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "isdirectory", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "isinf", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "islocked", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "isnan", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "items", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "job_getchannel", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "job_info", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "job_setoptions", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "job_start", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "job_status", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "job_stop", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "join", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "js_decode", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "js_encode", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "json_decode", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "json_encode", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "keys", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "last_buffer_nr", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "len", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "libcall", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "libcallnr", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "line", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "line2byte", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "lispindent", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "list2str", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "listener_add", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "listener_flush", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "listener_remove", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "localtime", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "log", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "log10", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "luaeval", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "map", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "maparg", "min_argc": 1, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "mapcheck", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "match", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "matchadd", "min_argc": 2, "max_argc": 5, "argtype": "FEARG_1"}), AttributeDict({"name": "matchaddpos", "min_argc": 2, "max_argc": 5, "argtype": "FEARG_1"}), AttributeDict({"name": "matcharg", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "matchdelete", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "matchend", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "matchlist", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "matchstr", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "matchstrpos", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "max", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "min", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "mkdir", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "mode", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "mzeval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "nextnonblank", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "nr2char", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "or", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "pathshorten", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "perleval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_atcursor", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_beval", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_clear", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "popup_close", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_create", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_dialog", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_filter_menu", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "popup_filter_yesno", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "popup_findinfo", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "popup_findpreview", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "popup_getoptions", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_getpos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_hide", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_locate", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "popup_menu", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_move", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_notification", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_setoptions", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_settext", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "popup_show", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "pow", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prevnonblank", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "printf", "min_argc": 1, "max_argc": 19, "argtype": "FEARG_2"}), AttributeDict({"name": "prompt_setcallback", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prompt_setinterrupt", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prompt_setprompt", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_add", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_clear", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_find", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_list", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_remove", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_type_add", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_type_change", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_type_delete", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_type_get", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "prop_type_list", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "pum_getpos", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "pumvisible", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "py3eval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "pyeval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "pyxeval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "rand", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "range", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "readdir", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "readfile", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "reg_executing", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "reg_recording", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "reltime", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "reltimefloat", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "reltimestr", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_expr", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_foreground", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_peek", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_read", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_send", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "remote_startserver", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "remove", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "rename", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "repeat", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "resolve", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "reverse", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "round", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "rubyeval", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "screenattr", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "screenchar", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "screenchars", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "screencol", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "screenpos", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "screenrow", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "screenstring", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "search", "min_argc": 1, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "searchdecl", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "searchpair", "min_argc": 3, "max_argc": 7, "argtype": "0"}), AttributeDict({"name": "searchpairpos", "min_argc": 3, "max_argc": 7, "argtype": "0"}), AttributeDict({"name": "searchpos", "min_argc": 1, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "server2client", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "serverlist", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "setbufline", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "setbufvar", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "setcharsearch", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "setcmdpos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "setenv", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "setfperm", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "setline", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "setloclist", "min_argc": 2, "max_argc": 4, "argtype": "FEARG_2"}), AttributeDict({"name": "setmatches", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "setpos", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "setqflist", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "setreg", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "settabvar", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "settabwinvar", "min_argc": 4, "max_argc": 4, "argtype": "FEARG_4"}), AttributeDict({"name": "settagstack", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "setwinvar", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_3"}), AttributeDict({"name": "sha256", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "shellescape", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "shiftwidth", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_define", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_getdefined", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_getplaced", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_jump", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_place", "min_argc": 4, "max_argc": 5, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_placelist", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_undefine", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_unplace", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "sign_unplacelist", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "simplify", "min_argc": 1, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "sin", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sinh", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "sort", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "sound_clear", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "sound_playevent", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "sound_playfile", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "sound_stop", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "soundfold", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "spellbadword", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "spellsuggest", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "split", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "sqrt", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "srand", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "state", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "str2float", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "str2list", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "str2nr", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "strcharpart", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "strchars", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "strdisplaywidth", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "strftime", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "strgetchar", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "stridx", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "string", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "strlen", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "strpart", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "strptime", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "strridx", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "strtrans", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "strwidth", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "submatch", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "substitute", "min_argc": 4, "max_argc": 4, "argtype": "FEARG_1"}), AttributeDict({"name": "swapinfo", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "swapname", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "synID", "min_argc": 3, "max_argc": 3, "argtype": "0"}), AttributeDict({"name": "synIDattr", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "synIDtrans", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "synconcealed", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "synstack", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "system", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "systemlist", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "tabpagebuflist", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "tabpagenr", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "tabpagewinnr", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "tagfiles", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "taglist", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "tan", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "tanh", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "tempname", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "term_dumpdiff", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "term_dumpload", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_dumpwrite", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "term_getaltscreen", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getansicolors", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getattr", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getcursor", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getjob", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getline", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getscrolled", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getsize", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_getstatus", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_gettitle", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "term_gettty", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_list", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "term_scrape", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_sendkeys", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_setansicolors", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_setapi", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_setkill", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_setrestore", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_setsize", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "term_start", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "term_wait", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "test_alloc_fail", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "test_autochdir", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_feedinput", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_garbagecollect_now", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_garbagecollect_soon", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_getvalue", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_ignore_error", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_null_blob", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_channel", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_dict", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_job", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_list", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_partial", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_null_string", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_option_not_set", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_override", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_2"}), AttributeDict({"name": "test_refcount", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_scrollbar", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "test_setmouse", "min_argc": 2, "max_argc": 2, "argtype": "0"}), AttributeDict({"name": "test_settime", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_srand_seed", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "test_unknown", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "test_void", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "timer_info", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "timer_pause", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "timer_start", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "timer_stop", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "timer_stopall", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "tolower", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "toupper", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "tr", "min_argc": 3, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "trim", "min_argc": 1, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "trunc", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "type", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "undofile", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "undotree", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "uniq", "min_argc": 1, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "values", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "virtcol", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "visualmode", "min_argc": 0, "max_argc": 1, "argtype": "0"}), AttributeDict({"name": "wildmenumode", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "win_execute", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_2"}), AttributeDict({"name": "win_findbuf", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_getid", "min_argc": 0, "max_argc": 2, "argtype": "FEARG_1"}), AttributeDict({"name": "win_gettype", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_gotoid", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_id2tabwin", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_id2win", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_screenpos", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "win_splitmove", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "winbufnr", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "wincol", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "windowsversion", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "winheight", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "winlayout", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "winline", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "winnr", "min_argc": 0, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "winrestcmd", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "winrestview", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "winsaveview", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "winwidth", "min_argc": 1, "max_argc": 1, "argtype": "FEARG_1"}), AttributeDict({"name": "wordcount", "min_argc": 0, "max_argc": 0, "argtype": "0"}), AttributeDict({"name": "writefile", "min_argc": 2, "max_argc": 3, "argtype": "FEARG_1"}), AttributeDict({"name": "xor", "min_argc": 2, "max_argc": 2, "argtype": "FEARG_1"})]


class ExprTokenizer:

    def __init__(self, reader):
        self.reader = reader
        self.cache = AttributeDict({})

    def token(self, type, value, pos):
        return AttributeDict({"type": type, "value": value, "pos": pos})

    def peek(self):
        pos = self.reader.tell()
        r = self.get()
        self.reader.seek_set(pos)
        return r

    def get(self):
        # FIXME: remove dirty hack
        if viml_has_key(self.cache, self.reader.tell()):
            x = self.cache[self.reader.tell()]
            self.reader.seek_set(x[0])
            return x[1]
        pos = self.reader.tell()
        self.reader.skip_white()
        r = self.get2()
        self.cache[pos] = [self.reader.tell(), r]
        return r

    def get2(self):
        r = self.reader
        pos = r.getpos()
        c = r.peek()
        if c == "<EOF>":
            return self.token(TOKEN_EOF, c, pos)
        elif c == "<EOL>":
            r.seek_cur(1)
            return self.token(TOKEN_EOL, c, pos)
        elif iswhite(c):
            s = r.read_white()
            return self.token(TOKEN_SPACE, s, pos)
        elif c == "0" and (r.p(1) == "X" or r.p(1) == "x") and isxdigit(r.p(2)):
            s = r.getn(3)
            s += r.read_xdigit()
            return self.token(TOKEN_NUMBER, s, pos)
        elif c == "0" and (r.p(1) == "B" or r.p(1) == "b") and (r.p(2) == "0" or r.p(2) == "1"):
            s = r.getn(3)
            s += r.read_bdigit()
            return self.token(TOKEN_NUMBER, s, pos)
        elif c == "0" and (r.p(1) == "Z" or r.p(1) == "z") and r.p(2) != ".":
            s = r.getn(2)
            s += r.read_blob()
            return self.token(TOKEN_BLOB, s, pos)
        elif isdigit(c):
            s = r.read_digit()
            if r.p(0) == "." and isdigit(r.p(1)):
                s += r.getn(1)
                s += r.read_digit()
                if (r.p(0) == "E" or r.p(0) == "e") and (isdigit(r.p(1)) or (r.p(1) == "-" or r.p(1) == "+") and isdigit(r.p(2))):
                    s += r.getn(2)
                    s += r.read_digit()
            return self.token(TOKEN_NUMBER, s, pos)
        elif c == "i" and r.p(1) == "s" and not isidc(r.p(2)):
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_ISCI, "is?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_ISCS, "is#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_IS, "is", pos)
        elif c == "i" and r.p(1) == "s" and r.p(2) == "n" and r.p(3) == "o" and r.p(4) == "t" and not isidc(r.p(5)):
            if r.p(5) == "?":
                r.seek_cur(6)
                return self.token(TOKEN_ISNOTCI, "isnot?", pos)
            elif r.p(5) == "#":
                r.seek_cur(6)
                return self.token(TOKEN_ISNOTCS, "isnot#", pos)
            else:
                r.seek_cur(5)
                return self.token(TOKEN_ISNOT, "isnot", pos)
        elif isnamec1(c):
            s = r.read_name()
            return self.token(TOKEN_IDENTIFIER, s, pos)
        elif c == "|" and r.p(1) == "|":
            r.seek_cur(2)
            return self.token(TOKEN_OROR, "||", pos)
        elif c == "&" and r.p(1) == "&":
            r.seek_cur(2)
            return self.token(TOKEN_ANDAND, "&&", pos)
        elif c == "=" and r.p(1) == "=":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_EQEQCI, "==?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_EQEQCS, "==#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_EQEQ, "==", pos)
        elif c == "!" and r.p(1) == "=":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_NEQCI, "!=?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_NEQCS, "!=#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_NEQ, "!=", pos)
        elif c == ">" and r.p(1) == "=":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_GTEQCI, ">=?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_GTEQCS, ">=#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_GTEQ, ">=", pos)
        elif c == "<" and r.p(1) == "=":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_LTEQCI, "<=?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_LTEQCS, "<=#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_LTEQ, "<=", pos)
        elif c == "=" and r.p(1) == "~":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_MATCHCI, "=~?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_MATCHCS, "=~#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_MATCH, "=~", pos)
        elif c == "!" and r.p(1) == "~":
            if r.p(2) == "?":
                r.seek_cur(3)
                return self.token(TOKEN_NOMATCHCI, "!~?", pos)
            elif r.p(2) == "#":
                r.seek_cur(3)
                return self.token(TOKEN_NOMATCHCS, "!~#", pos)
            else:
                r.seek_cur(2)
                return self.token(TOKEN_NOMATCH, "!~", pos)
        elif c == ">":
            if r.p(1) == "?":
                r.seek_cur(2)
                return self.token(TOKEN_GTCI, ">?", pos)
            elif r.p(1) == "#":
                r.seek_cur(2)
                return self.token(TOKEN_GTCS, ">#", pos)
            else:
                r.seek_cur(1)
                return self.token(TOKEN_GT, ">", pos)
        elif c == "<":
            if r.p(1) == "?":
                r.seek_cur(2)
                return self.token(TOKEN_LTCI, "<?", pos)
            elif r.p(1) == "#":
                r.seek_cur(2)
                return self.token(TOKEN_LTCS, "<#", pos)
            else:
                r.seek_cur(1)
                return self.token(TOKEN_LT, "<", pos)
        elif c == "+":
            r.seek_cur(1)
            return self.token(TOKEN_PLUS, "+", pos)
        elif c == "-":
            if r.p(1) == ">":
                r.seek_cur(2)
                return self.token(TOKEN_ARROW, "->", pos)
            else:
                r.seek_cur(1)
                return self.token(TOKEN_MINUS, "-", pos)
        elif c == ".":
            if r.p(1) == "." and r.p(2) == ".":
                r.seek_cur(3)
                return self.token(TOKEN_DOTDOTDOT, "...", pos)
            elif r.p(1) == ".":
                r.seek_cur(2)
                return self.token(TOKEN_DOTDOT, "..", pos)
                # TODO check scriptversion?
            else:
                r.seek_cur(1)
                return self.token(TOKEN_DOT, ".", pos)
                # TODO check scriptversion?
        elif c == "*":
            r.seek_cur(1)
            return self.token(TOKEN_STAR, "*", pos)
        elif c == "/":
            r.seek_cur(1)
            return self.token(TOKEN_SLASH, "/", pos)
        elif c == "%":
            r.seek_cur(1)
            return self.token(TOKEN_PERCENT, "%", pos)
        elif c == "!":
            r.seek_cur(1)
            return self.token(TOKEN_NOT, "!", pos)
        elif c == "?":
            r.seek_cur(1)
            return self.token(TOKEN_QUESTION, "?", pos)
        elif c == ":":
            r.seek_cur(1)
            return self.token(TOKEN_COLON, ":", pos)
        elif c == "#":
            if r.p(1) == "{":
                r.seek_cur(2)
                return self.token(TOKEN_LITCOPEN, "#{", pos)
            else:
                r.seek_cur(1)
                return self.token(TOKEN_SHARP, "#", pos)
        elif c == "(":
            r.seek_cur(1)
            return self.token(TOKEN_POPEN, "(", pos)
        elif c == ")":
            r.seek_cur(1)
            return self.token(TOKEN_PCLOSE, ")", pos)
        elif c == "[":
            r.seek_cur(1)
            return self.token(TOKEN_SQOPEN, "[", pos)
        elif c == "]":
            r.seek_cur(1)
            return self.token(TOKEN_SQCLOSE, "]", pos)
        elif c == "{":
            r.seek_cur(1)
            return self.token(TOKEN_COPEN, "{", pos)
        elif c == "}":
            r.seek_cur(1)
            return self.token(TOKEN_CCLOSE, "}", pos)
        elif c == ",":
            r.seek_cur(1)
            return self.token(TOKEN_COMMA, ",", pos)
        elif c == "'":
            r.seek_cur(1)
            return self.token(TOKEN_SQUOTE, "'", pos)
        elif c == "\"":
            r.seek_cur(1)
            return self.token(TOKEN_DQUOTE, "\"", pos)
        elif c == "$":
            s = r.getn(1)
            s += r.read_word()
            return self.token(TOKEN_ENV, s, pos)
        elif c == "@":
            # @<EOL> is treated as @"
            return self.token(TOKEN_REG, r.getn(2), pos)
        elif c == "&":
            s = ""
            if (r.p(1) == "g" or r.p(1) == "l") and r.p(2) == ":":
                s = r.getn(3) + r.read_word()
            else:
                s = r.getn(1) + r.read_word()
            return self.token(TOKEN_OPTION, s, pos)
        elif c == "=":
            r.seek_cur(1)
            return self.token(TOKEN_EQ, "=", pos)
        elif c == "|":
            r.seek_cur(1)
            return self.token(TOKEN_OR, "|", pos)
        elif c == ";":
            r.seek_cur(1)
            return self.token(TOKEN_SEMICOLON, ";", pos)
        elif c == "`":
            r.seek_cur(1)
            return self.token(TOKEN_BACKTICK, "`", pos)
        else:
            raise VimLParserException(Err(viml_printf("unexpected character: %s", c), self.reader.getpos()))

    def get_sstring(self):
        self.reader.skip_white()
        c = self.reader.p(0)
        if c != "'":
            raise VimLParserException(Err(viml_printf("unexpected character: %s", c), self.reader.getpos()))
        self.reader.seek_cur(1)
        s = ""
        while TRUE:
            c = self.reader.p(0)
            if c == "<EOF>" or c == "<EOL>":
                raise VimLParserException(Err("unexpected EOL", self.reader.getpos()))
            elif c == "'":
                self.reader.seek_cur(1)
                if self.reader.p(0) == "'":
                    self.reader.seek_cur(1)
                    s += "''"
                else:
                    break
            else:
                self.reader.seek_cur(1)
                s += c
        return s

    def get_dstring(self):
        self.reader.skip_white()
        c = self.reader.p(0)
        if c != "\"":
            raise VimLParserException(Err(viml_printf("unexpected character: %s", c), self.reader.getpos()))
        self.reader.seek_cur(1)
        s = ""
        while TRUE:
            c = self.reader.p(0)
            if c == "<EOF>" or c == "<EOL>":
                raise VimLParserException(Err("unexpectd EOL", self.reader.getpos()))
            elif c == "\"":
                self.reader.seek_cur(1)
                break
            elif c == "\\":
                self.reader.seek_cur(1)
                s += c
                c = self.reader.p(0)
                if c == "<EOF>" or c == "<EOL>":
                    raise VimLParserException(Err("ExprTokenizer: unexpected EOL", self.reader.getpos()))
                self.reader.seek_cur(1)
                s += c
            else:
                self.reader.seek_cur(1)
                s += c
        return s

    def parse_dict_literal_key(self):
        self.reader.skip_white()
        c = self.reader.peek()
        if not isalnum(c) and c != "_" and c != "-":
            raise VimLParserException(Err(viml_printf("unexpected character: %s", c), self.reader.getpos()))
        node = Node(NODE_STRING)
        s = c
        self.reader.seek_cur(1)
        node.pos = self.reader.getpos()
        while TRUE:
            c = self.reader.p(0)
            if c == "<EOF>" or c == "<EOL>":
                raise VimLParserException(Err("unexpectd EOL", self.reader.getpos()))
            if not isalnum(c) and c != "_" and c != "-":
                break
            self.reader.seek_cur(1)
            s += c
        node.value = "'" + s + "'"
        return node


class ExprParser:

    def __init__(self, reader):
        self.reader = reader
        self.tokenizer = ExprTokenizer(reader)

    def parse(self):
        return self.parse_expr1()

    # expr1: expr2 ? expr1 : expr1
    def parse_expr1(self):
        left = self.parse_expr2()
        pos = self.reader.tell()
        token = self.tokenizer.get()
        if token.type == TOKEN_QUESTION:
            node = Node(NODE_TERNARY)
            node.pos = token.pos
            node.cond = left
            node.left = self.parse_expr1()
            token = self.tokenizer.get()
            if token.type != TOKEN_COLON:
                raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
            node.right = self.parse_expr1()
            left = node
        else:
            self.reader.seek_set(pos)
        return left

    # expr2: expr3 || expr3 ..
    def parse_expr2(self):
        left = self.parse_expr3()
        while TRUE:
            pos = self.reader.tell()
            token = self.tokenizer.get()
            if token.type == TOKEN_OROR:
                node = Node(NODE_OR)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr3()
                left = node
            else:
                self.reader.seek_set(pos)
                break
        return left

    # expr3: expr4 && expr4
    def parse_expr3(self):
        left = self.parse_expr4()
        while TRUE:
            pos = self.reader.tell()
            token = self.tokenizer.get()
            if token.type == TOKEN_ANDAND:
                node = Node(NODE_AND)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr4()
                left = node
            else:
                self.reader.seek_set(pos)
                break
        return left

    # expr4: expr5 == expr5
    #        expr5 != expr5
    #        expr5 >  expr5
    #        expr5 >= expr5
    #        expr5 <  expr5
    #        expr5 <= expr5
    #        expr5 =~ expr5
    #        expr5 !~ expr5
    #
    #        expr5 ==? expr5
    #        expr5 ==# expr5
    #        etc.
    #
    #        expr5 is expr5
    #        expr5 isnot expr5
    def parse_expr4(self):
        left = self.parse_expr5()
        pos = self.reader.tell()
        token = self.tokenizer.get()
        if token.type == TOKEN_EQEQ:
            node = Node(NODE_EQUAL)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_EQEQCI:
            node = Node(NODE_EQUALCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_EQEQCS:
            node = Node(NODE_EQUALCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NEQ:
            node = Node(NODE_NEQUAL)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NEQCI:
            node = Node(NODE_NEQUALCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NEQCS:
            node = Node(NODE_NEQUALCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GT:
            node = Node(NODE_GREATER)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GTCI:
            node = Node(NODE_GREATERCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GTCS:
            node = Node(NODE_GREATERCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GTEQ:
            node = Node(NODE_GEQUAL)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GTEQCI:
            node = Node(NODE_GEQUALCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_GTEQCS:
            node = Node(NODE_GEQUALCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LT:
            node = Node(NODE_SMALLER)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LTCI:
            node = Node(NODE_SMALLERCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LTCS:
            node = Node(NODE_SMALLERCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LTEQ:
            node = Node(NODE_SEQUAL)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LTEQCI:
            node = Node(NODE_SEQUALCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_LTEQCS:
            node = Node(NODE_SEQUALCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_MATCH:
            node = Node(NODE_MATCH)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_MATCHCI:
            node = Node(NODE_MATCHCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_MATCHCS:
            node = Node(NODE_MATCHCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NOMATCH:
            node = Node(NODE_NOMATCH)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NOMATCHCI:
            node = Node(NODE_NOMATCHCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_NOMATCHCS:
            node = Node(NODE_NOMATCHCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_IS:
            node = Node(NODE_IS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_ISCI:
            node = Node(NODE_ISCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_ISCS:
            node = Node(NODE_ISCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_ISNOT:
            node = Node(NODE_ISNOT)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_ISNOTCI:
            node = Node(NODE_ISNOTCI)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        elif token.type == TOKEN_ISNOTCS:
            node = Node(NODE_ISNOTCS)
            node.pos = token.pos
            node.left = left
            node.right = self.parse_expr5()
            left = node
        else:
            self.reader.seek_set(pos)
        return left

    # expr5: expr6 + expr6 ..
    #        expr6 - expr6 ..
    #        expr6 . expr6 ..
    #        expr6 .. expr6 ..
    def parse_expr5(self):
        left = self.parse_expr6()
        while TRUE:
            pos = self.reader.tell()
            token = self.tokenizer.get()
            if token.type == TOKEN_PLUS:
                node = Node(NODE_ADD)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr6()
                left = node
            elif token.type == TOKEN_MINUS:
                node = Node(NODE_SUBTRACT)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr6()
                left = node
            elif token.type == TOKEN_DOTDOT:
                # TODO check scriptversion?
                node = Node(NODE_CONCAT)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr6()
                left = node
            elif token.type == TOKEN_DOT:
                # TODO check scriptversion?
                node = Node(NODE_CONCAT)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr6()
                left = node
            else:
                self.reader.seek_set(pos)
                break
        return left

    # expr6: expr7 * expr7 ..
    #        expr7 / expr7 ..
    #        expr7 % expr7 ..
    def parse_expr6(self):
        left = self.parse_expr7()
        while TRUE:
            pos = self.reader.tell()
            token = self.tokenizer.get()
            if token.type == TOKEN_STAR:
                node = Node(NODE_MULTIPLY)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr7()
                left = node
            elif token.type == TOKEN_SLASH:
                node = Node(NODE_DIVIDE)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr7()
                left = node
            elif token.type == TOKEN_PERCENT:
                node = Node(NODE_REMAINDER)
                node.pos = token.pos
                node.left = left
                node.right = self.parse_expr7()
                left = node
            else:
                self.reader.seek_set(pos)
                break
        return left

    # expr7: ! expr7
    #        - expr7
    #        + expr7
    def parse_expr7(self):
        pos = self.reader.tell()
        token = self.tokenizer.get()
        if token.type == TOKEN_NOT:
            node = Node(NODE_NOT)
            node.pos = token.pos
            node.left = self.parse_expr7()
            return node
        elif token.type == TOKEN_MINUS:
            node = Node(NODE_MINUS)
            node.pos = token.pos
            node.left = self.parse_expr7()
            return node
        elif token.type == TOKEN_PLUS:
            node = Node(NODE_PLUS)
            node.pos = token.pos
            node.left = self.parse_expr7()
            return node
        else:
            self.reader.seek_set(pos)
            node = self.parse_expr8()
            return node

    # expr8: expr8[expr1]
    #        expr8[expr1 : expr1]
    #        expr8.name
    #        expr8->name(expr1, ...)
    #        expr8->s:user_func(expr1, ...)
    #        expr8->{lambda}(expr1, ...)
    #        expr8(expr1, ...)
    def parse_expr8(self):
        left = self.parse_expr9()
        while TRUE:
            pos = self.reader.tell()
            c = self.reader.peek()
            token = self.tokenizer.get()
            if not iswhite(c) and token.type == TOKEN_SQOPEN:
                npos = token.pos
                if self.tokenizer.peek().type == TOKEN_COLON:
                    self.tokenizer.get()
                    node = Node(NODE_SLICE)
                    node.pos = npos
                    node.left = left
                    node.rlist = [NIL, NIL]
                    token = self.tokenizer.peek()
                    if token.type != TOKEN_SQCLOSE:
                        node.rlist[1] = self.parse_expr1()
                    token = self.tokenizer.get()
                    if token.type != TOKEN_SQCLOSE:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                    left = node
                else:
                    right = self.parse_expr1()
                    if self.tokenizer.peek().type == TOKEN_COLON:
                        self.tokenizer.get()
                        node = Node(NODE_SLICE)
                        node.pos = npos
                        node.left = left
                        node.rlist = [right, NIL]
                        token = self.tokenizer.peek()
                        if token.type != TOKEN_SQCLOSE:
                            node.rlist[1] = self.parse_expr1()
                        token = self.tokenizer.get()
                        if token.type != TOKEN_SQCLOSE:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                        left = node
                    else:
                        node = Node(NODE_SUBSCRIPT)
                        node.pos = npos
                        node.left = left
                        node.right = right
                        token = self.tokenizer.get()
                        if token.type != TOKEN_SQCLOSE:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                        left = node
                del node
            elif token.type == TOKEN_ARROW:
                funcname_or_lambda = self.parse_expr9()
                token = self.tokenizer.get()
                if token.type != TOKEN_POPEN:
                    raise VimLParserException(Err("E107: Missing parentheses: lambda", token.pos))
                right = Node(NODE_CALL)
                right.pos = token.pos
                right.left = funcname_or_lambda
                right.rlist = self.parse_rlist()
                node = Node(NODE_METHOD)
                node.pos = token.pos
                node.left = left
                node.right = right
                left = node
                del node
            elif token.type == TOKEN_POPEN:
                node = Node(NODE_CALL)
                node.pos = token.pos
                node.left = left
                node.rlist = self.parse_rlist()
                left = node
                del node
            elif not iswhite(c) and token.type == TOKEN_DOT:
                # TODO check scriptversion?
                node = self.parse_dot(token, left)
                if node is NIL:
                    self.reader.seek_set(pos)
                    break
                left = node
                del node
            else:
                self.reader.seek_set(pos)
                break
        return left

    def parse_rlist(self):
        rlist = []
        token = self.tokenizer.peek()
        if self.tokenizer.peek().type == TOKEN_PCLOSE:
            self.tokenizer.get()
        else:
            while TRUE:
                viml_add(rlist, self.parse_expr1())
                token = self.tokenizer.get()
                if token.type == TOKEN_COMMA:
                    # XXX: Vim allows foo(a, b, ).  Lint should warn it.
                    if self.tokenizer.peek().type == TOKEN_PCLOSE:
                        self.tokenizer.get()
                        break
                elif token.type == TOKEN_PCLOSE:
                    break
                else:
                    raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        if viml_len(rlist) > MAX_FUNC_ARGS:
            # TODO: funcname E740: Too many arguments for function: %s
            raise VimLParserException(Err("E740: Too many arguments for function", token.pos))
        return rlist

    # expr9: number
    #        "string"
    #        'string'
    #        [expr1, ...]
    #        {expr1: expr1, ...}
    #        #{literal_key1: expr1, ...}
    #        {args -> expr1}
    #        &option
    #        (expr1)
    #        variable
    #        var{ria}ble
    #        $VAR
    #        @r
    #        function(expr1, ...)
    #        func{ti}on(expr1, ...)
    def parse_expr9(self):
        pos = self.reader.tell()
        token = self.tokenizer.get()
        node = Node(-1)
        if token.type == TOKEN_NUMBER:
            node = Node(NODE_NUMBER)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_BLOB:
            node = Node(NODE_BLOB)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_DQUOTE:
            self.reader.seek_set(pos)
            node = Node(NODE_STRING)
            node.pos = token.pos
            node.value = "\"" + self.tokenizer.get_dstring() + "\""
        elif token.type == TOKEN_SQUOTE:
            self.reader.seek_set(pos)
            node = Node(NODE_STRING)
            node.pos = token.pos
            node.value = "'" + self.tokenizer.get_sstring() + "'"
        elif token.type == TOKEN_SQOPEN:
            node = Node(NODE_LIST)
            node.pos = token.pos
            node.value = []
            token = self.tokenizer.peek()
            if token.type == TOKEN_SQCLOSE:
                self.tokenizer.get()
            else:
                while TRUE:
                    viml_add(node.value, self.parse_expr1())
                    token = self.tokenizer.peek()
                    if token.type == TOKEN_COMMA:
                        self.tokenizer.get()
                        if self.tokenizer.peek().type == TOKEN_SQCLOSE:
                            self.tokenizer.get()
                            break
                    elif token.type == TOKEN_SQCLOSE:
                        self.tokenizer.get()
                        break
                    else:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        elif token.type == TOKEN_COPEN or token.type == TOKEN_LITCOPEN:
            is_litdict = token.type == TOKEN_LITCOPEN
            savepos = self.reader.tell()
            nodepos = token.pos
            token = self.tokenizer.get()
            lambda_ = token.type == TOKEN_ARROW
            if not lambda_ and not (token.type == TOKEN_SQUOTE or token.type == TOKEN_DQUOTE):
                # if the token type is stirng, we cannot peek next token and we can
                # assume it's not lambda.
                token2 = self.tokenizer.peek()
                lambda_ = token2.type == TOKEN_ARROW or token2.type == TOKEN_COMMA
            # fallback to dict or {expr} if true
            fallback = FALSE
            if lambda_:
                # lambda {token,...} {->...} {token->...}
                node = Node(NODE_LAMBDA)
                node.pos = nodepos
                node.rlist = []
                named = AttributeDict({})
                while TRUE:
                    if token.type == TOKEN_ARROW:
                        break
                    elif token.type == TOKEN_IDENTIFIER:
                        if not isargname(token.value):
                            raise VimLParserException(Err(viml_printf("E125: Illegal argument: %s", token.value), token.pos))
                        elif viml_has_key(named, token.value):
                            raise VimLParserException(Err(viml_printf("E853: Duplicate argument name: %s", token.value), token.pos))
                        named[token.value] = 1
                        varnode = Node(NODE_IDENTIFIER)
                        varnode.pos = token.pos
                        varnode.value = token.value
                        # XXX: Vim doesn't skip white space before comma.  {a ,b -> ...} => E475
                        if iswhite(self.reader.p(0)) and self.tokenizer.peek().type == TOKEN_COMMA:
                            raise VimLParserException(Err("E475: Invalid argument: White space is not allowed before comma", self.reader.getpos()))
                        token = self.tokenizer.get()
                        viml_add(node.rlist, varnode)
                        if token.type == TOKEN_COMMA:
                            # XXX: Vim allows last comma.  {a, b, -> ...} => OK
                            token = self.tokenizer.peek()
                            if token.type == TOKEN_ARROW:
                                self.tokenizer.get()
                                break
                        elif token.type == TOKEN_ARROW:
                            break
                        else:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s, type: %d", token.value, token.type), token.pos))
                    elif token.type == TOKEN_DOTDOTDOT:
                        varnode = Node(NODE_IDENTIFIER)
                        varnode.pos = token.pos
                        varnode.value = token.value
                        viml_add(node.rlist, varnode)
                        token = self.tokenizer.peek()
                        if token.type == TOKEN_ARROW:
                            self.tokenizer.get()
                            break
                        else:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                    else:
                        fallback = TRUE
                        break
                    token = self.tokenizer.get()
                if not fallback:
                    node.left = self.parse_expr1()
                    token = self.tokenizer.get()
                    if token.type != TOKEN_CCLOSE:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                    return node
            # dict
            node = Node(NODE_DICT)
            node.pos = nodepos
            node.value = []
            self.reader.seek_set(savepos)
            token = self.tokenizer.peek()
            if token.type == TOKEN_CCLOSE:
                self.tokenizer.get()
                return node
            while 1:
                key = self.tokenizer.parse_dict_literal_key() if is_litdict else self.parse_expr1()
                token = self.tokenizer.get()
                if token.type == TOKEN_CCLOSE:
                    if not viml_empty(node.value):
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                    self.reader.seek_set(pos)
                    node = self.parse_identifier()
                    break
                if token.type != TOKEN_COLON:
                    raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                val = self.parse_expr1()
                viml_add(node.value, [key, val])
                token = self.tokenizer.get()
                if token.type == TOKEN_COMMA:
                    if self.tokenizer.peek().type == TOKEN_CCLOSE:
                        self.tokenizer.get()
                        break
                elif token.type == TOKEN_CCLOSE:
                    break
                else:
                    raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
            return node
        elif token.type == TOKEN_POPEN:
            node = self.parse_expr1()
            token = self.tokenizer.get()
            if token.type != TOKEN_PCLOSE:
                raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        elif token.type == TOKEN_OPTION:
            node = Node(NODE_OPTION)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_IDENTIFIER:
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif FALSE and (token.type == TOKEN_COLON or token.type == TOKEN_SHARP):
            # XXX: no parse error but invalid expression
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_LT and viml_equalci(self.reader.peekn(4), "SID>"):
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_IS or token.type == TOKEN_ISCS or token.type == TOKEN_ISNOT or token.type == TOKEN_ISNOTCS:
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_ENV:
            node = Node(NODE_ENV)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_REG:
            node = Node(NODE_REG)
            node.pos = token.pos
            node.value = token.value
        else:
            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        return node

    # SUBSCRIPT or CONCAT
    #   dict "." [0-9A-Za-z_]+ => (subscript dict key)
    #   str  "." expr6         => (concat str expr6)
    def parse_dot(self, token, left):
        if left.type != NODE_IDENTIFIER and left.type != NODE_CURLYNAME and left.type != NODE_DICT and left.type != NODE_SUBSCRIPT and left.type != NODE_CALL and left.type != NODE_DOT:
            return NIL
        if not iswordc(self.reader.p(0)):
            return NIL
        pos = self.reader.getpos()
        name = self.reader.read_word()
        if isnamec(self.reader.p(0)):
            # XXX: foo is str => ok, foo is obj => invalid expression
            # foo.s:bar or foo.bar#baz
            return NIL
        node = Node(NODE_DOT)
        node.pos = token.pos
        node.left = left
        node.right = Node(NODE_IDENTIFIER)
        node.right.pos = pos
        node.right.value = name
        return node

    # CONCAT
    #   str  ".." expr6         => (concat str expr6)
    def parse_concat(self, token, left):
        if left.type != NODE_IDENTIFIER and left.type != NODE_CURLYNAME and left.type != NODE_DICT and left.type != NODE_SUBSCRIPT and left.type != NODE_CALL and left.type != NODE_DOT:
            return NIL
        if not iswordc(self.reader.p(0)):
            return NIL
        pos = self.reader.getpos()
        name = self.reader.read_word()
        if isnamec(self.reader.p(0)):
            # XXX: foo is str => ok, foo is obj => invalid expression
            # foo.s:bar or foo.bar#baz
            return NIL
        node = Node(NODE_CONCAT)
        node.pos = token.pos
        node.left = left
        node.right = Node(NODE_IDENTIFIER)
        node.right.pos = pos
        node.right.value = name
        return node

    def parse_identifier(self):
        self.reader.skip_white()
        npos = self.reader.getpos()
        curly_parts = self.parse_curly_parts()
        if viml_len(curly_parts) == 1 and curly_parts[0].type == NODE_CURLYNAMEPART:
            node = Node(NODE_IDENTIFIER)
            node.pos = npos
            node.value = curly_parts[0].value
            return node
        else:
            node = Node(NODE_CURLYNAME)
            node.pos = npos
            node.value = curly_parts
            return node

    def parse_curly_parts(self):
        curly_parts = []
        c = self.reader.peek()
        pos = self.reader.getpos()
        if c == "<" and viml_equalci(self.reader.peekn(5), "<SID>"):
            name = self.reader.getn(5)
            node = Node(NODE_CURLYNAMEPART)
            node.curly = FALSE
            # Keep backword compatibility for the curly attribute
            node.pos = pos
            node.value = name
            viml_add(curly_parts, node)
        while TRUE:
            c = self.reader.peek()
            if isnamec(c):
                pos = self.reader.getpos()
                name = self.reader.read_name()
                node = Node(NODE_CURLYNAMEPART)
                node.curly = FALSE
                # Keep backword compatibility for the curly attribute
                node.pos = pos
                node.value = name
                viml_add(curly_parts, node)
            elif c == "{":
                self.reader.get()
                pos = self.reader.getpos()
                node = Node(NODE_CURLYNAMEEXPR)
                node.curly = TRUE
                # Keep backword compatibility for the curly attribute
                node.pos = pos
                node.value = self.parse_expr1()
                viml_add(curly_parts, node)
                self.reader.skip_white()
                c = self.reader.p(0)
                if c != "}":
                    raise VimLParserException(Err(viml_printf("unexpected token: %s", c), self.reader.getpos()))
                self.reader.seek_cur(1)
            else:
                break
        return curly_parts


class LvalueParser(ExprParser):

    def parse(self):
        return self.parse_lv8()

    # expr8: expr8[expr1]
    #        expr8[expr1 : expr1]
    #        expr8.name
    def parse_lv8(self):
        left = self.parse_lv9()
        while TRUE:
            pos = self.reader.tell()
            c = self.reader.peek()
            token = self.tokenizer.get()
            if not iswhite(c) and token.type == TOKEN_SQOPEN:
                npos = token.pos
                node = Node(-1)
                if self.tokenizer.peek().type == TOKEN_COLON:
                    self.tokenizer.get()
                    node = Node(NODE_SLICE)
                    node.pos = npos
                    node.left = left
                    node.rlist = [NIL, NIL]
                    token = self.tokenizer.peek()
                    if token.type != TOKEN_SQCLOSE:
                        node.rlist[1] = self.parse_expr1()
                    token = self.tokenizer.get()
                    if token.type != TOKEN_SQCLOSE:
                        raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                else:
                    right = self.parse_expr1()
                    if self.tokenizer.peek().type == TOKEN_COLON:
                        self.tokenizer.get()
                        node = Node(NODE_SLICE)
                        node.pos = npos
                        node.left = left
                        node.rlist = [right, NIL]
                        token = self.tokenizer.peek()
                        if token.type != TOKEN_SQCLOSE:
                            node.rlist[1] = self.parse_expr1()
                        token = self.tokenizer.get()
                        if token.type != TOKEN_SQCLOSE:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                    else:
                        node = Node(NODE_SUBSCRIPT)
                        node.pos = npos
                        node.left = left
                        node.right = right
                        token = self.tokenizer.get()
                        if token.type != TOKEN_SQCLOSE:
                            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
                left = node
                del node
            elif not iswhite(c) and token.type == TOKEN_DOT:
                node = self.parse_dot(token, left)
                if node is NIL:
                    self.reader.seek_set(pos)
                    break
                left = node
                del node
            else:
                self.reader.seek_set(pos)
                break
        return left

    # expr9: &option
    #        variable
    #        var{ria}ble
    #        $VAR
    #        @r
    def parse_lv9(self):
        pos = self.reader.tell()
        token = self.tokenizer.get()
        node = Node(-1)
        if token.type == TOKEN_COPEN:
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_OPTION:
            node = Node(NODE_OPTION)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_IDENTIFIER:
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_LT and viml_equalci(self.reader.peekn(4), "SID>"):
            self.reader.seek_set(pos)
            node = self.parse_identifier()
        elif token.type == TOKEN_ENV:
            node = Node(NODE_ENV)
            node.pos = token.pos
            node.value = token.value
        elif token.type == TOKEN_REG:
            node = Node(NODE_REG)
            node.pos = token.pos
            node.pos = token.pos
            node.value = token.value
        else:
            raise VimLParserException(Err(viml_printf("unexpected token: %s", token.value), token.pos))
        return node


class StringReader:

    def __init__(self, lines):
        self.buf = []
        self.pos = []
        lnum = 0
        offset = 0
        while lnum < viml_len(lines):
            col = 0
            for c in viml_split(lines[lnum], "\\zs"):
                viml_add(self.buf, c)
                viml_add(self.pos, [lnum + 1, col + 1, offset])
                col += viml_len(c)
                offset += viml_len(c)
            while lnum + 1 < viml_len(lines) and viml_eqregh(lines[lnum + 1], "^\\s*\\\\"):
                skip = TRUE
                col = 0
                for c in viml_split(lines[lnum + 1], "\\zs"):
                    if skip:
                        if c == "\\":
                            skip = FALSE
                    else:
                        viml_add(self.buf, c)
                        viml_add(self.pos, [lnum + 2, col + 1, offset])
                    col += viml_len(c)
                    offset += viml_len(c)
                lnum += 1
                offset += 1
            viml_add(self.buf, "<EOL>")
            viml_add(self.pos, [lnum + 1, col + 1, offset])
            lnum += 1
            offset += 1
        # for <EOF>
        viml_add(self.pos, [lnum + 1, 0, offset])
        self.i = 0

    def eof(self):
        return self.i >= viml_len(self.buf)

    def tell(self):
        return self.i

    def seek_set(self, i):
        self.i = i

    def seek_cur(self, i):
        self.i = self.i + i

    def seek_end(self, i):
        self.i = viml_len(self.buf) + i

    def p(self, i):
        if self.i >= viml_len(self.buf):
            return "<EOF>"
        return self.buf[self.i + i]

    def peek(self):
        if self.i >= viml_len(self.buf):
            return "<EOF>"
        return self.buf[self.i]

    def get(self):
        if self.i >= viml_len(self.buf):
            return "<EOF>"
        self.i += 1
        return self.buf[self.i - 1]

    def peekn(self, n):
        pos = self.tell()
        r = self.getn(n)
        self.seek_set(pos)
        return r

    def getn(self, n):
        r = ""
        j = 0
        while self.i < viml_len(self.buf) and (n < 0 or j < n):
            c = self.buf[self.i]
            if c == "<EOL>":
                break
            r += c
            self.i += 1
            j += 1
        return r

    def peekline(self):
        return self.peekn(-1)

    def readline(self):
        r = self.getn(-1)
        self.get()
        return r

    def getstr(self, begin, end):
        r = ""
        for i in viml_range(begin.i, end.i - 1):
            if i >= viml_len(self.buf):
                break
            c = self.buf[i]
            if c == "<EOL>":
                c = "\n"
            r += c
        return r

    def getpos(self):
        lnum, col, offset = self.pos[self.i]
        return AttributeDict({"i": self.i, "lnum": lnum, "col": col, "offset": offset})

    def setpos(self, pos):
        self.i = pos.i

    def read_alpha(self):
        r = ""
        while isalpha(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_alnum(self):
        r = ""
        while isalnum(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_digit(self):
        r = ""
        while isdigit(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_odigit(self):
        r = ""
        while isodigit(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_blob(self):
        r = ""
        while 1:
            s = self.peekn(2)
            if viml_eqregh(s, "^[0-9A-Fa-f][0-9A-Fa-f]$"):
                r += self.getn(2)
            elif viml_eqregh(s, "^\\.[0-9A-Fa-f]$"):
                r += self.getn(1)
            elif viml_eqregh(s, "^[0-9A-Fa-f][^0-9A-Fa-f]$"):
                raise VimLParserException(Err("E973: Blob literal should have an even number of hex characters:" + s, self.getpos()))
            else:
                break
        return r

    def read_xdigit(self):
        r = ""
        while isxdigit(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_bdigit(self):
        r = ""
        while self.peekn(1) == "0" or self.peekn(1) == "1":
            r += self.getn(1)
        return r

    def read_integer(self):
        r = ""
        c = self.peekn(1)
        if c == "-" or c == "+":
            r = self.getn(1)
        return r + self.read_digit()

    def read_word(self):
        r = ""
        while iswordc(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_white(self):
        r = ""
        while iswhite(self.peekn(1)):
            r += self.getn(1)
        return r

    def read_nonwhite(self):
        r = ""
        ch = self.peekn(1)
        while not iswhite(ch) and ch != "":
            r += self.getn(1)
            ch = self.peekn(1)
        return r

    def read_name(self):
        r = ""
        while isnamec(self.peekn(1)):
            r += self.getn(1)
        return r

    def skip_white(self):
        while iswhite(self.peekn(1)):
            self.seek_cur(1)

    def skip_white_and_colon(self):
        while TRUE:
            c = self.peekn(1)
            if not iswhite(c) and c != ":":
                break
            self.seek_cur(1)


class Compiler:

    def __init__(self):
        self.indent = [""]
        self.lines = []

    def out(self, *a000):
        if viml_len(a000) == 1:
            if a000[0][0] == ")":
                self.lines[-1] += a000[0]
            else:
                viml_add(self.lines, self.indent[0] + a000[0])
        else:
            viml_add(self.lines, self.indent[0] + viml_printf(*a000))

    def incindent(self, s):
        viml_insert(self.indent, self.indent[0] + s)

    def decindent(self):
        viml_remove(self.indent, 0)

    def compile(self, node):
        if node.type == NODE_TOPLEVEL:
            return self.compile_toplevel(node)
        elif node.type == NODE_COMMENT:
            self.compile_comment(node)
            return NIL
        elif node.type == NODE_EXCMD:
            self.compile_excmd(node)
            return NIL
        elif node.type == NODE_FUNCTION:
            self.compile_function(node)
            return NIL
        elif node.type == NODE_DELFUNCTION:
            self.compile_delfunction(node)
            return NIL
        elif node.type == NODE_RETURN:
            self.compile_return(node)
            return NIL
        elif node.type == NODE_EXCALL:
            self.compile_excall(node)
            return NIL
        elif node.type == NODE_EVAL:
            self.compile_eval(node)
            return NIL
        elif node.type == NODE_LET:
            self.compile_let(node)
            return NIL
        elif node.type == NODE_CONST:
            self.compile_const(node)
            return NIL
        elif node.type == NODE_UNLET:
            self.compile_unlet(node)
            return NIL
        elif node.type == NODE_LOCKVAR:
            self.compile_lockvar(node)
            return NIL
        elif node.type == NODE_UNLOCKVAR:
            self.compile_unlockvar(node)
            return NIL
        elif node.type == NODE_IF:
            self.compile_if(node)
            return NIL
        elif node.type == NODE_WHILE:
            self.compile_while(node)
            return NIL
        elif node.type == NODE_FOR:
            self.compile_for(node)
            return NIL
        elif node.type == NODE_CONTINUE:
            self.compile_continue(node)
            return NIL
        elif node.type == NODE_BREAK:
            self.compile_break(node)
            return NIL
        elif node.type == NODE_TRY:
            self.compile_try(node)
            return NIL
        elif node.type == NODE_THROW:
            self.compile_throw(node)
            return NIL
        elif node.type == NODE_ECHO:
            self.compile_echo(node)
            return NIL
        elif node.type == NODE_ECHON:
            self.compile_echon(node)
            return NIL
        elif node.type == NODE_ECHOHL:
            self.compile_echohl(node)
            return NIL
        elif node.type == NODE_ECHOMSG:
            self.compile_echomsg(node)
            return NIL
        elif node.type == NODE_ECHOERR:
            self.compile_echoerr(node)
            return NIL
        elif node.type == NODE_EXECUTE:
            self.compile_execute(node)
            return NIL
        elif node.type == NODE_TERNARY:
            return self.compile_ternary(node)
        elif node.type == NODE_OR:
            return self.compile_or(node)
        elif node.type == NODE_AND:
            return self.compile_and(node)
        elif node.type == NODE_EQUAL:
            return self.compile_equal(node)
        elif node.type == NODE_EQUALCI:
            return self.compile_equalci(node)
        elif node.type == NODE_EQUALCS:
            return self.compile_equalcs(node)
        elif node.type == NODE_NEQUAL:
            return self.compile_nequal(node)
        elif node.type == NODE_NEQUALCI:
            return self.compile_nequalci(node)
        elif node.type == NODE_NEQUALCS:
            return self.compile_nequalcs(node)
        elif node.type == NODE_GREATER:
            return self.compile_greater(node)
        elif node.type == NODE_GREATERCI:
            return self.compile_greaterci(node)
        elif node.type == NODE_GREATERCS:
            return self.compile_greatercs(node)
        elif node.type == NODE_GEQUAL:
            return self.compile_gequal(node)
        elif node.type == NODE_GEQUALCI:
            return self.compile_gequalci(node)
        elif node.type == NODE_GEQUALCS:
            return self.compile_gequalcs(node)
        elif node.type == NODE_SMALLER:
            return self.compile_smaller(node)
        elif node.type == NODE_SMALLERCI:
            return self.compile_smallerci(node)
        elif node.type == NODE_SMALLERCS:
            return self.compile_smallercs(node)
        elif node.type == NODE_SEQUAL:
            return self.compile_sequal(node)
        elif node.type == NODE_SEQUALCI:
            return self.compile_sequalci(node)
        elif node.type == NODE_SEQUALCS:
            return self.compile_sequalcs(node)
        elif node.type == NODE_MATCH:
            return self.compile_match(node)
        elif node.type == NODE_MATCHCI:
            return self.compile_matchci(node)
        elif node.type == NODE_MATCHCS:
            return self.compile_matchcs(node)
        elif node.type == NODE_NOMATCH:
            return self.compile_nomatch(node)
        elif node.type == NODE_NOMATCHCI:
            return self.compile_nomatchci(node)
        elif node.type == NODE_NOMATCHCS:
            return self.compile_nomatchcs(node)
        elif node.type == NODE_IS:
            return self.compile_is(node)
        elif node.type == NODE_ISCI:
            return self.compile_isci(node)
        elif node.type == NODE_ISCS:
            return self.compile_iscs(node)
        elif node.type == NODE_ISNOT:
            return self.compile_isnot(node)
        elif node.type == NODE_ISNOTCI:
            return self.compile_isnotci(node)
        elif node.type == NODE_ISNOTCS:
            return self.compile_isnotcs(node)
        elif node.type == NODE_ADD:
            return self.compile_add(node)
        elif node.type == NODE_SUBTRACT:
            return self.compile_subtract(node)
        elif node.type == NODE_CONCAT:
            return self.compile_concat(node)
        elif node.type == NODE_MULTIPLY:
            return self.compile_multiply(node)
        elif node.type == NODE_DIVIDE:
            return self.compile_divide(node)
        elif node.type == NODE_REMAINDER:
            return self.compile_remainder(node)
        elif node.type == NODE_NOT:
            return self.compile_not(node)
        elif node.type == NODE_PLUS:
            return self.compile_plus(node)
        elif node.type == NODE_MINUS:
            return self.compile_minus(node)
        elif node.type == NODE_SUBSCRIPT:
            return self.compile_subscript(node)
        elif node.type == NODE_SLICE:
            return self.compile_slice(node)
        elif node.type == NODE_DOT:
            return self.compile_dot(node)
        elif node.type == NODE_METHOD:
            return self.compile_method(node)
        elif node.type == NODE_CALL:
            return self.compile_call(node)
        elif node.type == NODE_NUMBER:
            return self.compile_number(node)
        elif node.type == NODE_BLOB:
            return self.compile_blob(node)
        elif node.type == NODE_STRING:
            return self.compile_string(node)
        elif node.type == NODE_LIST:
            return self.compile_list(node)
        elif node.type == NODE_DICT:
            return self.compile_dict(node)
        elif node.type == NODE_OPTION:
            return self.compile_option(node)
        elif node.type == NODE_IDENTIFIER:
            return self.compile_identifier(node)
        elif node.type == NODE_CURLYNAME:
            return self.compile_curlyname(node)
        elif node.type == NODE_ENV:
            return self.compile_env(node)
        elif node.type == NODE_REG:
            return self.compile_reg(node)
        elif node.type == NODE_CURLYNAMEPART:
            return self.compile_curlynamepart(node)
        elif node.type == NODE_CURLYNAMEEXPR:
            return self.compile_curlynameexpr(node)
        elif node.type == NODE_LAMBDA:
            return self.compile_lambda(node)
        elif node.type == NODE_HEREDOC:
            return self.compile_heredoc(node)
        else:
            raise VimLParserException(viml_printf("Compiler: unknown node: %s", viml_string(node)))
        return NIL

    def compile_body(self, body):
        for node in body:
            self.compile(node)

    def compile_toplevel(self, node):
        self.compile_body(node.body)
        return self.lines

    def compile_comment(self, node):
        self.out(";%s", node.str)

    def compile_excmd(self, node):
        self.out("(excmd \"%s\")", viml_escape(node.str, "\\\""))

    def compile_function(self, node):
        left = self.compile(node.left)
        rlist = [self.compile(vval) for vval in node.rlist]
        default_args = [self.compile(vval) for vval in node.default_args]
        if not viml_empty(rlist):
            remaining = FALSE
            if rlist[-1] == "...":
                viml_remove(rlist, -1)
                remaining = TRUE
            for i in viml_range(viml_len(rlist)):
                if i < viml_len(rlist) - viml_len(default_args):
                    left += viml_printf(" %s", rlist[i])
                else:
                    left += viml_printf(" (%s %s)", rlist[i], default_args[i + viml_len(default_args) - viml_len(rlist)])
            if remaining:
                left += " . ..."
        self.out("(function (%s)", left)
        self.incindent("  ")
        self.compile_body(node.body)
        self.out(")")
        self.decindent()

    def compile_delfunction(self, node):
        self.out("(delfunction %s)", self.compile(node.left))

    def compile_return(self, node):
        if node.left is NIL:
            self.out("(return)")
        else:
            self.out("(return %s)", self.compile(node.left))

    def compile_excall(self, node):
        self.out("(call %s)", self.compile(node.left))

    def compile_eval(self, node):
        self.out("(eval %s)", self.compile(node.left))

    def compile_let(self, node):
        left = ""
        if node.left is not NIL:
            left = self.compile(node.left)
        else:
            left = viml_join([self.compile(vval) for vval in node.list], " ")
            if node.rest is not NIL:
                left += " . " + self.compile(node.rest)
            left = "(" + left + ")"
        right = self.compile(node.right)
        self.out("(let %s %s %s)", node.op, left, right)

    # TODO: merge with s:Compiler.compile_let() ?
    def compile_const(self, node):
        left = ""
        if node.left is not NIL:
            left = self.compile(node.left)
        else:
            left = viml_join([self.compile(vval) for vval in node.list], " ")
            if node.rest is not NIL:
                left += " . " + self.compile(node.rest)
            left = "(" + left + ")"
        right = self.compile(node.right)
        self.out("(const %s %s %s)", node.op, left, right)

    def compile_unlet(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(unlet %s)", viml_join(list, " "))

    def compile_lockvar(self, node):
        list = [self.compile(vval) for vval in node.list]
        if node.depth is NIL:
            self.out("(lockvar %s)", viml_join(list, " "))
        else:
            self.out("(lockvar %s %s)", node.depth, viml_join(list, " "))

    def compile_unlockvar(self, node):
        list = [self.compile(vval) for vval in node.list]
        if node.depth is NIL:
            self.out("(unlockvar %s)", viml_join(list, " "))
        else:
            self.out("(unlockvar %s %s)", node.depth, viml_join(list, " "))

    def compile_if(self, node):
        self.out("(if %s", self.compile(node.cond))
        self.incindent("  ")
        self.compile_body(node.body)
        self.decindent()
        for enode in node.elseif:
            self.out(" elseif %s", self.compile(enode.cond))
            self.incindent("  ")
            self.compile_body(enode.body)
            self.decindent()
        if node.else_ is not NIL:
            self.out(" else")
            self.incindent("  ")
            self.compile_body(node.else_.body)
            self.decindent()
        self.incindent("  ")
        self.out(")")
        self.decindent()

    def compile_while(self, node):
        self.out("(while %s", self.compile(node.cond))
        self.incindent("  ")
        self.compile_body(node.body)
        self.out(")")
        self.decindent()

    def compile_for(self, node):
        left = ""
        if node.left is not NIL:
            left = self.compile(node.left)
        else:
            left = viml_join([self.compile(vval) for vval in node.list], " ")
            if node.rest is not NIL:
                left += " . " + self.compile(node.rest)
            left = "(" + left + ")"
        right = self.compile(node.right)
        self.out("(for %s %s", left, right)
        self.incindent("  ")
        self.compile_body(node.body)
        self.out(")")
        self.decindent()

    def compile_continue(self, node):
        self.out("(continue)")

    def compile_break(self, node):
        self.out("(break)")

    def compile_try(self, node):
        self.out("(try")
        self.incindent("  ")
        self.compile_body(node.body)
        for cnode in node.catch:
            if cnode.pattern is not NIL:
                self.decindent()
                self.out(" catch /%s/", cnode.pattern)
                self.incindent("  ")
                self.compile_body(cnode.body)
            else:
                self.decindent()
                self.out(" catch")
                self.incindent("  ")
                self.compile_body(cnode.body)
        if node.finally_ is not NIL:
            self.decindent()
            self.out(" finally")
            self.incindent("  ")
            self.compile_body(node.finally_.body)
        self.out(")")
        self.decindent()

    def compile_throw(self, node):
        self.out("(throw %s)", self.compile(node.left))

    def compile_echo(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(echo %s)", viml_join(list, " "))

    def compile_echon(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(echon %s)", viml_join(list, " "))

    def compile_echohl(self, node):
        self.out("(echohl \"%s\")", viml_escape(node.str, "\\\""))

    def compile_echomsg(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(echomsg %s)", viml_join(list, " "))

    def compile_echoerr(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(echoerr %s)", viml_join(list, " "))

    def compile_execute(self, node):
        list = [self.compile(vval) for vval in node.list]
        self.out("(execute %s)", viml_join(list, " "))

    def compile_ternary(self, node):
        return viml_printf("(?: %s %s %s)", self.compile(node.cond), self.compile(node.left), self.compile(node.right))

    def compile_or(self, node):
        return viml_printf("(|| %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_and(self, node):
        return viml_printf("(&& %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_equal(self, node):
        return viml_printf("(== %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_equalci(self, node):
        return viml_printf("(==? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_equalcs(self, node):
        return viml_printf("(==# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nequal(self, node):
        return viml_printf("(!= %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nequalci(self, node):
        return viml_printf("(!=? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nequalcs(self, node):
        return viml_printf("(!=# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_greater(self, node):
        return viml_printf("(> %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_greaterci(self, node):
        return viml_printf("(>? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_greatercs(self, node):
        return viml_printf("(># %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_gequal(self, node):
        return viml_printf("(>= %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_gequalci(self, node):
        return viml_printf("(>=? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_gequalcs(self, node):
        return viml_printf("(>=# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_smaller(self, node):
        return viml_printf("(< %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_smallerci(self, node):
        return viml_printf("(<? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_smallercs(self, node):
        return viml_printf("(<# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_sequal(self, node):
        return viml_printf("(<= %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_sequalci(self, node):
        return viml_printf("(<=? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_sequalcs(self, node):
        return viml_printf("(<=# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_match(self, node):
        return viml_printf("(=~ %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_matchci(self, node):
        return viml_printf("(=~? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_matchcs(self, node):
        return viml_printf("(=~# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nomatch(self, node):
        return viml_printf("(!~ %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nomatchci(self, node):
        return viml_printf("(!~? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_nomatchcs(self, node):
        return viml_printf("(!~# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_is(self, node):
        return viml_printf("(is %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_isci(self, node):
        return viml_printf("(is? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_iscs(self, node):
        return viml_printf("(is# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_isnot(self, node):
        return viml_printf("(isnot %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_isnotci(self, node):
        return viml_printf("(isnot? %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_isnotcs(self, node):
        return viml_printf("(isnot# %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_add(self, node):
        return viml_printf("(+ %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_subtract(self, node):
        return viml_printf("(- %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_concat(self, node):
        return viml_printf("(concat %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_multiply(self, node):
        return viml_printf("(* %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_divide(self, node):
        return viml_printf("(/ %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_remainder(self, node):
        return viml_printf("(%% %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_not(self, node):
        return viml_printf("(! %s)", self.compile(node.left))

    def compile_plus(self, node):
        return viml_printf("(+ %s)", self.compile(node.left))

    def compile_minus(self, node):
        return viml_printf("(- %s)", self.compile(node.left))

    def compile_subscript(self, node):
        return viml_printf("(subscript %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_slice(self, node):
        r0 = "nil" if node.rlist[0] is NIL else self.compile(node.rlist[0])
        r1 = "nil" if node.rlist[1] is NIL else self.compile(node.rlist[1])
        return viml_printf("(slice %s %s %s)", self.compile(node.left), r0, r1)

    def compile_dot(self, node):
        return viml_printf("(dot %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_method(self, node):
        return viml_printf("(method %s %s)", self.compile(node.left), self.compile(node.right))

    def compile_call(self, node):
        rlist = [self.compile(vval) for vval in node.rlist]
        if viml_empty(rlist):
            return viml_printf("(%s)", self.compile(node.left))
        else:
            return viml_printf("(%s %s)", self.compile(node.left), viml_join(rlist, " "))

    def compile_number(self, node):
        return node.value

    def compile_blob(self, node):
        return node.value

    def compile_string(self, node):
        return node.value

    def compile_list(self, node):
        value = [self.compile(vval) for vval in node.value]
        if viml_empty(value):
            return "(list)"
        else:
            return viml_printf("(list %s)", viml_join(value, " "))

    def compile_dict(self, node):
        value = ["(" + self.compile(vval[0]) + " " + self.compile(vval[1]) + ")" for vval in node.value]
        if viml_empty(value):
            return "(dict)"
        else:
            return viml_printf("(dict %s)", viml_join(value, " "))

    def compile_option(self, node):
        return node.value

    def compile_identifier(self, node):
        return node.value

    def compile_curlyname(self, node):
        return viml_join([self.compile(vval) for vval in node.value], "")

    def compile_env(self, node):
        return node.value

    def compile_reg(self, node):
        return node.value

    def compile_curlynamepart(self, node):
        return node.value

    def compile_curlynameexpr(self, node):
        return "{" + self.compile(node.value) + "}"

    def escape_string(self, str):
        m = AttributeDict({"\n": "\\n", "\t": "\\t", "\r": "\\r"})
        out = "\""
        for i in viml_range(viml_len(str)):
            c = str[i]
            if viml_has_key(m, c):
                out += m[c]
            else:
                out += c
        out += "\""
        return out

    def compile_lambda(self, node):
        rlist = [self.compile(vval) for vval in node.rlist]
        return viml_printf("(lambda (%s) %s)", viml_join(rlist, " "), self.compile(node.left))

    def compile_heredoc(self, node):
        if viml_empty(node.rlist):
            rlist = "(list)"
        else:
            rlist = "(list " + viml_join([self.escape_string(vval) for vval in node.rlist], " ") + ")"
        if viml_empty(node.body):
            body = "(list)"
        else:
            body = "(list " + viml_join([self.escape_string(vval) for vval in node.body], " ") + ")"
        op = self.escape_string(node.op)
        return viml_printf("(heredoc %s %s %s)", rlist, op, body)


# TODO: under construction
class RegexpParser:
    RE_VERY_NOMAGIC = 1
    RE_NOMAGIC = 2
    RE_MAGIC = 3
    RE_VERY_MAGIC = 4

    def __init__(self, reader, cmd, delim):
        self.reader = reader
        self.cmd = cmd
        self.delim = delim
        self.reg_magic = self.RE_MAGIC

    def isend(self, c):
        return c == "<EOF>" or c == "<EOL>" or c == self.delim

    def parse_regexp(self):
        prevtoken = ""
        ntoken = ""
        ret = []
        if self.reader.peekn(4) == "\\%#=":
            epos = self.reader.getpos()
            token = self.reader.getn(5)
            if token != "\\%#=0" and token != "\\%#=1" and token != "\\%#=2":
                raise VimLParserException(Err("E864: \\%#= can only be followed by 0, 1, or 2", epos))
            viml_add(ret, token)
        while not self.isend(self.reader.peek()):
            prevtoken = ntoken
            token, ntoken = self.get_token()
            if ntoken == "\\m":
                self.reg_magic = self.RE_MAGIC
            elif ntoken == "\\M":
                self.reg_magic = self.RE_NOMAGIC
            elif ntoken == "\\v":
                self.reg_magic = self.RE_VERY_MAGIC
            elif ntoken == "\\V":
                self.reg_magic = self.RE_VERY_NOMAGIC
            elif ntoken == "\\*":
                # '*' is not magic as the very first character.
                if prevtoken == "" or prevtoken == "\\^" or prevtoken == "\\&" or prevtoken == "\\|" or prevtoken == "\\(":
                    ntoken = "*"
            elif ntoken == "\\^":
                # '^' is only magic as the very first character.
                if self.reg_magic != self.RE_VERY_MAGIC and prevtoken != "" and prevtoken != "\\&" and prevtoken != "\\|" and prevtoken != "\\n" and prevtoken != "\\(" and prevtoken != "\\%(":
                    ntoken = "^"
            elif ntoken == "\\$":
                # '$' is only magic as the very last character
                pos = self.reader.tell()
                if self.reg_magic != self.RE_VERY_MAGIC:
                    while not self.isend(self.reader.peek()):
                        t, n = self.get_token()
                        # XXX: Vim doesn't check \v and \V?
                        if n == "\\c" or n == "\\C" or n == "\\m" or n == "\\M" or n == "\\Z":
                            continue
                        if n != "\\|" and n != "\\&" and n != "\\n" and n != "\\)":
                            ntoken = "$"
                        break
                self.reader.seek_set(pos)
            elif ntoken == "\\?":
                # '?' is literal in '?' command.
                if self.cmd == "?":
                    ntoken = "?"
            viml_add(ret, ntoken)
        return ret

    # @return [actual_token, normalized_token]
    def get_token(self):
        if self.reg_magic == self.RE_VERY_MAGIC:
            return self.get_token_very_magic()
        elif self.reg_magic == self.RE_MAGIC:
            return self.get_token_magic()
        elif self.reg_magic == self.RE_NOMAGIC:
            return self.get_token_nomagic()
        elif self.reg_magic == self.RE_VERY_NOMAGIC:
            return self.get_token_very_nomagic()

    def get_token_very_magic(self):
        if self.isend(self.reader.peek()):
            return ["<END>", "<END>"]
        c = self.reader.get()
        if c == "\\":
            return self.get_token_backslash_common()
        elif c == "*":
            return ["*", "\\*"]
        elif c == "+":
            return ["+", "\\+"]
        elif c == "=":
            return ["=", "\\="]
        elif c == "?":
            return ["?", "\\?"]
        elif c == "{":
            return self.get_token_brace("{")
        elif c == "@":
            return self.get_token_at("@")
        elif c == "^":
            return ["^", "\\^"]
        elif c == "$":
            return ["$", "\\$"]
        elif c == ".":
            return [".", "\\."]
        elif c == "<":
            return ["<", "\\<"]
        elif c == ">":
            return [">", "\\>"]
        elif c == "%":
            return self.get_token_percent("%")
        elif c == "[":
            return self.get_token_sq("[")
        elif c == "~":
            return ["~", "\\~"]
        elif c == "|":
            return ["|", "\\|"]
        elif c == "&":
            return ["&", "\\&"]
        elif c == "(":
            return ["(", "\\("]
        elif c == ")":
            return [")", "\\)"]
        return [c, c]

    def get_token_magic(self):
        if self.isend(self.reader.peek()):
            return ["<END>", "<END>"]
        c = self.reader.get()
        if c == "\\":
            pos = self.reader.tell()
            c = self.reader.get()
            if c == "+":
                return ["\\+", "\\+"]
            elif c == "=":
                return ["\\=", "\\="]
            elif c == "?":
                return ["\\?", "\\?"]
            elif c == "{":
                return self.get_token_brace("\\{")
            elif c == "@":
                return self.get_token_at("\\@")
            elif c == "<":
                return ["\\<", "\\<"]
            elif c == ">":
                return ["\\>", "\\>"]
            elif c == "%":
                return self.get_token_percent("\\%")
            elif c == "|":
                return ["\\|", "\\|"]
            elif c == "&":
                return ["\\&", "\\&"]
            elif c == "(":
                return ["\\(", "\\("]
            elif c == ")":
                return ["\\)", "\\)"]
            self.reader.seek_set(pos)
            return self.get_token_backslash_common()
        elif c == "*":
            return ["*", "\\*"]
        elif c == "^":
            return ["^", "\\^"]
        elif c == "$":
            return ["$", "\\$"]
        elif c == ".":
            return [".", "\\."]
        elif c == "[":
            return self.get_token_sq("[")
        elif c == "~":
            return ["~", "\\~"]
        return [c, c]

    def get_token_nomagic(self):
        if self.isend(self.reader.peek()):
            return ["<END>", "<END>"]
        c = self.reader.get()
        if c == "\\":
            pos = self.reader.tell()
            c = self.reader.get()
            if c == "*":
                return ["\\*", "\\*"]
            elif c == "+":
                return ["\\+", "\\+"]
            elif c == "=":
                return ["\\=", "\\="]
            elif c == "?":
                return ["\\?", "\\?"]
            elif c == "{":
                return self.get_token_brace("\\{")
            elif c == "@":
                return self.get_token_at("\\@")
            elif c == ".":
                return ["\\.", "\\."]
            elif c == "<":
                return ["\\<", "\\<"]
            elif c == ">":
                return ["\\>", "\\>"]
            elif c == "%":
                return self.get_token_percent("\\%")
            elif c == "~":
                return ["\\~", "\\^"]
            elif c == "[":
                return self.get_token_sq("\\[")
            elif c == "|":
                return ["\\|", "\\|"]
            elif c == "&":
                return ["\\&", "\\&"]
            elif c == "(":
                return ["\\(", "\\("]
            elif c == ")":
                return ["\\)", "\\)"]
            self.reader.seek_set(pos)
            return self.get_token_backslash_common()
        elif c == "^":
            return ["^", "\\^"]
        elif c == "$":
            return ["$", "\\$"]
        return [c, c]

    def get_token_very_nomagic(self):
        if self.isend(self.reader.peek()):
            return ["<END>", "<END>"]
        c = self.reader.get()
        if c == "\\":
            pos = self.reader.tell()
            c = self.reader.get()
            if c == "*":
                return ["\\*", "\\*"]
            elif c == "+":
                return ["\\+", "\\+"]
            elif c == "=":
                return ["\\=", "\\="]
            elif c == "?":
                return ["\\?", "\\?"]
            elif c == "{":
                return self.get_token_brace("\\{")
            elif c == "@":
                return self.get_token_at("\\@")
            elif c == "^":
                return ["\\^", "\\^"]
            elif c == "$":
                return ["\\$", "\\$"]
            elif c == "<":
                return ["\\<", "\\<"]
            elif c == ">":
                return ["\\>", "\\>"]
            elif c == "%":
                return self.get_token_percent("\\%")
            elif c == "~":
                return ["\\~", "\\~"]
            elif c == "[":
                return self.get_token_sq("\\[")
            elif c == "|":
                return ["\\|", "\\|"]
            elif c == "&":
                return ["\\&", "\\&"]
            elif c == "(":
                return ["\\(", "\\("]
            elif c == ")":
                return ["\\)", "\\)"]
            self.reader.seek_set(pos)
            return self.get_token_backslash_common()
        return [c, c]

    def get_token_backslash_common(self):
        cclass = "iIkKfFpPsSdDxXoOwWhHaAlLuU"
        c = self.reader.get()
        if c == "\\":
            return ["\\\\", "\\\\"]
        elif viml_stridx(cclass, c) != -1:
            return ["\\" + c, "\\" + c]
        elif c == "_":
            epos = self.reader.getpos()
            c = self.reader.get()
            if viml_stridx(cclass, c) != -1:
                return ["\\_" + c, "\\_ . c"]
            elif c == "^":
                return ["\\_^", "\\_^"]
            elif c == "$":
                return ["\\_$", "\\_$"]
            elif c == ".":
                return ["\\_.", "\\_."]
            elif c == "[":
                return self.get_token_sq("\\_[")
            raise VimLParserException(Err("E63: invalid use of \\_", epos))
        elif viml_stridx("etrb", c) != -1:
            return ["\\" + c, "\\" + c]
        elif viml_stridx("123456789", c) != -1:
            return ["\\" + c, "\\" + c]
        elif c == "z":
            epos = self.reader.getpos()
            c = self.reader.get()
            if viml_stridx("123456789", c) != -1:
                return ["\\z" + c, "\\z" + c]
            elif c == "s":
                return ["\\zs", "\\zs"]
            elif c == "e":
                return ["\\ze", "\\ze"]
            elif c == "(":
                return ["\\z(", "\\z("]
            raise VimLParserException(Err("E68: Invalid character after \\z", epos))
        elif viml_stridx("cCmMvVZ", c) != -1:
            return ["\\" + c, "\\" + c]
        elif c == "%":
            epos = self.reader.getpos()
            c = self.reader.get()
            if c == "d":
                r = self.getdecchrs()
                if r != "":
                    return ["\\%d" + r, "\\%d" + r]
            elif c == "o":
                r = self.getoctchrs()
                if r != "":
                    return ["\\%o" + r, "\\%o" + r]
            elif c == "x":
                r = self.gethexchrs(2)
                if r != "":
                    return ["\\%x" + r, "\\%x" + r]
            elif c == "u":
                r = self.gethexchrs(4)
                if r != "":
                    return ["\\%u" + r, "\\%u" + r]
            elif c == "U":
                r = self.gethexchrs(8)
                if r != "":
                    return ["\\%U" + r, "\\%U" + r]
            raise VimLParserException(Err("E678: Invalid character after \\%[dxouU]", epos))
        return ["\\" + c, c]

    # \{}
    def get_token_brace(self, pre):
        r = ""
        minus = ""
        comma = ""
        n = ""
        m = ""
        if self.reader.p(0) == "-":
            minus = self.reader.get()
            r += minus
        if isdigit(self.reader.p(0)):
            n = self.reader.read_digit()
            r += n
        if self.reader.p(0) == ",":
            comma = self.rader.get()
            r += comma
        if isdigit(self.reader.p(0)):
            m = self.reader.read_digit()
            r += m
        if self.reader.p(0) == "\\":
            r += self.reader.get()
        if self.reader.p(0) != "}":
            raise VimLParserException(Err("E554: Syntax error in \\{...}", self.reader.getpos()))
        self.reader.get()
        return [pre + r, "\\{" + minus + n + comma + m + "}"]

    # \[]
    def get_token_sq(self, pre):
        start = self.reader.tell()
        r = ""
        # Complement of range
        if self.reader.p(0) == "^":
            r += self.reader.get()
        # At the start ']' and '-' mean the literal character.
        if self.reader.p(0) == "]" or self.reader.p(0) == "-":
            r += self.reader.get()
        while TRUE:
            startc = 0
            c = self.reader.p(0)
            if self.isend(c):
                # If there is no matching ']', we assume the '[' is a normal character.
                self.reader.seek_set(start)
                return [pre, "["]
            elif c == "]":
                self.reader.seek_cur(1)
                return [pre + r + "]", "\\[" + r + "]"]
            elif c == "[":
                e = self.get_token_sq_char_class()
                if e == "":
                    e = self.get_token_sq_equi_class()
                    if e == "":
                        e = self.get_token_sq_coll_element()
                        if e == "":
                            e, startc = self.get_token_sq_c()
                r += e
            else:
                e, startc = self.get_token_sq_c()
                r += e
            if startc != 0 and self.reader.p(0) == "-" and not self.isend(self.reader.p(1)) and not (self.reader.p(1) == "\\" and self.reader.p(2) == "n"):
                self.reader.seek_cur(1)
                r += "-"
                c = self.reader.p(0)
                if c == "[":
                    e = self.get_token_sq_coll_element()
                    if e != "":
                        endc = viml_char2nr(e[2])
                    else:
                        e, endc = self.get_token_sq_c()
                    r += e
                else:
                    e, endc = self.get_token_sq_c()
                    r += e
                if startc > endc or endc > startc + 256:
                    raise VimLParserException(Err("E16: Invalid range", self.reader.getpos()))

    # [c]
    def get_token_sq_c(self):
        c = self.reader.p(0)
        if c == "\\":
            self.reader.seek_cur(1)
            c = self.reader.p(0)
            if c == "n":
                self.reader.seek_cur(1)
                return ["\\n", 0]
            elif c == "r":
                self.reader.seek_cur(1)
                return ["\\r", 13]
            elif c == "t":
                self.reader.seek_cur(1)
                return ["\\t", 9]
            elif c == "e":
                self.reader.seek_cur(1)
                return ["\\e", 27]
            elif c == "b":
                self.reader.seek_cur(1)
                return ["\\b", 8]
            elif viml_stridx("]^-\\", c) != -1:
                self.reader.seek_cur(1)
                return ["\\" + c, viml_char2nr(c)]
            elif viml_stridx("doxuU", c) != -1:
                c, n = self.get_token_sq_coll_char()
                return [c, n]
            else:
                return ["\\", viml_char2nr("\\")]
        elif c == "-":
            self.reader.seek_cur(1)
            return ["-", viml_char2nr("-")]
        else:
            self.reader.seek_cur(1)
            return [c, viml_char2nr(c)]

    # [\d123]
    def get_token_sq_coll_char(self):
        pos = self.reader.tell()
        c = self.reader.get()
        if c == "d":
            r = self.getdecchrs()
            n = viml_str2nr(r, 10)
        elif c == "o":
            r = self.getoctchrs()
            n = viml_str2nr(r, 8)
        elif c == "x":
            r = self.gethexchrs(2)
            n = viml_str2nr(r, 16)
        elif c == "u":
            r = self.gethexchrs(4)
            n = viml_str2nr(r, 16)
        elif c == "U":
            r = self.gethexchrs(8)
            n = viml_str2nr(r, 16)
        else:
            r = ""
        if r == "":
            self.reader.seek_set(pos)
            return "\\"
        return ["\\" + c + r, n]

    # [[.a.]]
    def get_token_sq_coll_element(self):
        if self.reader.p(0) == "[" and self.reader.p(1) == "." and not self.isend(self.reader.p(2)) and self.reader.p(3) == "." and self.reader.p(4) == "]":
            return self.reader.getn(5)
        return ""

    # [[=a=]]
    def get_token_sq_equi_class(self):
        if self.reader.p(0) == "[" and self.reader.p(1) == "=" and not self.isend(self.reader.p(2)) and self.reader.p(3) == "=" and self.reader.p(4) == "]":
            return self.reader.getn(5)
        return ""

    # [[:alpha:]]
    def get_token_sq_char_class(self):
        class_names = ["alnum", "alpha", "blank", "cntrl", "digit", "graph", "lower", "print", "punct", "space", "upper", "xdigit", "tab", "return", "backspace", "escape"]
        pos = self.reader.tell()
        if self.reader.p(0) == "[" and self.reader.p(1) == ":":
            self.reader.seek_cur(2)
            r = self.reader.read_alpha()
            if self.reader.p(0) == ":" and self.reader.p(1) == "]":
                self.reader.seek_cur(2)
                for name in class_names:
                    if r == name:
                        return "[:" + name + ":]"
        self.reader.seek_set(pos)
        return ""

    # \@...
    def get_token_at(self, pre):
        epos = self.reader.getpos()
        c = self.reader.get()
        if c == ">":
            return [pre + ">", "\\@>"]
        elif c == "=":
            return [pre + "=", "\\@="]
        elif c == "!":
            return [pre + "!", "\\@!"]
        elif c == "<":
            c = self.reader.get()
            if c == "=":
                return [pre + "<=", "\\@<="]
            elif c == "!":
                return [pre + "<!", "\\@<!"]
        raise VimLParserException(Err("E64: @ follows nothing", epos))

    # \%...
    def get_token_percent(self, pre):
        c = self.reader.get()
        if c == "^":
            return [pre + "^", "\\%^"]
        elif c == "$":
            return [pre + "$", "\\%$"]
        elif c == "V":
            return [pre + "V", "\\%V"]
        elif c == "#":
            return [pre + "#", "\\%#"]
        elif c == "[":
            return self.get_token_percent_sq(pre + "[")
        elif c == "(":
            return [pre + "(", "\\%("]
        else:
            return self.get_token_mlcv(pre)

    # \%[]
    def get_token_percent_sq(self, pre):
        r = ""
        while TRUE:
            c = self.reader.peek()
            if self.isend(c):
                raise VimLParserException(Err("E69: Missing ] after \\%[", self.reader.getpos()))
            elif c == "]":
                if r == "":
                    raise VimLParserException(Err("E70: Empty \\%[", self.reader.getpos()))
                self.reader.seek_cur(1)
                break
            self.reader.seek_cur(1)
            r += c
        return [pre + r + "]", "\\%[" + r + "]"]

    # \%'m \%l \%c \%v
    def get_token_mlvc(self, pre):
        r = ""
        cmp = ""
        if self.reader.p(0) == "<" or self.reader.p(0) == ">":
            cmp = self.reader.get()
            r += cmp
        if self.reader.p(0) == "'":
            r += self.reader.get()
            c = self.reader.p(0)
            if self.isend(c):
                # FIXME: Should be error?  Vim allow this.
                c = ""
            else:
                c = self.reader.get()
            return [pre + r + c, "\\%" + cmp + "'" + c]
        elif isdigit(self.reader.p(0)):
            d = self.reader.read_digit()
            r += d
            c = self.reader.p(0)
            if c == "l":
                self.reader.get()
                return [pre + r + "l", "\\%" + cmp + d + "l"]
            elif c == "c":
                self.reader.get()
                return [pre + r + "c", "\\%" + cmp + d + "c"]
            elif c == "v":
                self.reader.get()
                return [pre + r + "v", "\\%" + cmp + d + "v"]
        raise VimLParserException(Err("E71: Invalid character after %", self.reader.getpos()))

    def getdecchrs(self):
        return self.reader.read_digit()

    def getoctchrs(self):
        return self.reader.read_odigit()

    def gethexchrs(self, n):
        r = ""
        for i in viml_range(n):
            c = self.reader.peek()
            if not isxdigit(c):
                break
            r += self.reader.get()
        return r


if __name__ == '__main__':
    main()
