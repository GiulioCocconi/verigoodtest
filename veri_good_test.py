#!/usr/bin/python

# Part of the logic and some of the regex are based on Xiongfei Guo's tbgen
import logging
import re
import sys
import os
import itertools

debug = False
logging.basicConfig(
        format = '[%(levelname)s]: %(message)s',
        level  = logging.DEBUG if debug else logging.INFO,
        )

def usage():
    print(f"USAGE: {sys.argv[0]} <INPUT FILENAME> [OUTPUT TB FILENAME]")
    print(f"\"{sys.argv[0]} -h\" prints this message")

def goodbye(exit_status, close = None):
    print("\n")

    if exit_status == 0:
        print("Hope you've had fun using this program!")

    print("If you've found any bug please open an issue on the project's github page :-)")

    if (close != None):
        close()
    sys.exit(exit_status);


class Generator(object):
    def __init__(self, input_filename, output_filename, bin_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.bin_filename = bin_filename
        self.input_file = None
        self.output_file = None
        logging.debug(f"Generator has been configured to read from {input_filename} and write to {output_filename}")

        self.input_data = ""; # The content of the input file
        self.module_name = "";
        self.pin_list = []

        self.truth_not_supported = False # If the input file contains features that aren't supported by the truth table generator the user has to write his own test

        self.open_input()
        self.clean_input()

        self.parser()
        self.open_output()

    def open_input(self):
        try:
            self.input_file = open(self.input_filename, 'r')
            self.input_data = self.input_file.read()
            logging.debug("Input opened")
            logging.debug("Content:\n" + self.input_data)
        except Exception as e:
            logging.error(f"The generator is unable to read {self.input_filename}")
            logging.error(str(e))
            goodbye(1, self.close)

    def clean_input(self):
        '''
        Removes all useless tokens from input file
        '''

        logging.debug("Cleaning input")

        ## clean "//..."
        self.input_data = re.sub(r"//[^\n^\r]*", '', self.input_data)

        ## clean "/*...*/"
        self.input_data = re.sub(r"/\*.*\*/", '', self.input_data)

        ## clean tables
        self.input_data = re.sub(r'    +', ' ', self.input_data)

        ## Remove empty lines
        self.input_data = re.sub(r'\n\s*\n', '\n', self.input_data, re.MULTILINE)

        logging.debug("Content:\n" + self.input_data)

    def parser(self):
        logging.info(f"Parsing {self.input_filename}...")
        self.parse_module_name()
        self.parse_io()

    def parse_module_name(self):
        logging.debug("Parsing module name...")

        mod_pattern_string = r"module[\s]([^\(\)\;\n\s]*)"
        module_result = re.findall(mod_pattern_string, self.input_data)
        self.module_name = module_result[0]

        logging.debug(f"Found module name {self.module_name}")

    def parse_io(self):
        '''
        Parses all IO ports
        '''

        ## Possibilities:
        ## input a,
        ## input [7:0] a,
        ## input a, b,
        ## input [7:0] a, b,

        tb_translation_type = ['reg', 'wire']
        for item in re.findall(r'(input|output|inout)[\s](\[[^\[]*\])?([^\\[\]\n\\;\)]*)(\[[^\[]*\])?', self.input_data):
            mod = list(item)
            logging.debug(f"New Item: {item}")

            mod[2] = mod[2].replace(" ", "")

            # For "input a,b," io_names will be ["a","b"], that should preserve buses and arrays
            io_names = mod[2].split(sep=",")
            io_names = [x for x in io_names if x] # Remove empty elements
            logging.debug(f"new io_names found: {io_names}")

            for port_name in io_names:
                temp_io_item = (item[0], item[1], port_name, item[3]) # (direction, bus, name, array)

                # Find TB type
                if item[0] == "input":
                    io_type = 0
                elif item[0] == "inout":
                    io_type = 0
                    self.truth_not_supported = True
                elif item[0] == "output":
                    io_type = 1
                else:
                    # Handle error
                    logging.error(f"Type {item[0]} is unknown")
                    goodbye(1, self.close)

                isBus = item[1] != ''
                isArray = item[3] != ''

                if (isBus or isArray):
                    self.truth_not_supported = True

                def_item = (tb_translation_type[io_type], item[1], port_name, item[3])
                logging.debug(f"New def_item is: {def_item}")

                self.pin_list.append(def_item)
        logging.debug(f"The generator's pin list is now {str(self.pin_list)}")

    def open_output(self):
        try:
            self.output_file = open(self.output_filename, "w");
            logging.debug("Output opened")
        except Exception as e:
            logging.error(f"Generator can't write to {self.output_filename}")
            print(e)
            goodbye(1, self.close())

    def print_line(self, string, debug_msg = None):
        if self.output_file == None:
            logging.error("Output file is not opened!")
            goodbye(1, self.close)

        if debug_msg == None:
            debug_msg = string

        if string != "":
            logging.debug(f"Printing: {debug_msg}")
        print(string, file=self.output_file)

    def print_file(self):
        '''
        Calls all the function that will write the sections of the TB file
        '''

        self.print_head()
        self.print_io()
        self.print_dut();
        self.print_truth_table();
        self.print_monitor()
        self.print_end();

    def print_head(self):
        '''
        Prints the initial comment and the module declaration
        '''

        self.print_line("// A part of this file was autogenerated by verigoodtest, if you find any bug please open an issue on github", "head comment")
        self.print_line(f"`include \"{self.input_filename}\"", "include directive")
        self.print_line(f"module tb_{self.module_name};", "module line")

    def print_io(self):
        '''
        Prints the pins section
        '''
        self.print_line("")
        self.print_line("// Pins", "Pins")

        for pin in self.pin_list:
            pin_str = ""

            for attribute in pin:
                if attribute:
                    pin_str += (attribute + " ")

            pin_str = pin_str[:-1]
            pin_str += ";"
            self.print_line(pin_str)

        self.print_line("")

    def print_dut(self):
        dut_string = f"{self.module_name} dut("

        for pin in self.pin_list:
            dut_string += f".{pin[2]}({pin[2]}), "

        dut_string = dut_string[:-2] # remove the trailing ', '

        dut_string += ");"


        self.print_line(dut_string)
        self.print_line("")


    def print_truth_table(self):
        '''
        If the user wants the truth table and it's supported it writes one
        '''

        if self.truth_not_supported:
            logging.info("You've used features not supported by this program's truth table generator, you'll have to write your own truth table")
            return

        choose = input("Do you need a truth table test? [Y/N] ")

        if choose != "Y" and choose != "y":
            logging.info("You chose to not let me write a truth table for you :-(")
            return

        self.print_line("// Truth table")
        self.print_line("initial begin")
        # Find input pins
        input_pins = []
        for pin in self.pin_list:
            if pin[0] == "reg":
                logging.debug(f"pin[3] is input (type reg in TB)")
                input_pins.append(pin)

        combinations = list(map(list, itertools.product([0, 1], repeat=len(input_pins)))) # Array of all the binary combinations of all inputs
        combinations.pop(0) # removes [0, ..., 0] combo, that's handled separately


        toBePrinted = "" # Print buffer for pins = 0
        for pin in input_pins:
            toBePrinted += f"{pin[2]} = 0; "

        self.print_line(toBePrinted)

        for combo in combinations:
            combo_str = "#10 "
            for i, pin in enumerate(input_pins):
                combo_str += f"{pin[2]} = {combo[i]}; "
            self.print_line(combo_str)

        self.print_line("end")
        self.print_line("")


    def print_monitor(self):

        choose = input("Do you need a monitor? [Y/N] ")

        if choose != "Y" and choose != "y":
            logging.info("You chose to not let me write a monitor for you :-(")
            return

        self.print_line("initial begin")

        monitor_str = "$monitor(\"simtime = %g, \\t"
        attributes_str = "$time, "

        for pin in self.pin_list:
            monitor_str += f"{pin[2]} = %b, \\t"
            attributes_str += f"{pin[2]}, "

        # Remove trailing ", "
        monitor_str = monitor_str[:-2]
        attributes_str = attributes_str[:-2]

        monitor_str += "\", "
        attributes_str += ");"

        monitor_str += attributes_str;
        self.print_line(monitor_str)

        self.print_line("end")
        self.print_line("")

    def print_end(self):
        self.print_line("")
        self.print_line("endmodule")

    def gen_bin(self):
        if not self.truth_not_supported:
            choose = input("Will you let me compile the testbench with IVERILOG? [Y/N] ")

            if choose != "Y" and choose != "y":
                logging.info("You chose to not let me generate the bin file for you :-(")
                return

            compile_command = f"iverilog {self.output_filename} -o {self.bin_filename}"

            logging.debug(f"The compile command is {compile_command}")

            logging.info(f"Running iverilog to compile to {self.bin_filename}...")
            os.system(compile_command)

            logging.info("Running the compiled bin...\n")
            os.system(f"vvp {self.bin_filename}")



    def close(self):
        if (self.input_file != None):
            self.input_file.close()

        if (self.output_file != None):
            self.output_file.close()

        logging.debug("Generator closed")


if __name__ == "__main__":

    # If the program hasn't got the right number of args
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        logging.error("Incorrect number of arguments")
        usage()
        goodbye(1)

    if sys.argv[1] in ["-h", "--help"]:
        usage()
        goodbye(0)

    input_filename = sys.argv[1]

    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        output_filename = input_filename[:-2] + "_tb.v"
        logging.info(f"Writing to {output_filename}")

    bin_filename = input_filename[:-2] + ".out"

    generator = Generator(input_filename, output_filename, bin_filename)

    generator.print_file()
    generator.close()
    generator.gen_bin()
    goodbye(0)
