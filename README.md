# VeriGoodTest
This script will generate for you the TB of a Verilog descripted module, including a truth table monitor if you want it

**I took some regex from [xfguo's tbgen](https://github.com/xfguo/tbgen/blob/master/tbgen.py)**



## Usage

```
  ./veri_good_test.py <INPUT FILENAME> [OUTPUT FILENAME]
```
The script will ask you if you want the truth table and if you want the monitor.

If you want to use it as a system program you need to move it in a directory in your `$PATH` such as `/usr/bin/`


## Examples
In the `tests` folder there are various logic gates implementations descripted by Verilog HDL. 
To run them you need to generate the TB first:

```
./veri_good_test.py tests/test1.v
```
This will generate `tb_test1.v`.

You can then choose to compile it within the script ([iverilog](https://github.com/steveicarus/iverilog)) is required).
Or you can compile it manually:
```
iverilog tests/test1.v tests/test1_tb.v -o tests/test1.out
```


When you execute the compiled file the output should be something like:
```
simtime = 0,    A = 0,  B = 0,  O = 0,
simtime = 10,   A = 0,  B = 1,  O = 0,
simtime = 20,   A = 1,  B = 0,  O = 0,
simtime = 30,   A = 1,  B = 1,  O = 1,
```
