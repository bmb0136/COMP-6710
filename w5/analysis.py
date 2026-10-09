import ast
import json

class Tracer:
    events: list
    _values: dict[str, any]

    def __init__(self):
        self.events = []
        self._values = {}

    def append_assignment(self, name, value):
        if value == self._values.get(name, None):
            return
        self._values[name] = value
        self.events.append({ "kind": "assignment", "name": name, "value": value })

    def append_branch(self, condition, result):
        self.events.append({ "kind": "branch", "condition": condition, "result": result })

def format_trace_value(node):
    match node:
        case AssignmentNode():
            return node.name
        case VariableNode():
            return node.name
        case ConstantNode():
            return f"{node.value!r}"
        case BinaryOpNode():
            return f"{format_trace_value(node.left)} {node.op} {format_trace_value(node.right)}"
        case NotNode():
            return f"not (format_trace_value({node.value}))"

    return node

class DFANode:
    def to_json(self):
        raise NotImplemented("TODO")

    def fold(self, trace):
        raise NotImplemented("TODO")

class ConstantNode(DFANode):
    value: any

    def __init__(self, value):
        self.value = value

    def to_json(self):
        return {
            "$type": "Constant",
            "$id": id(self),
            "value": self.value
        }

    def fold(self, trace):
        return self

class VariableNode(DFANode):
    name: str
    value: DFANode

    def __init__(self, name, value):
        assert isinstance(name, str)
        assert isinstance(value, DFANode)
        self.name, self.value = name, value

    def to_json(self):
        return {
            "$type": "Variable",
            "$id": id(self),
            "name": self.name,
            "value": self.value.to_json()
        }

    def fold(self, trace):
        return self.value.fold(trace)

class AssignmentNode(DFANode):
    name: str
    value: DFANode
    prev: DFANode | None

    def __init__(self, name, value, prev=None):
        assert isinstance(name, str)
        assert isinstance(value, DFANode)
        assert prev is None or isinstance(prev, DFANode)
        self.name, self.value, self.prev = name, value, prev

    def to_json(self):
        return {
            "$type": "Assignment",
            "$id": id(self),
            "name": self.name,
            "value": self.value.to_json(),
            "prev": self.prev.to_json() if self.prev is not None else None
        }

    def fold(self, trace):
        v = self.value.fold(trace)
        trace.append_assignment(self.name, format_trace_value(self.value))
        return v

class BinaryOpNode(DFANode):
    left: DFANode
    op: str
    right: DFANode
    prev: DFANode | None

    def __init__(self, left, op, right, prev):
        assert isinstance(left, DFANode)
        assert isinstance(op, str)
        assert isinstance(right, DFANode)
        assert prev is None or isinstance(prev, DFANode)
        self.left, self.op, self.right, self.prev = left, op, right, prev

    def to_json(self):
        return {
            "$type": "BinaryOp",
            "$id": id(self),
            "left": self.left.to_json(),
            "op": self.op,
            "right": self.right.to_json(),
            "prev": self.prev.to_json() if self.prev is not None else None
        }

    def fold(self, trace):
        l = self.left.fold(trace)
        r = self.right.fold(trace)
        if not isinstance(l, ConstantNode) or not isinstance(r, ConstantNode):
            return BinaryOpNode(l, self.op, r, self.prev.fold(trace))
        match self.op:
            case "+":
                return ConstantNode(l.value + r.value)
            case "/":
                return ConstantNode(l.value / r.value)
            case "==":
                return ConstantNode(l.value == r.value)
            case ">":
                return ConstantNode(l.value > r.value)
            case _:
                return BinaryOpNode(l, self.op, r, self.prev.fold(trace))

class NotNode(DFANode):
    value: DFANode

    def __init__(self, value):
        assert isinstance(value, DFANode)
        self.value = value

    def to_json(self):
        return {
            "$type": "Not",
            "$id": id(self),
            "value": self.value.to_json()
        }

    def fold(self, trace):
        v = self.value.fold(trace)
        if isinstance(v, ConstantNode):
            return ConstantNode(not v.value)
        return NotNode(v)

class IfElseNode(DFANode):
    condition: DFANode
    if_true: DFANode
    if_false: DFANode | None
    prev: DFANode | None

    def __init__(self, condition, if_true, if_false, prev):
        assert isinstance(condition, DFANode)
        assert isinstance(if_true, DFANode)
        assert if_false is None or isinstance(if_false, DFANode)
        assert prev is None or isinstance(prev, DFANode)
        self.condition, self.if_true, self.if_false, self.prev = condition, if_true, if_false, prev

    def to_json(self):
        return {
            "$type": "IfElse",
            "$id": id(self),
            "condition": self.condition.to_json(),
            "if_true": self.if_true.to_json(),
            "if_false": self.if_false.to_json() if self.if_false is not None else None,
            "prev": self.prev.to_json() if self.prev is not None else None
        }

    def fold(self, trace):
        c = self.condition.fold(trace)
        if isinstance(c, ConstantNode):
            if c.value:
                trace.append_branch(format_trace_value(self.condition), True)
                v = self.if_true.fold(trace)
                return v
            else:
                trace.append_branch(format_trace_value(self.condition), False)
                v = self.if_false.fold(trace)
                return v
        trace.append_branch(format_trace_value(self.condition), None)
        return IfElseNode(c, self.if_true, self.if_false, self.prev)


def extract_parse_tree(file_path):
    with open(file_path) as f:
        code = f.read()
    return ast.parse(code)

def flatten_assignment(a):
    if isinstance(a.targets[0], ast.Tuple):
        for i, e in enumerate(a.targets[0].elts):
            yield e.id, a.value.elts[i]
        return
    yield a.targets[0].id, a.value

def op_to_str(op):
    match op:
        case ast.Add():
            return "+"
        case ast.Div():
            return "/"
        case ast.Eq():
            return "=="
        case ast.Gt():
            return ">"
        case _:
            raise ValueError(f"Unknown op: {ast.dump(op)}")

def process_expr(node, vars):
    if isinstance(node, ast.Constant):
        return ConstantNode(node.value)
    elif isinstance(node, ast.Name):
        return VariableNode(node.id, vars[node.id])
    elif isinstance(node, ast.BinOp):
        return BinaryOpNode(process_expr(node.left, vars), op_to_str(node.op), process_expr(node.right, vars), None)
    elif isinstance(node, ast.Compare):
        # NOTE: only supports basic `x op y` (e.g., not `x < y < z`)
        return BinaryOpNode(process_expr(node.left, vars), op_to_str(node.ops[0]), process_expr(node.comparators[0], vars), None)
    else:
        raise ValueError(f"Unknown expr kind: {ast.dump(node)}")

def process_assignment(child, vars, funcs):
    for name, val in flatten_assignment(child):
        old = vars.get(name, None)
        if isinstance(val, ast.Constant):
            vars[name] = AssignmentNode(name, ConstantNode(val.value), old)
        elif isinstance(val, ast.Call):
            if isinstance(val.func, ast.Name):
                f = funcs[val.func.id]
                new_vars = {} # bound args
                args = []
                for arg, expr in zip(f.args.args, val.args):
                    value = process_expr(expr, vars)
                    new_vars[arg.arg] = AssignmentNode(arg.arg, value, None)
                    args.append(value)

                ret = process_block(f, new_vars, funcs)

                vars[name] = AssignmentNode(name, ret or ConstantNode(None), vars.get(name, None))
            else:
                raise ValueError(f"Unknown call kind: {ast.dump(val.func)}")
        elif isinstance(val, ast.BinOp):
            vars[name] = AssignmentNode(name, BinaryOpNode(process_expr(val.left, vars), op_to_str(val.op), process_expr(val.right, vars), None), vars.get(name, None))
        else:
            raise ValueError(f"Unknown value type: {ast.dump(val)}")

def process_if(child, vars, funcs):
    condition = process_expr(child.test, vars)

    vars_true = {k: v for k, v in vars.items()}
    process_block(child, vars_true, funcs)

    if child.orelse:
        vars_false = {k: v for k, v in vars.items()}
        process_block(child.orelse, vars_false, funcs)

        keys_true = set(vars_true.keys())
        keys_false = set(vars_false.keys())

        # Changed by both branches
        for k in (keys_true & keys_false):
            vars[k] = IfElseNode(condition, vars_true[k], vars_false[k], vars.get(k, None))

        # Changed by true branch only
        for k in (keys_true - keys_false):
            vars[k] = IfElseNode(condition, vars_true[k], vars.get(k, None), None)

        # Change by false branch only
        for k in (keys_false - keys_true):
            # Using NotNode to invert the condition
            vars[k] = IfElseNode(NotNode(condition), vars_false[k], vars.get(k, None), None)
    else:
        for k, v in vars_true.items():
            vars[k] = IfElseNode(condition, v, vars.get(k, None), None)

def process_block(node, vars, funcs):
    for child in (getattr(node, "body", None) or node):
        if isinstance(child, ast.Assign):
            process_assignment(child, vars, funcs)
        elif isinstance(child, ast.If):
            process_if(child, vars, funcs)
        elif isinstance(child, ast.Return):
            # NOTE: assumes that a return is the last statement of the function (fine for calc.py)
            return process_expr(child.value, vars)

if __name__ == '__main__':
    parse_tree = extract_parse_tree('./calc.py')

    funcs = {}
    main = None
    for node in parse_tree.body:
        if isinstance(node, ast.FunctionDef):
            funcs[node.name] = node
        # Look for `if __name__ == '__main__'` so we can start flow analysis there
        elif isinstance(node, ast.If):
            if not isinstance(c := node.test, ast.Compare):
                continue
            if not (isinstance(l := c.left, ast.Name) and l.id == '__name__'):
                continue
            if len(c.ops) != 1 or not isinstance(c.ops[0], ast.Eq):
                continue
            if not (len(c.comparators) == 1 and isinstance(r := c.comparators[0], ast.Constant) and r.value == '__main__'):
                continue
            main = node

    vars = {}
    process_block(main, vars, funcs)

    for k, v in vars.items():
        trace = Tracer()
        v.fold(trace)
        #print(json.dumps(data.to_json()))
        print(f"{k}")
        for e in trace.events:
            print(f"\t{e}")

