;+
; zenith  angle: [0   , 180] or [0  , pi]
; azimuth angle: [-180, 180] or [-pi, pi]
;-
function ScatteringAngle, SZA = SZA, SAA = SAA, VZA = VZA, VAA = VAA, degree = DEGREE
  compile_opt idl2, hidden
  
  if ~ISA(SZA) or ~ISA(SAA) or ~ISA(VZA) or ~ISA(VAA) then begin
    PRINTF, -1, 'Invalid Parameter Number'
    RETURN, -1
  endif
  
  if ISA(DEGREE) then begin
    SZA *= !const.DtoR
    SAA *= !const.DtoR
    VZA *= !const.DtoR
    VAA *= !const.DtoR
  endif
  
  ;cos(SA) = - cos(SZA) * cos(VZA) - sqrt(1 - cos(SZA) * cos(SZA)) * sqrt(1 - cos(VZA) * cos(VZA)) * cos(SAA - VAA)
  
  cSZA = COS(TEMPORARY(SZA))
  cVZA = COS(TEMPORARY(VZA))
  
  RETURN, ACOS(-cSZA * cVZA - SQRT(1-TEMPORARY(cSZA)^2) * SQRT((1-TEMPORARY(cVZA)^2)) * COS(TEMPORARY(SAA) - TEMPORARY(VAA))) * (ISA(DEGREE) ? !const.RtoD : 1)
  
end
