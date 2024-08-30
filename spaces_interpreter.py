import re
import sys

class TestInterpreter:
    def __init__(self):
        self.variables = {}
        self.program = []
        self.pc = 0  # Program Counter

    def run(self, code):
        self.parse(code)
        while self.pc < len(self.program):
            try:
                self.execute(self.program[self.pc])
                self.pc += 1
            except IndexError:
                self.error(f"Unexpected end of program", self.pc)

    def parse(self, code):
        lines = code.split('\n')
        self.program = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            tokens = self.tokenize(stripped)
            if tokens:  # Only add non-empty token lists
                self.program.append((i + 1, tokens))  # Store line number with tokens

    def tokenize(self, line):
        token_specification = [
            ('NUMBER',   r'\d+(\.\d*)?'),
            ('ASSIGN',   r'='),
            ('ID',       r'[A-Za-z_]\w*'),
            ('OP',       r'[+\-*/()<>=!]+'),
            ('STRING',   r'"[^"]*"'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.')
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        return [(m.lastgroup, m.group()) for m in re.finditer(tok_regex, line) if m.lastgroup != 'SKIP']

    def execute(self, instruction):
        line_num, tokens = instruction
        if not tokens:
            return
        
        keyword = tokens[0][1]
        if keyword == 'if':
            self.handle_if(tokens[1:], line_num)
        elif keyword == 'else':
            self.handle_else(line_num)
        elif keyword == 'while':
            self.handle_while(tokens[1:], line_num)
        elif keyword == 'print':
            self.handle_print(tokens[1:], line_num)
        elif keyword == 'input':
            self.handle_input(tokens[1:], line_num)
        elif keyword == 'file_write':
            self.handle_file_write(tokens[1:], line_num)
        elif keyword == 'file_read':
            self.handle_file_read(tokens[1:], line_num)
        elif len(tokens) > 1 and tokens[1][1] == '=':
            self.handle_assignment(tokens, line_num)
        else:
            self.error(f"Unknown statement: {' '.join(t[1] for t in tokens)}", line_num)

    def handle_if(self, condition, start_line):
        if self.evaluate_condition(condition, start_line):
            self.pc += 1  # Move to the next instruction
        else:
            # Skip to matching else or end of if block
            nesting = 1
            while nesting > 0 and self.pc < len(self.program) - 1:
                self.pc += 1
                next_tokens = self.program[self.pc][1]
                if next_tokens[0][1] == 'if':
                    nesting += 1
                elif next_tokens[0][1] == 'else' and nesting == 1:
                    self.pc += 1  # Move past the else
                    break
                elif nesting == 1 and (self.pc == len(self.program) - 1 or self.program[self.pc + 1][1][0][1] in ['else', 'while', 'print', 'input', 'file_write', 'file_read']):
                    break
            if nesting > 0:
                self.error("Unmatched if statement", start_line)

    def handle_else(self, line_num):
        # Skip to end of else block
        nesting = 1
        while nesting > 0 and self.pc < len(self.program) - 1:
            self.pc += 1
            next_tokens = self.program[self.pc][1]
            if next_tokens[0][1] == 'if':
                nesting += 1
            elif nesting == 1 and (self.pc == len(self.program) - 1 or self.program[self.pc + 1][1][0][1] in ['else', 'while', 'print', 'input', 'file_write', 'file_read']):
                break

    def handle_while(self, condition, start_line):
        while_start = self.pc
        while self.evaluate_condition(condition, start_line):
            # Execute the while block
            self.pc += 1
            while self.pc < len(self.program):
                next_tokens = self.program[self.pc][1]
                if next_tokens[0][1] == 'while':
                    break
                self.execute(self.program[self.pc])
                self.pc += 1
            self.pc = while_start  # Go back to re-evaluate the condition

        # Skip to end of while block
        nesting = 1
        while nesting > 0 and self.pc < len(self.program) - 1:
            self.pc += 1
            next_tokens = self.program[self.pc][1]
            if next_tokens[0][1] == 'while':
                nesting += 1
            elif nesting == 1 and (self.pc == len(self.program) - 1 or self.program[self.pc + 1][1][0][1] in ['else', 'while', 'print', 'input', 'file_write', 'file_read']):
                break
        if nesting > 0:
            self.error("Unmatched while statement", start_line)

    def handle_print(self, tokens, line_num):
        value = self.evaluate(tokens, line_num)
        print(str(value))

    def handle_input(self, tokens, line_num):
        if not tokens:
            self.error("Missing variable name for input", line_num)
        var_name = tokens[0][1]
        self.variables[var_name] = input()

    def handle_assignment(self, tokens, line_num):
        if len(tokens) < 3:
            self.error("Invalid assignment statement", line_num)
        var_name = tokens[0][1]
        value = self.evaluate(tokens[2:], line_num)
        self.variables[var_name] = value

    def handle_file_write(self, tokens, line_num):
        if len(tokens) < 4 or tokens[-2][1] != 'to':
            self.error("Invalid file_write statement", line_num)
        content = self.evaluate(tokens[:-2], line_num)
        filename = self.evaluate([tokens[-1]], line_num)
        with open(filename, 'w') as f:
            f.write(str(content))

    def handle_file_read(self, tokens, line_num):
        if len(tokens) != 4 or tokens[2][1] != 'to':
            self.error("Invalid file_read statement", line_num)
        filename = self.evaluate([tokens[0]], line_num)
        var_name = tokens[3][1]
        with open(filename, 'r') as f:
            self.variables[var_name] = f.read()

    def evaluate_condition(self, tokens, line_num):
        if len(tokens) != 3:
            self.error("Invalid condition", line_num)
        left = self.evaluate([tokens[0]], line_num)
        op = tokens[1][1]
        right = self.evaluate([tokens[2]], line_num)
        
        if op == '<':
            return float(left) < float(right)
        elif op == '>':
            return float(left) > float(right)
        elif op == '<=':
            return float(left) <= float(right)
        elif op == '>=':
            return float(left) >= float(right)
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        else:
            self.error(f"Unknown operator: {op}", line_num)

    def evaluate(self, tokens, line_num):
        if not tokens:
            return None
        if len(tokens) == 1:
            token = tokens[0]
            if token[0] == 'NUMBER':
                return float(token[1])
            elif token[0] == 'ID':
                if token[1] not in self.variables:
                    self.error(f"Undefined variable: {token[1]}", line_num)
                return self.variables[token[1]]
            elif token[0] == 'STRING':
                return token[1][1:-1]  # Remove quotes
        expr = ' '.join(token[1] for token in tokens)
        try:
            return eval(expr, {"__builtins__": None, "float": float}, self.variables)
        except Exception as e:
            self.error(f"Invalid expression: {expr}. Error: {str(e)}", line_num)

    def error(self, message, line_num):
        raise SyntaxError(f"Line {line_num}: {message}")

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
        print(f"Error occurred at line {interpreter.pc + 1}")