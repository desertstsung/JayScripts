pro StaProjLine, dir
  compile_opt idl2, hidden

  files = FILE_SEARCH(dir, '*.pro')
  
  GET_LUN, lun
  str = ''
  n1  = (n2 = (n3 = 0L))

  foreach file, files do begin
    OPENR, lun, file
    while ~EOF(lun) do begin
      READF, lun, str
      str = STRCOMPRESS(str, /REMOVE_ALL)
      if str eq '' then n1++ else if STRMID(str,0,1) eq ';' then n2++ else n3++
    endwhile
    FREE_LUN, lun
  endforeach
  
  PRINTF, -1, 'BALNK   LINES: ', STRING(n1      , FORMAT='(i6)')
  PRINTF, -1, 'COMMENT LINES: ', STRING(n2      , FORMAT='(i6)')
  PRINTF, -1, 'CODE    LINES: ', STRING(n3      , FORMAT='(i6)')
  PRINTF, -1, '---------------------'
  PRINTF, -1, 'TOTAL   LINES: ', STRING(n1+n2+n3, FORMAT='(i6)')

end
