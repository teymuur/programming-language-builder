
document.getElementById('langForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const langName = document.getElementById('langName').value.trim();
    const fileExtension = document.getElementById('fileExtension').value.trim();
    const indentation = document.getElementById('indentation').value.trim();
    const commentSymbol = document.getElementById('commentSymbol').value.trim() || '#';
    const ifKeyword = document.getElementById('ifKeyword').value.trim() || 'if';
    const elseKeyword = document.getElementById('elseKeyword').value.trim() || 'else';
    const whileKeyword = document.getElementById('whileKeyword').value.trim() || 'while';
    const printKeyword = document.getElementById('printKeyword').value.trim() || 'print';
    const forKeyword = document.getElementById('forKeyword').value.trim() || 'for';
    const inputKeyword = document.getElementById('inputKeyword').value.trim() || 'input';
    const fileReadKeyword = document.getElementById('fileReadKeyword').value.trim() || 'file_read';
    const fileWriteKeyword = document.getElementById('fileWriteKeyword').value.trim() || 'file_write';

    let interpreterCode = '';

    if (indentation == 'braces') {
        interpreterCode = `
import re
import sys
import os

class ${langName}Interpreter:
    def __init__(self):
        self.variables = {}
        self.keywords = {
            '${ifKeyword}': self.handle_if,
            '${elseKeyword}': self.handle_else,
            '${whileKeyword}': self.handle_while,
            '${printKeyword}': self.handle_print,
            '${inputKeyword}': self.handle_input,
            '${fileReadKeyword}': self.handle_file_read,
            '${fileWriteKeyword}': self.handle_file_write
        }

    def run(self, code):
        self.tokens = self.tokenize(code)
        self.current = 0
        while self.current < len(self.tokens):
            self.parse_statement()

    def tokenize(self, code):
        token_specification = [
            ('NUMBER',   r'\\d+(\\.\\d*)?'),
            ('ASSIGN',   r'='),
            ('END',      r';'),
            ('ID',       r'[A-Za-z_]\\w*'),
            ('OP',       r'[+\\-*/{}()<>=!]'),
            ('STRING',   r'"[^"]*"'),
            ('NEWLINE',  r'\\n'),
            ('COMMENT',  r'${commentSymbol}.*'),
            ('SKIP',     r'[ \\t]+'),
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
            if self.peek()[1] == '${elseKeyword}':
                self.get_next_token()  # Consume 'else'
                self.expect('OP', '{')
                self.skip_block()
        else:
            self.skip_block()
            if self.peek()[1] == '${elseKeyword}':
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
    if not filename.endswith('.${fileExtension}'):
        print(f"Error: File must have .${fileExtension} extension")
        sys.exit(1)

    with open(filename, 'r') as file:
        code = file.read()

    interpreter = ${langName}Interpreter()
    try:
        interpreter.run(code)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
    except Exception as e:
        print(f"Runtime Error: {e}")
`;
    }else if (indentation == 'spaces') {
        interpreterCode = `
        import re
        import sys
        import os
        
        class ${langName}Interpreter:
            def __init__(self):
                self.variables = {}
                self.keywords = {
                    '${ifKeyword}': self.handle_if,
                    '${elseKeyword}': self.handle_else,
                    '${whileKeyword}': self.handle_while,
                    '${printKeyword}': self.handle_print,
                    '${forKeyword}': self.handle_for,
                    '${inputKeyword}': self.handle_input,
                    '${fileReadKeyword}': self.handle_file_read,
                    '${fileWriteKeyword}': self.handle_file_write
                }
                self.indentation_level = 0
        
            def run(self, code):
                self.lines = code.split('\\n')
                self.current_line = 0
                while self.current_line < len(self.lines):
                    self.parse_statement(self.lines[self.current_line].strip())
                    self.current_line += 1
        
            def parse_statement(self, line):
                if not line or line.startswith('${commentSymbol}'):
                    return
                
                tokens = self.tokenize(line)
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
                    ('NUMBER',   r'\\d+(\\.\\d*)?'),
                    ('ASSIGN',   r'='),
                    ('ID',       r'[A-Za-z_]\\w*'),
                    ('OP',       r'[+\\-*/()<>=!]'),
                    ('STRING',   r'"[^"]*"'),
                    ('SKIP',     r'[ \\t]+'),
                    ('MISMATCH', r'.')
                ]
                tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
                return [(m.lastgroup, m.group()) for m in re.finditer(tok_regex, line) if m.lastgroup != 'SKIP']
        
            def handle_if(self, tokens):
                condition = self.evaluate(tokens)
                if condition:
                    self.indentation_level += 1
                    self.current_line += 1
                    while self.current_line < len(self.lines):
                        line = self.lines[self.current_line].strip()
                        if line.startswith('${elseKeyword}'):
                            break
                        if not line or line.startswith('${commentSymbol}'):
                            self.current_line += 1
                            continue
                        if self.get_indentation(self.lines[self.current_line]) == self.indentation_level:
                            self.parse_statement(line)
                            self.current_line += 1
                        else:
                            break
                    self.indentation_level -= 1
                else:
                    while self.current_line < len(self.lines):
                        if self.lines[self.current_line].strip().startswith('${elseKeyword}'):
                            return self.handle_else([])
                        if self.get_indentation(self.lines[self.current_line]) <= self.indentation_level:
                            return
                        self.current_line += 1
        
            def handle_else(self, tokens):
                self.indentation_level += 1
                self.current_line += 1
                while self.current_line < len(self.lines):
                    line = self.lines[self.current_line].strip()
                    if not line or line.startswith('${commentSymbol}'):
                        self.current_line += 1
                        continue
                    if self.get_indentation(self.lines[self.current_line]) == self.indentation_level:
                        self.parse_statement(line)
                        self.current_line += 1
                    else:
                        break
                self.indentation_level -= 1
        
            def handle_while(self, tokens):
                while_start = self.current_line
                condition = self.evaluate(tokens)
                while condition:
                    self.indentation_level += 1
                    self.current_line += 1
                    while self.current_line < len(self.lines):
                        line = self.lines[self.current_line].strip()
                        if not line or line.startswith('${commentSymbol}'):
                            self.current_line += 1
                            continue
                        if self.get_indentation(self.lines[self.current_line]) == self.indentation_level:
                            self.parse_statement(line)
                            self.current_line += 1
                        else:
                            break
                    self.indentation_level -= 1
                    self.current_line = while_start
                    condition = self.evaluate(tokens)
        
            def handle_for(self, tokens):
                # Implement for loop logic here
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
                filename = self.evaluate(tokens[:tokens.index(('ID', 'to'))])
                content = self.evaluate(tokens[tokens.index(('ID', 'to'))+1:])
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
                if len(tokens) == 1:
                    token = tokens[0]
                    if token[0] == 'NUMBER':
                        return float(token[1])
                    elif token[0] == 'ID':
                        return self.variables.get(token[1], 0)
                    elif token[0] == 'STRING':
                        return token[1][1:-1]  # Remove quotes
                expr = ' '.join(token[1] for token in tokens)
                return eval(expr, {}, self.variables)
        
            def get_indentation(self, line):
                return len(line) - len(line.lstrip())
        
            def error(self, message):
                raise SyntaxError(f"Line {self.current_line + 1}: {message}")
        
        if __name__ == '__main__':
            if len(sys.argv) != 2:
                print(f"Usage: python {sys.argv[0]} <filename>")
                sys.exit(1)
        
            filename = sys.argv[1]
            if not filename.endswith('.${fileExtension}'):
                print(f"Error: File must have .${fileExtension} extension")
                sys.exit(1)
        
            with open(filename, 'r') as file:
                code = file.read()
        
            interpreter = ${langName}Interpreter()
            try:
                interpreter.run(code)
            except SyntaxError as e:
                print(f"SyntaxError: {e}")
            except Exception as e:
                print(f"Runtime Error: {e}")
        `;
    }

    const blob = new Blob([interpreterCode], { type: "text/plain;charset=utf-8" });
    saveAs(blob, `${langName.toLowerCase()}_interpreter.py`);

    alert(`${langName} interpreter has been generated and downloaded. Use it to run .${fileExtension} files.`);
});
