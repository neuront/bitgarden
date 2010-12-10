import output

class ContextFlow:
    def __init__(self):
        self.block = output.Block([])

class Expression:
    pass

class NumericLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        return output.NumericLiteral(self.value)

class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        return output.StringLiteral(self.value)

class Reference(Expression):
    def __init__(self, name):
        self.name = name

    def compile(self, context):
        return output.Reference(self.name)

class Binary(Expression):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def compile(self, context):
        return output.Binary(self.op,
                             self.left.compile(context),
                             self.right.compile(context))

class Call(Expression):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def compile(self, context):
        compl_callee = self.callee.compile(context)
        compl_args = [ arg.compile(context) for arg in self.arguments ]
        return output.Call(compl_callee, compl_args)

class Lambda(Expression):
    def __init__(self, parameters, body):
        self.parameters = parameters
        self.body = body

    def compile(self, context):
        body_context = ContextFlow()
        body_flow = body_context.block
        self.body.compile(body_context)
        return output.Lambda(self.parameters, body_flow)

class RegularAsyncCall(Expression):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def compile(self, context):
        compl_callee = self.callee.compile(context)

        compl_args = [ arg.compile(context) for arg in self.arguments ]

        callback_body_context = ContextFlow()
        cb_body_flow = callback_body_context.block
        compl_args.append(output.Lambda([ 'error', 'result' ], cb_body_flow))

        context.block.add(output.Arithmetics(
                                    output.Call(compl_callee, compl_args)))

        context.block = cb_body_flow

        return output.Reference('result')

class Statement:
    pass

class Block(Statement):
    def __init__(self, statements):
        self.statements = statements

    def compile(self, context):
        for s in self.statements: s.compile(context)

class Arithmetics(Statement):
    def __init__(self, expression):
        self.expression = expression

    def compile(self, context):
        compl_arith = output.Arithmetics(self.expression.compile(context))
        context.block.add(compl_arith)

class Branch(Statement):
    def __init__(self, predicate, consequence, alternative):
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative

    def compile(self, context):
        consq_context = ContextFlow()
        consq_flow = consq_context.block
        self.consequence.compile(consq_context)

        alter_context = ContextFlow()
        alter_flow = alter_context.block
        self.alternative.compile(consq_context)

        compl_branch = output.Branch(self.predicate.compile(context),
                                     consq_flow, alter_flow)
        context.block.add(compl_branch)

def main():
    root_context = ContextFlow()
    root_flow = root_context.block

    Block([
            Arithmetics(NumericLiteral('10.24')),
            Arithmetics(Call(Reference('setTimeout'), [
                    Lambda([], Block([
                            Branch(Reference('condition'), Block([
                                Arithmetics(Call(Reference('doSomething'), []))
                            ]), Block([]))
                        ])),
                    NumericLiteral(1000)
                ])),
            Arithmetics(
                    Binary(
                        '=',
                        Reference('content'),
                        RegularAsyncCall(
                            Binary('.', Reference('fs'), Reference('readFile')),
                            [ StringLiteral('/etc/passwd') ]))),
            Arithmetics(Call(Binary('.',
                                    Reference('console'),
                                    Reference('log')),
                        [ Reference('context') ]))
        ]).compile(root_context)

    print root_flow.str()

if __name__ == '__main__':
    main()
