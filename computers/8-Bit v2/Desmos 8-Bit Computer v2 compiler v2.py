file_path = 'test Flags.dasm'
opcodes = {'ADD': '0010','SUB': '0011','XOR': '0100','NOR': '0101','AND': '0110','RSH': '0111', 'LDI': '1000', 'ADI': '1001', 'JMP': '1010'}
psuedocodes = {'INC': opcodes['ADI'], 'DEC': opcodes['ADI']}
psuedocodes2 = {'INC': 1, 'DEC': 2**8-1}
definitions = {}
labels = {}
with open(file_path, 'r') as inputFile:
    i = 0
    with open(file_path.rpartition('.')[0]+'.bin', 'w') as outputFile:
        for line in inputFile:
            if line[0] == '.':
                labels[line[1:].replace('\n','')] = i
                print(labels)
            elif line[0:8] == '#define ':
                defined = line[8:].replace('\n','').split(' ')
                definitions[defined[0]] = defined[1]
                print(definitions)
            else:
                opcode = line[:3]
                operands = line[4:].replace('\n','').split(' ')
                if opcode in ['ADD', 'SUB', 'XOR', 'NOR', 'AND']:
                    binary = []
                    for operand in operands:
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(format(int(definitions[operand]), '04b'))
                            print(operand, definitions[operand], format(int(definitions[operand]), '04b'))
                        else:
                            binary.append(operand)
                    while len(binary) < 3:
                        binary.append('0000')
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['RSH']:
                    binary = []
                    for i, operand in enumerate(operands):
                        if i == 1:
                            binary.append('0000')
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(format(int(definitions[operand]), '04b'))
                            print(operand, definitions[operand], format(int(definitions[operand]), '04b'))
        
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['LDI', 'ADI']:
                    binary = []
                    for operand in operands:
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            immediate = format(int(definitions[operand]), '08b')
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                            print(operand, definitions[operand], format(int(definitions[operand]), '08b'))
                        else:
                            immediate = format(int(operand), '08b')
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                    while len(binary) < 3:
                        binary.append('0000')
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['INC', 'DEC']:
                    binary = []
                    for operand in operands:
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(format(int(definitions[operand]), '04b'))
                            print(operand, definitions[operand], format(int(definitions[operand]), '04b'))
                        else:
                            binary.append(operand)
                    binary.append(format(psuedocodes2[opcode], '08b'))
                    #binary.append(format(int(operand[1:]), '04b'))
                    outputFile.write(psuedocodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['JMP']:
                    binary = []
                    binary.append('00')
                    for operand in operands:
                        if operand.isnumeric():
                            binary.append(format(int(operand), '010b'))
                        elif operand in labels:
                            binary.append(format(int(labels[operand]), '010b'))
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode == 'NOP':
                    outputFile.write(format(0, '016b') + '\n')
                else:
                    raise ValueError(f'Opcode {opcode} Not Recognized')
                i += 1