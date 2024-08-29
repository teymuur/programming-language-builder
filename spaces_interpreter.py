import re
import sys
import os

class TestInterpreter:
    def __init__(self):
        self.variables = {}
        self.keywords = {
            'if': self.handle_if,
            'else': self.handle_else,
            'while': self.handle_while,
            'print': self.handle_print,
            'for': self.handle_for,
            'input': self.handle_input,
            'file_read': self.handle_file_read,
            'file_write': self.handle_file_write
        }
        self.indentation_level = 0

    def run(self, code):
        self.lines = code.split('\n')
        self.current_line = 0
        while self.current_line < len(self.lines):
            self.parse_statement(self.lines[self.current_line].strip())
            self.current_line += 1

    def parse_statement(self, line):
        if not line or line.startswith('#'):
            return
        
        tokens = self.tokenize(line)
        if not tokens:
            return
        if tokens[0][0] == 'ID':
            if tokens[0][1] in self.keywords:
                self.keywords[tokens[0][1]](tokens[1:])
            elif len(tokens) > 1 and tokens[1][1] == '=':
                self.handle_assignment(tokens)
            else:
                self.error(f"Unknown identifier: {tokens[0][1]}")
        else:
            self.error(f"Unexpected token: {tokens[0][1]}")

    def tokenize(self, line):
        token_specification = [
            ('NUMBER',   r'\d+(\.\d*)?'),
            ('ASSIGN',   r'='),
            ('ID',       r'[A-Za-z_]\w*'),
            ('OP',       r'[+\-*/()<>=!]'),
            ('STRING',   r'"[^"]*"'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.')
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        return [(m.lastgroup, m.group()) for m in re.finditer(tok_regex, line) if m.lastgroup != 'SKIP']

    def handle_if(self, tokens):
        condition = self.evaluate(tokens)
        if condition:
            self.execute_block()
        else:
            self.skip_block()
            if self.current_line < len(self.lines) and self.lines[self.current_line].strip().startswith('else'):
                self.current_line += 1
                self.execute_block()

    def handle_else(self, tokens):
        self.execute_block()

    def handle_while(self, tokens):
        while_start = self.current_line
        while self.evaluate(tokens):
            self.execute_block()
            self.current_line = while_start
            if self.current_line >= len(self.lines):
                break

    def handle_for(self, tokens):
        # Placeholder for for loop implementation
        pass

    def handle_print(self, tokens):
        value = self.evaluate(tokens)
        print(value)

    def handle_input(self, tokens):
        var_name = tokens[0][1]
        self.variables[var_name] = input()

    def handle_file_read(self, tokens):
        filename = self.evaluate(tokens[:-2])
        var_name = tokens[-1][1]
        try:
            with open(filename, 'r') as file:
                self.variables[var_name] = file.read()
        except IOError as e:
            self.error(f"Error reading file: {e}")

    def handle_file_write(self, tokens):
        to_index = next((i for i, t in enumerate(tokens) if t[1] == 'to'), -1)
        if to_index == -1:
            self.error("Invalid file_write syntax")
        filename = self.evaluate(tokens[to_index+1:])
        content = self.evaluate(tokens[:to_index])
        try:
            with open(filename, 'w') as file:
                file.write(str(content))
        except IOError as e:
            self.error(f"Error writing to file: {e}")

    def handle_assignment(self, tokens):
        var_name = tokens[0][1]
        value = self.evaluate(tokens[2:])
        self.variables[var_name] = value

    def evaluate(self, tokens):
        if not tokens:
            return None
        if len(tokens) == 1:
            token = tokens[0]
            if token[0] == 'NUMBER':
                return float(token[1])
            elif token[0] == 'ID':
                return self.variables.get(token[1], 0)
            elif token[0] == 'STRING':
                return token[1][1:-1]  # Remove quotes
        expr = ' '.join(token[1] for token in tokens)
        try:
            return eval(expr, {"__builtins__": None}, self.variables)
        except:
            self.error(f"Invalid expression: {expr}")

    def execute_block(self):
        self.indentation_level += 1
        self.current_line += 1
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].strip()
            if not line or line.startswith('#'):
                self.current_line += 1
                continue
            if self.get_indentation(self.lines[self.current_line]) == self.indentation_level:
                self.parse_statement(line)
                self.current_line += 1
            else:
                break
        self.indentation_level -= 1

    def skip_block(self):
        self.current_line += 1
        while self.current_line < len(self.lines):
            if self.get_indentation(self.lines[self.current_line]) <= self.indentation_level:
                break
            self.current_line += 1

    def get_indentation(self, line):
        return len(line) - len(line.lstrip())

    def error(self, message):
        raise SyntaxError(f"Line {self.current_line + 1}: {message}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.spaces.test-lang'):
        print(f"Error: File must have .spaces.test-lang extension")
        sys.exit(1)

    with open(filename, 'r') as file:
        code = file.read()

    interpreter = TestInterpreter()
    try:
        interpreter.run(code)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
    except Exception as e:
        print(f"Runtime Error: {e}")