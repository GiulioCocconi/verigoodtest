# VeriGoodTest
This script will generate for you the TB of a Verilog descripted module, including a truth table monitor if you want it

**I took all the regex from [xfguo's tbgen](https://github.com/xfguo/tbgen/blob/master/tbgen.py)**


## Usage

```
  ./veri_good_test.py <INPUT FILENAME> [OUTPUT FILENAME]
```
The script will ask you if you want the truth table and if you want the monitor.


## Tests
In the test folder there's the Verilog implementation of an AND gate, built using NAND. 
You need to generate the TB first:

```
./veri_good_test.py tests/AND.v
```
The script will generate `tb_AND.v`, 
then you'll need to compile the Verilog implementation and the TB (I recommend to use [iverilog](https://github.com/steveicarus/iverilog)):

```
iverilog tests/AND.v tests/tb_AND.v -o AND.out
```


When you execute the compiled file the output should be something like:
```
simtime = 0,    A = 0,  B = 0,  O = 0,
simtime = 10,   A = 0,  B = 1,  O = 0,
simtime = 20,   A = 1,  B = 0,  O = 0,
simtime = 30,   A = 1,  B = 1,  O = 1,
```
