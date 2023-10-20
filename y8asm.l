%{
    #include "y8.tab.h"
%}

NL [\n\r\l]
CND3 "NEVR"|"IFNC"|"IFNS"|"IFNZ"|"ALWS"|"IFC"|"IFS"|"IFZ"
CND4 "B0Z"|"B1Z"|"B2Z"|"B3Z"|"B0NZ"|"B1NZ"|"B2NZ"|"B3NZ"
REG "D1"|"A1"|"D2"|"A2"|"R1"|"R2"|"R3"|"PC";
INST9 "IN"|"OUT"
INST8 "ADD"|"AND"|"ANDN"|"CALL"|"CMPS"|"CMPU"|"OR"|"SET"|"SUB"|"XOR"
INST4 "LDCH"|"LDCL"|"RC"|"RO"|"SA"|"SH" 
INST0  "INV"

%%

[ \t]*                      { ; }
{NL}+		{return NL;}

[0-9]+			{yylval = atoi(yytext); return NUMBER;}

"NEVR"		{yylval = 0; return CND3;}
"IFNC"		{yylval = 1; return CND3;}
"IFNS"		{yylval = 2; return CND3;}
"IFNZ"		{yylval = 3; return CND3;}
"ALWS"		{yylval = 4; return CND3;}
"IFC"		{yylval = 5; return CND3;}
"IFS"		{yylval = 6; return CND3;}
"IFZ"		{yylval = 7; return CND3;}
"B0Z"		{yylval = 0; return CND4;}
"B1Z"		{yylval = 0; return CND4;}
"B2Z"		{yylval = 0; return CND4;}
"B3Z"		{yylval = 0; return CND4;}
"B0NZ"		{yylval = 0; return CND4;}
"B1NZ"		{yylval = 0; return CND4;}
"B2NZ"		{yylval = 0; return CND4;}
"B3NZ"		{yylval = 0; return CND4;}

"D1"		{yylval = 2; return REG;}
"A1"		{yylval = 2; return REG;}
"D2"		{yylval = 2; return REG;}
"A2"		{yylval = 2; return REG;}
"R1"		{yylval = 2; return REG;}
"R2"		{yylval = 2; return REG;}
"R3"		{yylval = 2; return REG;}
"PC"		{yylval = 2; return REG;}

"IN"		{yylval = 12 * 2^12; return INST9;}
"OUT"		{yylval = 13 * 2^12; return INST9;}
"PF"		{yylval = 14 * 2^12; return INST_PF;}

"OR"		{yylval = 0 * 2^12; return INST8;}
"XOR"		{yylval = 1 * 2^12; return INST8;}
"AND"		{yylval = 2 * 2^12; return INST8;}
"ANDN"		{yylval = 3 * 2^12; return INST8;}
"CMPU"		{yylval = 4 * 2^12; return INST8;}
"CMPS"		{yylval = 5 * 2^12; return INST8;}
"SUB"		{yylval = 6 * 2^12; return INST8;}
"ADD"		{yylval = 7 * 2^12; return INST8;}
"SET"		{yylval = 8 * 2^12; return INST8;}
"CALL"		{yylval = 9 * 2^12; return INST8;}

"SH" 		{yylval = 320 * 2^7; return INST4;}
"SA"		{yylval = 321 * 2^7; return INST4;}
"RO"		{yylval = 322 * 2^7; return INST4;}
"RC"		{yylval = 323 * 2^7; return INST4;}
"LDCH"		{yylval = 324 * 2^7; return INST4;}
"LDCL"		{yylval = 325 * 2^7; return INST4;}

"INV"		{yylval = 0; return INST0;}

".ORG"		{return ORG;}
".END"		{return END;}
".DW"		{return DW;}

%%


int yywrap() {
    return 1;
}
