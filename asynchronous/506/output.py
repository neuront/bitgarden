class Expression:
    pass

class NumericLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def str(self):
        return str(self.value)

class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def str(self):
        return `self.value`

class Reference(Expression):
    def __init__(self, name):
        self.name = name

    def str(self):
        return self.name

class Binary(Expression):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def str(self):
        return '({left} {op} {right})'.format(
                left=self.left.str(), op=self.op, right=self.right.str())

class Call(Expression):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def str(self):
        return '({callee}({arguments}))'.format(
                callee=self.callee.str(),
                arguments=','.join([ arg.str() for arg in self.arguments ]))

class Lambda(Expression):
    def __init__(self, parameters, body):
        self.parameters = parameters
        self.body = body

    def str(self):
        return 'function ({parameters}) {body}'.format(
                    parameters=','.join(self.parameters), body=self.body.str())

class Statement:
    pass

class Block(Statement):
    def __init__(self, statements):
        self.statements = statements

    def str(self):
        return '{' + ''.join([ st.str() for st in self.statements ]) + '}'

    def add(self, statement):
        self.statements.append(statement)

class Arithmetics(Statement):
    def __init__(self, expression):
        self.expression = expression

    def str(self):
        return self.expression.str() + ';'

class Branch(Statement):
    def __init__(self, predicate, consequence, alternative):
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative

    def str(self):
        return 'if ({pred}) {consq} else {alter}'.format(
                    pred=self.predicate.str(),
                    consq=self.consequence.str(),
                    alter=self.alternative.str())

def main():
    print '/* a binary operation in a single statement */'
    print Arithmetics(Binary(
            '+',
            NumericLiteral(10),
            Reference('x')
        )).str()
    # result: (10 + x);

    print '/* a call in a statement, as a member of a block */'
    print Block([
            Arithmetics(Call(Binary('.',
                                    Reference('console'),
                                    Reference('log')),
                             [ StringLiteral('something') ]))
        ]).str()
    # result: {((console . log)('something'));}

    print '/* a more complex case */'
    print Block([
            Arithmetics(NumericLiteral('10.24')),
            Arithmetics(Call(Reference('setTimeout'), [
                    Lambda([], Block([
                            Branch(Reference('condition'), Block([
                                Arithmetics(Call(Reference('doSomething'), []))
                            ]), Block([]))
                        ])),
                    NumericLiteral(1000)
                ])),
        ]).str()
    # result: {10.24;(setTimeout(function () {if (condition) {(doSomething());} else {}},1000));}

if __name__ == '__main__':
    main()
