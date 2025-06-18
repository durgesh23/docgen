-- Ultra-simple filter to handle the \real command in tables

function RawBlock(block)
  if block.format == "latex" then
    -- Replace \real commands
    block.text = block.text:gsub("\\real{([0-9.]+)}", "%1")
    
    -- Replace column width expressions
    block.text = block.text:gsub("p{%(\\columnwidth %- 2\\tabcolsep%) %* ([0-9.]+)}", 
                               "p{%1\\columnwidth}")
  end
  return block
end

function RawInline(inline)
  if inline.format == "latex" then
    -- Replace \real commands
    inline.text = inline.text:gsub("\\real{([0-9.]+)}", "%1")
  end
  return inline
end
