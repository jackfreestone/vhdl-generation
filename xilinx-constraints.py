import csv

# complete before running
project_name = ''
company = ''
engineer = ''
input_file = 'io.csv'

physical = open('./work/physical.xdc', 'w')
timing = open('./work/timing.xdc', 'w')
vhd_file = ('./work/%s_top.vhd' % project_name)
top_vhd = open(vhd_file, 'w')

vhd_comment = '--'
xdc_comment = '#'

net = 0
pin = 1
dir = 2


def get_io_data(filename):
    imported_data = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # change this to import all io data and return
        fieldnames = reader.next()
        for i, name in enumerate(fieldnames):
            fieldnames[i] = fieldnames[i].upper()
        net_index = fieldnames.index('NET')
        pin_index = fieldnames.index('PIN')
        dir_index = fieldnames.index('DIR')
        for row in reader:
            imported_data.append(row)
    csvfile.close()
    for row in imported_data:
        row[net_index] = make_vhdl_legal(row[net_index])
    return imported_data, net_index, pin_index, dir_index


def write_config_settings(filename, spi_width, spi_mode, spi_speed):
    filename.write('# Configuration settings\n')
    filename.write('set_property BITSTREAM.CONFIG.SPI_BUSWIDTH %d [current_design]\n' % spi_width)
    filename.write('set_property CONFIG_MODE SPIx%d [current_design]\n' % spi_mode)
    filename.write('set_property BITSTREAM.CONFIG.CONFIGRATE %d [current_design]\n' % spi_speed)


def write_io_constraints(port_list, fileout, net_index, pin_index):
    physical.write('\n# Design io\n')
    for row in port_list:
        net_name = row[net_index].upper()
        pin_num = row[pin_index].upper()
        fileout.write('set_property PACKAGE_PIN %s [get_ports {%s}]\n' % (pin_num, net_name))


def write_divider(fileout, comment):
    for i in range(0, 41):
        fileout.write('%s' % comment)
    fileout.write('\n')


def write_file_header(fileout, comment, proj_name, co, eng):
    import time
    create_date = time.strftime('%d %b %Y %H:%M:%S %p')
    write_divider(fileout, comment)
    fileout.write('%s Company: %s\n' % (comment, co))
    fileout.write('%s Engineer: %s\n' % (comment, eng))
    fileout.write('%s \n' % comment)
    fileout.write('%s Create Date: %s\n' % (comment, create_date))
    fileout.write('%s Design Name: %s FPGA\n' % (comment, proj_name))
    fileout.write('%s Module Name: %s_top - rtl\n' % (comment, proj_name))
    fileout.write('%s Project Name: %s\n' % (comment, proj_name))
    fileout.write('%s Target Devices:\n' % comment)
    fileout.write('%s Tool Versions:\n' % comment)
    fileout.write('%s Description:\n' % comment)
    fileout.write('%s \n\n' % comment)
    fileout.write('%s Revision:\n' % comment)
    fileout.write('%s 0.01 - File generated\n' % comment)
    fileout.write('%s Additional Comments:\n' % comment)
    fileout.write('%s \n' % comment)
    write_divider(fileout, comment)


def remove_first_char(string):
    return string[1:]


def remove_last_char(string):
    return string[:(len(string)-1)]


def make_vhdl_legal(string):
    new_str = ''
    upper_case = string.upper()
    letters = 'ABCDEFGHIJKLMNOPQRSTUQWXYZ'
    while upper_case[0] not in letters:
        upper_case = remove_first_char(upper_case)
    for i, char in enumerate(upper_case):
        if char in letters:
            new_str += char
        elif char == '_':
            if i == (len(upper_case) - 1):
                pass
            else:
                new_str += char
        elif char.isdigit():
            new_str += char
        else:
            if i == (len(upper_case) - 1):
                pass
            else:
                # print("Warning: Replacing illegal character '%s' in '%s' with '_'" % (char, string))
                new_str += '_'
    return new_str


def write_vhdl_entity(fileout, port_list, project, net_index, dir_index):
    port_indent = '       '
    fileout.write('entity %s_top is\n' % project)
    fileout.write('Port ( ')
    for idx, row in enumerate(port_list):
        port = row[net_index].upper()
        if row[dir_index] == 'o' or row[dir_index] == 'O':
            port_dir = 'out'
        elif row[dir_index] == 'i' or row[dir_index] == 'I':
            port_dir = 'in'
        else:
            port_dir = 'inout'
        if idx == 0:
            fileout.write('%s : %s STD_LOGIC;\n' % (port, port_dir))
        elif idx == (len(port_list) - 1):
            fileout.write('%s%s : %s STD_LOGIC  );\n\n' % (port_indent, port, port_dir))
        else:
            fileout.write('%s%s : %s STD_LOGIC;\n' % (port_indent, port, port_dir))
    fileout.write('end entity %s_top;\n' % project)
    write_divider(fileout, vhd_comment)


def write_vhdl_architecture(fileout, project):
    fileout.write('\narchitecture RTL of %s_top is\n' % project)
    fileout.write('  -- constant, component and signal declarations here \n')
    fileout.write('\nbegin\n')
    fileout.write('  -- instances etc. here \n')
    fileout.write('\nend architecture RTL;')


def write_vhdl_libs(fileout):
    fileout.write('LIBRARY IEEE;\n')
    fileout.write('USE IEEE.STD_LOGIC_1164.ALL;\n\n')


# get data from csv
io_data, net, pin, dir = get_io_data(input_file)

# write physical constraints file
write_file_header(physical, vhd_comment, project_name, company, engineer)
write_config_settings(physical, 2, 2, 16)
write_io_constraints(io_data, physical, net, pin)

# write vhdl top level
write_file_header(top_vhd, vhd_comment, project_name, company, engineer)
write_vhdl_libs(top_vhd)
write_vhdl_entity(top_vhd, io_data, project_name, net, dir)
write_vhdl_architecture(top_vhd, project_name)
