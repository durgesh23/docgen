-- Simplest possible Lua filter to fix \real command in tables

-- Define a replacement function for \real commands
function replace_real(text)
  -- First replace the specific pattern that's causing issues
  local result = text:gsub("(\\columnwidth %- 2\\tabcolsep) %* \\real{([0-9.]+)}", 
                          "\\dimexpr\\columnwidth * %2\\relax")
  
  -- Then replace any remaining \real commands
  result = result:gsub("\\real{([0-9.]+)}", "%1")
  
  return result
end

-- Process any Raw LaTeX blocks
function RawBlock(block)
  if block.format == "latex" then
    block.text = replace_real(block.text)
  end
  return block
end

-- Process tables
function Table(el)
  return el
end

-- Process any Raw LaTeX inline elements
function RawInline(inline)
  if inline.format == "latex" then
    inline.text = replace_real(inline.text)
  end
  return inline
end
  
  -- Double-check if there are still \real commands left
  if text:find("\\real") then
    io.stderr:write("WARNING: \\real command still present in text!\n")
    -- Extreme measure - do a complete direct replacement of the specific pattern from debug logs
    text = text:gsub("%(\\columnwidth %- 2\\tabcolsep%) %* \\real{([0-9%.]+)}", "\\dimexpr\\columnwidth * %1\\relax")
  end
  
  io.stderr:write("Modified text (excerpt): " .. text:sub(1, 50) .. "...\n")
  return text
end

-- Process any raw LaTeX blocks
function RawBlock(block)
  if block.format == "latex" then
    block.text = fix_latex_text(block.text)
  end
  return block
end

-- Process tables
function Table(el)
  io.stderr:write("Processing table\n")
  return el
end

-- Final document-wide processing
function Pandoc(doc)
  -- Process all blocks to ensure we catch everything
  for i, block in ipairs(doc.blocks) do
    if block.t == "RawBlock" and block.format == "latex" then
      block.text = fix_latex_text(block.text)
    end
  end
  
  io.stderr:write("Completed document processing\n")
  return doc
end
