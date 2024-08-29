document.getElementById('langForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const langName = document.getElementById('langName').value;
    const fileExtension = document.getElementById('fileExtension').value;
    const indentation = document.getElementById('indentation').value;
    const commentSymbol = document.getElementById('commentSymbol').value || '#';
    const ifKeyword = document.getElementById('ifKeyword').value || 'if';
    const elseKeyword = document.getElementById('elseKeyword').value || 'else';
    const whileKeyword = document.getElementById('whileKeyword').value || 'while';
    const printKeyword = document.getElementById('printKeyword').value || 'print';
    const forKeyword = document.getElementById('forKeyword').value || 'for';
    const inputKeyword = document.getElementById('inputKeyword').value || 'input';
    const fileReadKeyword = document.getElementById('fileReadKeyword').value || 'file_read';
    const fileWriteKeyword = document.getElementById('fileWriteKeyword').value || 'file_write';

    const interpreterCode = `
import re
import sys

class ${langName}Interpreter:
def __init__(self):
self.variables = {}

def run(self, code):
lines = code.split('\\n')
for line in lines:
    self.execute_line(line.strip())

def execute_line(self, line):
if line.startswith('${commentSymbol}'):
    return
elif line.startswith('${printKeyword}'):
    match = re.match(r'${printKeyword}\s*\((.*)\)', line)
    if match:
        print(self.evaluate_expression(match.group(1)))
elif line.startswith('${inputKeyword}'):
    match = re.match(r'${inputKeyword}\s*\((.*)\)', line)
    if match:
        var_name = match.group(1).strip()
        self.variables[var_name] = input()
elif '=' in line:
    var_name, expression = line.split('=', 1)
    self.variables[var_name.strip()] = self.evaluate_expression(expression)
# Add more syntax rules here

def evaluate_expression(self, expression):
# Simple evaluation, replace variable names with their values
for var_name, value in self.variables.items():
    expression = expression.replace(var_name, str(value))
return eval(expression)

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
interpreter.run(code)
`;

    const blob = new Blob([interpreterCode], {type: "text/plain;charset=utf-8"});
    saveAs(blob, `${langName.toLowerCase()}_interpreter.py`);

    alert(`${langName} interpreter has been generated and downloaded. Use it to run .${fileExtension} files.`);
});