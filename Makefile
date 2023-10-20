y8asm: y8.lex.c y8.tab.c
	/usr/local/Cellar/gcc/13.2.0/bin/gcc-13 -o y8asm y8.lex.c y8.tab.c
        
y8.lex.c: y8asm.l y8.tab.c
	flex -o y8.lex.c y8asm.l
             
y8.tab.c: y8asm.y
	/usr/local/Cellar/bison/3.8.2/bin/bison -o y8.tab.c -vd y8asm.y

clean: 
	rm y8.lex.c y8.tab.c y8.tab.h y8.output
