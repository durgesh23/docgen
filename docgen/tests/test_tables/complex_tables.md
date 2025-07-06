# Complex Table Testing

## Tables with Long Text Content

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| This cell contains a very long text that should wrap properly within the table cell without overflowing into the next column or outside the page margins. | This is a shorter cell. | This is another cell with medium length content. |
| Short text | This cell also contains text that should wrap properly within the table boundaries and demonstrate that our LaTeX template handles wrapping correctly. | Final cell. |

## Tables with Code Blocks

| Component | Sample Code | Description |
|-----------|-------------|-------------|
| Component 1 | `const myFunction = (param1, param2) => { return param1 + param2; // This is a very long line of code that should wrap properly within the cell }` | This component demonstrates inline code wrapping. |
| Component 2 | ```javascript
function anotherFunction() {
  // This is a multiline code block
  const veryLongVariableName = "This is a long string value that should wrap properly within the table cell";
  console.log(veryLongVariableName);
  return true;
}
``` | This shows a multiline code block in a table cell. |

## Tables with Lists

| Feature | Implementation | Benefits |
|---------|----------------|----------|
| Feature A | - Step 1: Configure the settings<br>- Step 2: Initialize the component<br>- Step 3: Run the validation process | - Improved performance<br>- Better user experience<br>- Reduced complexity |
| Feature B | - First apply the transformation<br>- Then validate the output<br>- Finally save the results | - Maintains data integrity<br>- Ensures compatibility<br>- Simplifies maintenance |

## Tables with Mixed Content

| ID | Content | Technical Details |
|----|---------|-------------------|
| 1 | This section contains **bold text**, *italic text*, and `inline code` that should all be properly formatted within the table cell. | ```python
def process_data(input_data):
    result = input_data * 2
    return result
``` |
| 2 | - First item in a list<br>- Second item with `inline code`<br>- Third item with *emphasis* | Configuration: `{ "autoWrap": true, "maxWidth": 80, "tabSize": 4 }` |

## Wide Table with Many Columns

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 | Col 8 |
|-------|-------|-------|-------|-------|-------|-------|-------|
| Data 1 | Data 2 | Data 3 | Data 4 | Data 5 | Data 6 | Data 7 | Data 8 |
| Longer content that should wrap | Short | Medium length content | Short | Very very long content that definitely needs to wrap properly | Short | Medium | Short |

## Nested Tables

| Outer Col 1 | Outer Col 2 |
|-------------|-------------|
| Regular cell | <table><tr><th>Inner Header 1</th><th>Inner Header 2</th></tr><tr><td>Inner Data 1</td><td>Inner Data 2</td></tr></table> |
| Another regular cell | Cell with some text content |

This test document includes various table scenarios to verify our LaTeX template improvements.
