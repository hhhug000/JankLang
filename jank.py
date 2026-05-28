import sys

variables = {}
functions = {}


def call_function(name, arg_values):
    if name not in functions:
        return ""
    params, body_lines = functions[name]
    global variables
    backup_vars = variables
    # create local scope that starts with a copy of globals
    local_vars = backup_vars.copy()
    # bind parameters
    for i, p in enumerate(params):
        if i < len(arg_values):
            local_vars[p] = arg_values[i]
        else:
            local_vars[p] = ""

    variables = local_vars
    ret = ""
    for line in body_lines:
        runline(line)
        if '_return' in variables:
            ret = variables.pop('_return')
            break

    # restore globals
    variables = backup_vars
    return ret


def expression(exprString):
    exprString = exprString.strip()
    
    openBracket = exprString.find("(")
    if openBracket != -1:
        closeBracket = exprString.find(")")
        beforeBracket = exprString[:openBracket]
        insideBracket = exprString[openBracket + 1:closeBracket]
        afterBracket = exprString[closeBracket + 1:]
        beforeBracket = beforeBracket.strip()

        if beforeBracket == "tonumber":
            innerValue = expression(insideBracket)
            try:
                if '.' in str(innerValue):
                    result = float(innerValue)
                else:
                    result = int(innerValue)
            except (ValueError, TypeError):
                result = 0
            bracketResult = str(result)
            newExprString = bracketResult + afterBracket
        elif beforeBracket == "readfile":
            inner = expression(insideBracket)
            try:
                with open(str(inner), 'r', encoding='utf-8') as _f:
                    data = _f.read()
            except Exception:
                data = ""
            bracketResult = data
            newExprString = bracketResult + afterBracket
        else:
            # function call support
            if beforeBracket in functions:
                # split args, evaluate each, call function
                def split_args(s):
                    args = []
                    cur = ""
                    depth = 0
                    in_str = False
                    i = 0
                    while i < len(s):
                        c = s[i]
                        if c == '"':
                            in_str = not in_str
                            cur += c
                        elif not in_str:
                            if c == '(':
                                depth += 1
                                cur += c
                            elif c == ')':
                                depth -= 1
                                cur += c
                            elif c == ',' and depth == 0:
                                args.append(cur)
                                cur = ""
                            else:
                                cur += c
                        else:
                            cur += c
                        i += 1
                    if cur.strip() != "":
                        args.append(cur)
                    return args

                arg_strs = split_args(insideBracket)
                evaluated_args = [expression(a.strip()) for a in arg_strs if a.strip() != ""]
                # call the function
                bracketResult = call_function(beforeBracket, evaluated_args)
                newExprString = str(bracketResult) + afterBracket
            else:
                bracketResult = expression(insideBracket)
                newExprString = beforeBracket + bracketResult + afterBracket
        
        exprString = newExprString.strip()
        
        if "(" in exprString:
            return expression(exprString)
    
    splitParts = exprString.split("+")
    parts = []
    for part in splitParts:
        strippedPart = part.strip()
        parts.append(strippedPart)
    values = []
    for part in parts:
        firstChar = part[0]
        if firstChar == '"':
            value = part[1:-1]
        else:
            try:
                float(part)
                if '.' in part:
                    value = float(part)
                else:
                    value = int(part)
            except ValueError:
                value = variables.get(part, "")
        values.append(value)
    isAllNumbers = True
    for v in values:
        if not isinstance(v, (int, float)):
            isAllNumbers = False
            break
    if isAllNumbers:
        result = sum(values)
    else:
        resultParts = []
        for v in values:
            resultParts.append(str(v))
        result = "".join(resultParts)
    finalResult = str(result)
    return finalResult


def condition(condString):
    condString = condString.strip()
    
    openBracket = condString.find("(")
    if openBracket != -1:
        closeBracket = condString.find(")")
        beforeBracket = condString[:openBracket]
        insideBracket = condString[openBracket + 1:closeBracket]
        afterBracket = condString[closeBracket + 1:]
        bracketResult = condition(insideBracket)
        if bracketResult:
            resultStr = "true"
        else:
            resultStr = "false"
        condString = (beforeBracket + resultStr + afterBracket).strip()
    
    operators = ["==", "!=", "<=", ">=", "<", ">"]
    
    for op in operators:
        if op in condString:
            split = condString.split(op, 1)
            leftExpr = split[0].strip()
            rightExpr = split[1].strip()
            
            leftVal = expression(leftExpr)
            rightVal = expression(rightExpr)
            
            try:
                leftNum = float(leftVal)
                rightNum = float(rightVal)
                leftVal = leftNum
                rightVal = rightNum
            except (ValueError, TypeError):
                pass
            
            if op == "==":
                return leftVal == rightVal
            elif op == "!=":
                return leftVal != rightVal
            elif op == "<":
                return leftVal < rightVal
            elif op == ">":
                return leftVal > rightVal
            elif op == "<=":
                return leftVal <= rightVal
            elif op == ">=":
                return leftVal >= rightVal
    
    return False


def file(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if line.strip().lower().startswith("if "):
            # collect full if/elif/else/.../endif group including inner nested ifs
            header = line.strip()
            i += 1
            blocks = []  # list of (cond_or_None, lines)
            current_cond = header[3:]
            current_block = []
            blocks.append((current_cond, current_block))
            nesting_depth = 1
            while i < len(lines) and nesting_depth > 0:
                current_line = lines[i]
                stripped = current_line.strip()
                low = stripped.lower()
                if low.startswith("if "):
                    nesting_depth += 1
                    current_block.append(current_line)
                elif low == "endif":
                    nesting_depth -= 1
                    if nesting_depth == 0:
                        i += 1
                        break
                    else:
                        current_block.append(current_line)
                elif low.startswith("elif ") and nesting_depth == 1:
                    # start new elif block
                    current_cond = current_line.strip()[5:]
                    current_block = []
                    blocks.append((current_cond, current_block))
                elif low == "else" and nesting_depth == 1:
                    current_cond = None
                    current_block = []
                    blocks.append((current_cond, current_block))
                else:
                    current_block.append(current_line)
                i += 1

            # evaluate blocks in order
            executed = False
            for cond, b_lines in blocks:
                if cond is None:
                    # else
                    file("\n".join(b_lines))
                    executed = True
                    break
                else:
                    if condition(cond):
                        file("\n".join(b_lines))
                        executed = True
                        break
            # if none matched, do nothing
        elif line.strip().lower().startswith("func "):
            header = line.strip()[5:]
            name = header
            params = []
            if "(" in header and ")" in header:
                pstart = header.find("(")
                pend = header.find(")")
                name = header[:pstart].strip()
                params = [p.strip() for p in header[pstart+1:pend].split(",") if p.strip() != ""]
            i += 1
            body_lines = []
            while i < len(lines):
                cur = lines[i]
                if cur.strip().lower() == "endfunc":
                    i += 1
                    break
                else:
                    body_lines.append(cur)
                i += 1
            functions[name] = (params, body_lines)
        elif line.strip().lower() == "endif":
            i += 1
        else:
            runline(line)
            i += 1
        
def repl():
    while True:
        try:
            line = input("jank> ")
            if line.strip().lower().startswith("if "):
                header = line.strip()
                block_lines = []
                nesting_depth = 1
                while nesting_depth > 0:
                    line = input("... ")
                    if line.strip().lower().startswith("if "):
                        nesting_depth += 1
                        block_lines.append(line)
                    elif line.strip().lower() == "endif":
                        nesting_depth -= 1
                        if nesting_depth > 0:
                            block_lines.append(line)
                    else:
                        block_lines.append(line)
                # reconstruct full conditional group and let file() handle elif/else
                full_text = header + "\n" + "\n".join(block_lines) + "\nendif"
                file(full_text)
            elif line.strip().lower().startswith("func "):
                header = line.strip()[5:]
                name = header
                params = []
                if "(" in header and ")" in header:
                    pstart = header.find("(")
                    pend = header.find(")")
                    name = header[:pstart].strip()
                    params = [p.strip() for p in header[pstart+1:pend].split(",") if p.strip() != ""]
                body_lines = []
                while True:
                    l = input("... ")
                    if l.strip().lower() == "endfunc":
                        break
                    body_lines.append(l)
                functions[name] = (params, body_lines)
            else:
                runline(line)
        except EOFError:
            break

def runline(line):
    line = line.strip()
    if line == "" or line[0] == "#":
        return
    parts = line.split(" ", 1)
    command = parts[0].lower()
    try:
        match command:
            case "output":
                expr = parts[1]
                result = expression(expr)
                print(result)
            case "set":
                expr = parts[1]
                split = expr.split("=", 1)
                varName = split[0].strip()
                valueExpr = split[1].strip()
                result = expression(valueExpr)
                variables[varName] = result
            case "input":
                expr = parts[1]
                split = expr.split("=", 1)
                varName = split[0].strip()
                valueExpr = split[1].strip()
                result = expression(valueExpr)
                inputValue = input(result)
                variables[varName] = inputValue
            case "write":
                expr = parts[1]
                split = expr.split("=", 1)
                if len(split) < 2:
                    print("Usage: write filename = expression")
                else:
                    filenameExpr = split[0].strip()
                    valueExpr = split[1].strip()
                    filename = expression(filenameExpr)
                    content = expression(valueExpr)
                    try:
                        with open(str(filename), 'w', encoding='utf-8') as _f:
                            _f.write(str(content))
                    except Exception as e:
                        print(f"Error writing file: {e}")
            case "append":
                expr = parts[1]
                split = expr.split("=", 1)
                if len(split) < 2:
                    print("Usage: append filename = expression")
                else:
                    filenameExpr = split[0].strip()
                    valueExpr = split[1].strip()
                    filename = expression(filenameExpr)
                    content = expression(valueExpr)
                    try:
                        with open(str(filename), 'a', encoding='utf-8') as _f:
                            _f.write(str(content))
                    except Exception as e:
                        print(f"Error appending file: {e}")
            case "read":
                expr = parts[1]
                # support: read filename as var  OR read filename var
                e_lower = expr.lower()
                if " as " in e_lower:
                    idx = e_lower.rfind(" as ")
                    filenamePart = expr[:idx]
                    varName = expr[idx+4:].strip()
                else:
                    parts2 = expr.rsplit(" ", 1)
                    if len(parts2) == 2:
                        filenamePart, varName = parts2[0], parts2[1]
                    else:
                        print("Usage: read filename as var")
                        filenamePart = None
                        varName = None
                if filenamePart and varName:
                    filename = expression(filenamePart.strip())
                    try:
                        with open(str(filename), 'r', encoding='utf-8') as _f:
                            data = _f.read()
                    except Exception as e:
                        data = ""
                        print(f"Error reading file: {e}")
                    variables[varName] = data
            case "return":
                if len(parts) > 1:
                    result = expression(parts[1])
                else:
                    result = ""
                variables['_return'] = result
                return
            case "exit":
                exit()
            case _:
                print(f"Unknown command: {command}")
                
    except Exception as e:
        print(f"Error processing line '{line}': {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                text = f.read()
                file(text)
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        repl()