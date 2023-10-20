%{  
    #include <stdio.h>
    int PC = 0;

    void yyerror(const char *s);
    int yylex();
    int yywrap();

%}

%token ORG END DW NL NUMBER CND3 CND4 REG INST9 INST8 INST4 INST0 INST_PF


%%

FILE : PRG END { printf("End of program reached.\n"); YYACCEPT;}

PRG : %empty
     | PRG INST_V NL { PC++;}
     | PRG ORG NUMBER NL	{PC = $3;} 
     ;

INST_V : INST9 NUMBER REG 	{ printf("INST9 NUMBER REG,  %X, %X,%X\n", $1, $2, $3); }

     | INST8 NUMBER REG 	{ printf("INST8 NUMBER REG, %X, %X, %X\n", $1, $2, $3); }// Ambigu 
     | INST8 REG REG     	{ printf("INST8 REG REG, %X, %X, %X\n", $1, $2, $3); }
     | INST8 NUMBER REG CND3 	{ printf("INST8 NUMBER REG CND3, %X, %X, %X, %X\n", $1, $2, $3, $4); }
     | INST8 REG REG CND3 	{ printf("INST8 REG REG CND3, %X, %X, %X, %X\n", $1, $2, $3, $4); }
     | INST8 REG REG CND4 	{ printf("INST8 REG REG CND4, %X, %X, %X, %X\n", $1, $2, $3, $4); }

     | INST4 NUMBER REG     	{ printf("INST4 NUMBER REG, %X, %X, %X\n", $1, $2, $3); }
     | INST4 REG REG     	{ printf("INST4 REG REG, %X, %X, %X\n", $1, $2, $3); }
     | INST4 NUMBER REG CND3 	{ printf("INST4 NUMBER REG CND3, %X, %X, %X, %X\n", $1, $2, $3, $4); }
     | INST4 REG REG CND3 	{ printf("INST4 REG REG CND3, %X, %X, %X, %X\n", $1, $2, $3, $4); }
     | INST4 REG REG CND4 	{ printf("INST4 REG REG CND4, %X, %X, %X, %X\n", $1, $2, $3, $4); }

     | INST0 			{ printf("INST0, %X\n", $1); }

     | DW NUMBER		{printf("DW : %X \n",$1);}
     ;


%%


int main(){
    return yyparse();
}

void yyerror(const char* msg) {
    fprintf(stderr, "%s\n", msg);
}
