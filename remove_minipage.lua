-- Lua filter to remove minipage environments from table headers
-- Add detailed logging to debug the Lua filter
function Table(el)
  io.stderr:write("Processing a table element\n")
  io.stderr:write("Table element structure: " .. pandoc.utils.stringify(el) .. "\n")
  if el.rows then  -- Ensure el.rows is not nil
    for i, row in ipairs(el.rows) do
      for j, cell in ipairs(row) do
        for k, block in ipairs(cell) do
          if block.t == "RawBlock" then
            io.stderr:write("Found RawBlock: " .. block.text .. "\n")
            -- Replace minipage environments
            block.text = block.text:gsub("\\begin%%{minipage%%}.-\\end%%{minipage%%}", "")
            -- Replace problematic column width expressions
            block.text = block.text:gsub("\\%((\\columnwidth %- 2\\\\tabcolsep\\) %* \\real%{(.-)}\\)", "\\calculateWidth{\\columnwidth}{%1}")
            io.stderr:write("Updated RawBlock: " .. block.text .. "\n")
            io.stderr:write("Processed block text: " .. block.text .. "\n")
            -- Add logging to confirm if the replacement was successful
            if block.text:find("\\calculateWidth") then
              io.stderr:write("Replacement successful: " .. block.text .. "\n")
            else
              io.stderr:write("Replacement failed for block: " .. block.text .. "\n")
            end
          end
        end
      end
    end
  end
  return el
end
