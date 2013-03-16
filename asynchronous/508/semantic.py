import output

class ContextFlow:
    def __init__(self):
        self.block = output.Block([])

class Expression:
    def is_async(self):
        return False

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

    def is_async(self):
        return self.left.is_async() or self.right.is_async()

    def compile(self, context):
        return output.Binary(self.op,
                             self.left.compile(context),
                             self.right.compile(context))

class Conditional(Expression):
    def __init__(self, predicate, consequence, alternative):
        self.predicate = predicate
        self.consequence = consequence
        self.alternative = alternative

    def is_async(self):
        return self.predicate.is_async() or self.left.is_async(
                                       ) or self.right.is_async()

    def compile(self, context):
        if self.consequence.is_async() or self.alternative.is_async():
            return self.compile_async(context)
        return self.compile_sync(context)

    def compile_sync(self, context):
        return output.Conditional(self.predicate.compile(context),
                                  self.consequence.compile(context),
                                  self.alternative.compile(context))

    def compile_async(self, context):
        pred_compl = self.predicate.compile(context)

        cb_body_context = ContextFlow()
        cb_body_block = cb_body_context.block
        cb_body_id = str(id(cb_body_block))
        cb_param = 'result$' + cb_body_id
        cb_lambda = output.Lambda([ cb_param ], cb_body_block)
        cb_ref_name = 'conditionalCallback$' + cb_body_id
        context.block.add(output.Arithmetics(output.Binary('=',
                                             output.Reference(cb_ref_name),
                                             cb_lambda)))

        def compile_one_branch(expression):
            sub_context = ContextFlow()
            sub_block = sub_context.block
            expr_compl = expression.compile(sub_context)
            sub_context.block.add(output.Arithmetics(output.Call(
                            output.Reference(cb_ref_name), [ expr_compl ])))
            return sub_block

        context.block.add(output.Branch(pred_compl,
                                        compile_one_branch(self.consequence),
                                        compile_one_branch(self.alternative)))

        context.block = cb_lambda.body

        return output.Reference(cb_param)

class Call(Expression):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def is_async(self):
        for arg in self.arguments:
            if arg.is_async():
                return True
        return self.callee.is_async()

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

    def is_async(self):
        return True

    def compile(self, context):
        compl_callee = self.callee.compile(context)

        compl_args = [ arg.compile(context) for arg in self.arguments ]

        callback_body_context = ContextFlow()
        cb_body_flow = callback_body_context.block

        result_id = id(cb_body_flow)
        result_ref = 'result$' + str(result_id)
        compl_args.append(output.Lambda([ 'error', result_ref ], cb_body_flow))

        context.block.add(output.Arithmetics(output.Call(compl_callee, compl_args)))

        context.block = cb_body_flow

        return output.Reference(result_ref)

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
            Arithmetics(
                Binary(
                    '=',
                    Reference('m'),
                    Conditional(
                        Reference('a'),
                        Reference('b'),
                        Reference('c')))),
            Arithmetics(
                Binary(
                    '=',
                    Reference('n'),
                    Conditional(
                        RegularAsyncCall(
                            Reference('f'),
                            [ NumericLiteral(0) ]),
                        Reference('x'),
                        Reference('y')))),
            Arithmetics(
                Binary(
                    '=',
                    Reference('p'),
                    Conditional(
                        Reference('z'),
                        RegularAsyncCall(
                            Reference('g'),
                            [ NumericLiteral(1) ]),
                        RegularAsyncCall(
                            Reference('h'),
                            [ NumericLiteral(2) ]))))
        ]).compile(root_context)

    print root_flow.str()

if __name__ == '__main__':
    main()
