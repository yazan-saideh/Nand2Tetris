// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
//initialize min and max to first array value
@R14
A=M
D=M
@MIN
M=D
@MAX
M=D

//initialize the addresses of min and max to the address of first element 
@R14
D=M
@MINI
M=D
@MAXI
M=D

//counter i=1
@i
M=1

(LOOP)//loop that terminates if(i==R15)
@R15
D=M
@i
D=D-M
@STOP
D;JEQ

//compare i-th element with min
@R14
D=M
@i
D=D+M
A=D
D=M

//if the difference is positive then skip
@MIN
D=D-M
@SKIPMIN
D;JGE

//else the difference is negative and add the difference(negative) to min
@MIN
M=M+D
//save the new address of new min array element
@R14
D=M
@i
D=D+M
@MINI
M=D

(SKIPMIN)
//compare i-th element with MAX
@R14
D=M
@i
D=D+M
A=D
D=M

//if the difference is negative then skip
@MAX
D=D-M
@SKIPMAX
D;JLE

//else ADD the difference to MAX
@MAX
M=M+D
//save the new address of new max array element
@i
D=M
@R14
D=M
@i
D=D+M
@MAXI
M=D

(SKIPMAX)
//i=i+1
@i
M=M+1
@LOOP
0;JMP

//after finishing loop swap max and min in array
(STOP)
@MAX
D=M
@MINI
A=M
M=D

@MIN
D=M
@MAXI
A=M
M=D
//infinite loop
(END)
@END
0;JMP
