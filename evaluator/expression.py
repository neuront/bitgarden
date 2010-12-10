class NodeBase:
    def evaluate(self):
        return 0

class Integer(NodeBase):
    def evaluate(self):
        return self.value

    def __init__(self, value):
        self.value = int(value)

    value = 0

PRE_UNARY_OP_MAP = {
    '+': lambda x: x,
    '-': lambda x: -x,
}

BINARY_OP_MAP = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    '^': lambda x, y: x ** y,
}

class PreUnaryOperation(NodeBase):
    def evaluate(self):
        return PRE_UNARY_OP_MAP[self.op](self.rhs.evaluate())

    def __init__(self, op, rhs):
        self.op = op
        self.rhs = rhs

    op = ''
    rhs = NodeBase()

class BinaryOperation(NodeBase):
    def evaluate(self):
        return BINARY_OP_MAP[self.op](self.lhs.evaluate(), self.rhs.evaluate())

    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    op = ''
    lhs = NodeBase()
    rhs = NodeBase()

class Token:
    def __init__(self, image, is_number, is_pre_unary_operator):
        self.image = image
        self.is_number = is_number
        self.is_pre_unary_operator = is_pre_unary_operator

    image = ''
    is_number = False
    is_pre_unary_operator = False

POS, NEG, ADD, SUB, MUL, DIV, POW, PAREN = range(0, 8)

PRE_UNARY_SIGN_OP_MAP = {
    '+': POS,
    '-': NEG,
    '(': PAREN,
}

BINARY_SIGN_OP_MAP = {
    '+': ADD,
    '-': SUB,
    '*': MUL,
    '/': DIV,
    '^': POW,
}

OP_PRIO_MATRIX = (
  #  Stack top:
  #  POS    NEG    ADD    SUB    MUL    DIV    POW    PAREN   # Encounters:
    (False, False, False, False, False, False, False, False), # POS
    (False, False, False, False, False, False, False, False), # NEG
    (True,  True,  True,  True,  True,  True,  False, False), # ADD
    (True,  True,  True,  True,  True,  True,  False, False), # SUB
    (True,  True,  False, False, True,  True,  True,  False), # MUL
    (True,  True,  False, False, True,  True,  True,  False), # DIV
    (True,  True,  False, False, False, False, False, False), # POW
    (False, False, False, False, False, False, False, False), # PAREN
)

class Operator:
    def reduce(self, expr_stack):
        pass

    def __init__(self, op_image, op_type):
        self.op_image = op_image
        self.op_type = op_type

    op_image = ''
    op_type = 0

class OpenParen(Operator):
    def __init__(self):
        Operator.__init__(self, '(', PAREN)

class PreUnaryOperator(Operator):
    def reduce(self, expr_stack):
        rhs = expr_stack.pop()
        return PreUnaryOperation(self.op_image, rhs)

    def __init__(self, op_image):
        Operator.__init__(self, op_image, PRE_UNARY_SIGN_OP_MAP[op_image])

class BinaryOperator(Operator):
    def reduce(self, expr_stack):
        rhs = expr_stack.pop()
        lhs = expr_stack.pop()
        return BinaryOperation(self.op_image, lhs, rhs)

    def __init__(self, op_image):
        Operator.__init__(self, op_image, BINARY_SIGN_OP_MAP[op_image])

def handleNumber(token, expr_stack, op_stack):
    if '(' == token.image:
        op_stack.append(OpenParen())
        return True

    if token.is_pre_unary_operator:
        op_stack.append(PreUnaryOperator(token.image))
        return True

    if token.is_number:
        expr_stack.append(Integer(token.image))
        return False

    raise ValueError('Want a number, actually: ' + token.image)

def closeParenthesis(expr_stack, op_stack):
    while len(op_stack) > 0:
        operator = op_stack.pop()
        if '(' == operator.op_image:
            break
        expr_stack.append(operator.reduce(expr_stack))
    else:
        raise ValueError('Parenthesis not blanced')

def encounterBinaryOperator(operator, expr_stack, op_stack):
    while OP_PRIO_MATRIX[operator.op_type][op_stack[-1].op_type]:
        expr_stack.append(op_stack.pop().reduce(expr_stack))
    op_stack.append(operator)

def handleOperator(token, expr_stack, op_stack):
    if token.is_number or '(' == token.image:
        raise ValueError('Want a operator, actually: ' + token.image)

    if ')' == token.image:
        closeParenthesis(expr_stack, op_stack)
        return False

    operator = BinaryOperator(token.image)
    encounterBinaryOperator(operator, expr_stack, op_stack)
    return True

def buildExpression(tokens):
    want_factor = True
    expr_stack = []
    op_stack = [OpenParen()]

    for token in tokens:
        if want_factor:
            want_factor = handleNumber(token, expr_stack, op_stack)
        else:
            want_factor = handleOperator(token, expr_stack, op_stack)

    handleOperator(Token(')', False, False), expr_stack, op_stack)
    if len(expr_stack) != 1 or len(op_stack) != 0:
        raise ValueError('Invalid expression')
    return expr_stack.pop()

if '__main__' == __name__:
    assert (-(6 * 5)) + (4 ** (3 ** 2)) == buildExpression([
        Token('-', False, True),
        Token('(', False, False),
        Token('6', True,  False),
        Token('*', False, True),
        Token('5', True,  False),
        Token(')', False, False),
        Token('+', False, False),
        Token('4', True,  False),
        Token('^', False, False),
        Token('3', True,  False),
        Token('^', False, False),
        Token('2', True,  False),
    ]).evaluate()

    assert (-6) + 5 * (-4) + 3 + 2 == buildExpression([
        Token('-', False, True),
        Token('6', True,  False),
        Token('+', False, True),
        Token('5', True,  False),
        Token('*', False, False),
        Token('-', False, True),
        Token('4', True,  False),
        Token('+', False, False),
        Token('3', True,  False),
        Token('+', False, False),
        Token('2', True,  False),
    ]).evaluate()

    assert (+6) + (-5) * ((-4) ** (3 ** 2)) == buildExpression([
        Token('+', False, True),
        Token('6', True,  False),
        Token('+', False, True),
        Token('-', False, True),
        Token('5', True,  False),
        Token('*', False, False),
        Token('-', False, True),
        Token('4', True,  False),
        Token('^', False, False),
        Token('3', True,  False),
        Token('^', False, False),
        Token('2', True,  False),
    ]).evaluate()
