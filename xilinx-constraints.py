import csv

input_file = 'io.csv'

physical = open('./work/physical.xdc', 'w')
timing = open('./work/timing.xdc', 'w')

net = 0
pin = 1
dir = 2


def write_config_settings(filename, spi_width, spi_mode, spi_speed):
    filename.write('# Configuration settings\n')
    filename.write('set_property BITSTREAM.CONFIG.SPI_BUSWIDTH %d [current_design]\n' % spi_width)
    filename.write('set_property CONFIG_MODE SPIx%d [current_design]\n' % spi_mode)
    filename.write('set_property BITSTREAM.CONFIG.CONFIGRATE %d [current_design]\n' % spi_speed)


def get_fieldnames(filename):
    with open(filename, 'rb') as csvfile:
        # fieldnames = ['netname', 'direction']
        reader = csv.reader(csvfile, delimiter=',')
        fieldnames = reader.next()
        csvfile.close()

    net_index = fieldnames.index('NET')
    pin_index = fieldnames.index('PIN')
    dir_index = fieldnames.index('DIR')
    return net_index, pin_index, dir_index


def write_io_constraints(filein, fileout, net_index, pin_index):
    physical.write('\n# Design io\n')
    with open(filein, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[pin_index] != 'PIN':
                fileout.write('set_property PACKAGE_PIN %s [get_ports {%s}]\n' % (row[pin_index], row[net_index]))


net, pin, dir = get_fieldnames(input_file)
write_config_settings(physical, 2, 2, 16)
write_io_constraints(input_file, physical, net, pin)