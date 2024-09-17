
# Custom Language Interpreter Guide

This guide will help you set up and use the custom language interpreter. The interpreter can be configured to use either curly braces or spaces for indentation, depending on your preference.

## Setting Up the Interpreter

1. Choose Your Syntax Style: Decide whether you want to use curly braces or spaces for indentation in your custom language.

2. Generate the Interpreter Code: Use the provided code generator to create the interpreter code based on your chosen syntax style and custom keywords.

3. Save the Interpreter Code: Save the generated interpreter code as a Python file, for example, `custom_interpreter.py`.

## Using the Interpreter

1. Write Your Custom Language Code: Create a new file with the extension you specified (e.g., `.mylang`) and write your code using your custom language syntax.

2. Run the Interpreter: Open a terminal or command prompt and run the interpreter with your custom language file as an argument:

   ```
   python custom_interpreter.py your_code_file.mylang
   ```

## Syntax Examples

### Curly Braces Syntax

```
if (x > 5) {
    print "x is greater than 5"
} else {
    print "x is less than or equal to 5"
}

while (y < 10) {
    print y
    y = y + 1
}
```

### Spaces (Indentation) Syntax

```
if x > 5
    print "x is greater than 5"
else
    print "x is less than or equal to 5"

while y < 10
    print y
    y = y + 1
```

## Custom Keywords

Remember to use the custom keywords you defined when generating the interpreter:

- If: `${ifKeyword}`
- Else: `${elseKeyword}`
- While: `${whileKeyword}`
- Print: `${printKeyword}`
- Input: `${inputKeyword}`
- File Read: `${fileReadKeyword}`
- File Write: `${fileWriteKeyword}`

## Additional Features

### Comments

Use `${commentSymbol}` to start a comment in your code.

### File Operations

To read from a file: `${fileReadKeyword} "filename.txt" to variable_name`

To write to a file: `${fileWriteKeyword} "content" to "filename.txt"`

## Troubleshooting

If you encounter any issues:

1. Check that you're using the correct syntax (curly braces or indentation) based on how you configured your interpreter.
2. Verify that you're using the custom keywords you defined.
3. Ensure your custom language file has the correct extension.
4. Check the error messages provided by the interpreter for specific issues in your code.

For further assistance or to report bugs, please contact the developer.

[Website](https://tymbb.com)
[Email](mailto:teymur_babayev08@yahoo.com)

## License

Check out [LICENSE](LICENSE)