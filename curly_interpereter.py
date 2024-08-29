
import re
import sys
import os

class helloInterpreter:
    def __init__(self):
        self.variables = {}
        self.keywords = {
            'if': self.handle_if,
            'else': self.handle_else,
            'while': self.handle_while,
            'print': self.handle_print,
            'input': self.handle_input,
            'file_read': self.handle_file_read,
            'file_write': self.handle_file_write
        }

    def run(self, code):
        self.tokens = self.tokenize(code)
        self.current = 0
        while self.current < len(self.tokens):
            self.parse_statement()

    def tokenize(self, code):
        token_specification = [
            ('NUMBER',   r'\d+(\.\d*)?'),
            ('ASSIGN',   r'='),
            ('END',      r';'),
            ('ID',       r'[A-Za-z_]\w*'),
            ('OP',       r'[+\-*/{}()<>=!]'),
            ('STRING',   r'"[^"]*"'),
            ('NEWLINE',  r'\n'),
            ('COMMENT',  r'#.*'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.')
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        return [
            (m.lastgroup, m.group())
            for m in re.finditer(tok_regex, code)
            if m.lastgroup not in ['SKIP', 'COMMENT']
        ]

    def parse_statement(self):
        token = self.get_next_token()
        if token[0] == 'ID':
            if token[1] in self.keywords:
                self.keywords[token[1]]()
            elif self.peek()[1] == '=':
                self.handle_assignment(token[1])
            else:
                self.error(f"Unknown identifier: {token[1]}")
        elif token[0] == 'NEWLINE':
            pass  # Skip newlines
        elif token[0] == 'EOF':
            return  # End of file reached
        else:
            self.error(f"Unexpected token: {token[1]}")

    def handle_if(self):
        condition = self.parse_expression()
        self.expect('OP', '{')
        if self.evaluate(condition):
            while self.peek()[1] != '}':
                self.parse_statement()
            self.expect('OP', '}')
            if self.peek()[1] == 'else':
                self.get_next_token()  # Consume 'else'
                self.expect('OP', '{')
                self.skip_block()
        else:
            self.skip_block()
            if self.peek()[1] == 'else':
                self.get_next_token()  # Consume 'else'
                self.expect('OP', '{')
                while self.peek()[1] != '}':
                    self.parse_statement()
                self.expect('OP', '}')

    def handle_else(self):
        self.error("Unexpected 'else' without matching 'if'")

    def handle_while(self):
        condition_start = self.current
        condition = self.parse_expression()
        self.expect('OP', '{')
        while_start = self.current
        while self.evaluate(condition):
            while self.peek()[1] != '}':
                self.parse_statement()
            self.expect('OP', '}')
            self.current = condition_start
            condition = self.parse_expression()
            self.expect('OP', '{')
        self.skip_block()

    def handle_print(self):
        value = self.parse_expression()
        print(self.evaluate(value))
        self.expect('END')

    def handle_input(self):
        var_name = self.expect('ID')[1]
        self.variables[var_name] = input()
        self.expect('END')

    def handle_file_read(self):
        filename = self.evaluate(self.parse_expression())
        var_name = self.expect('ID')[1]
        try:
            with open(filename, 'r') as file:
                self.variables[var_name] = file.read()
        except IOError as e:
            self.error(f"Error reading file: {e}")
        self.expect('END')

    def handle_file_write(self):
        filename = self.evaluate(self.parse_expression())
        content = self.evaluate(self.parse_expression())
        try:
            with open(filename, 'w') as file:
                file.write(str(content))
        except IOError as e:
            self.error(f"Error writing to file: {e}")
        self.expect('END')

    def handle_assignment(self, var_name):
        self.expect('ASSIGN')
        value = self.parse_expression()
        self.variables[var_name] = self.evaluate(value)
        self.expect('END')

    def parse_expression(self):
        expr = []
        while self.peek()[1] not in [';', '{', '}']:
            expr.append(self.get_next_token())
        return expr

    def evaluate(self, expr):
        if len(expr) == 1:
            token = expr[0]
            if token[0] == 'NUMBER':
                return float(token[1])
            elif token[0] == 'ID':
                return self.variables.get(token[1], 0)
            elif token[0] == 'STRING':
                return token[1][1:-1]  # Remove quotes
        expr_str = ' '.join(token[1] for token in expr)
        return eval(expr_str, {}, self.variables)

    def expect(self, expected_type, expected_value=None):
        token = self.get_next_token()
        if expected_value:
            if token[0] != expected_type or token[1] != expected_value:
                self.error(f"Expected {expected_value}, got {token[1]}")
        elif token[0] != expected_type:
            self.error(f"Expected {expected_type}, got {token[0]}")
        return token

    def get_next_token(self):
        if self.current < len(self.tokens):
            self.current += 1
            return self.tokens[self.current - 1]
        return ('EOF', '')

    def peek(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return ('EOF', '')

    def skip_block(self):
        depth = 1
        while depth > 0:
            token = self.get_next_token()
            if token[1] == '{':
                depth += 1
            elif token[1] == '}':
                depth -= 1

    def error(self, message):
        raise SyntaxError(message)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.test-lang'):
        print(f"Error: File must have .test-lang extension")
        sys.exit(1)

    with open(filename, 'r') as file:
        code = file.read()

    interpreter = helloInterpreter()
    try:
        interpreter.run(code)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
    except Exception as e:
        print(f"Runtime Error: {e}")
