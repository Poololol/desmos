file_path = 'test2.dasm'
opcodes = {'ADD': '0010','SUB': '0011','XOR': '0100','NOR': '0101','AND': '0110','RSH': '0111'}
definitions = {}
labels = {}
with open(file_path, 'r') as inputFile:
    i = 0
    with open(file_path.rpartition('.')[0]+'.out', 'w') as outputFile:
        for line in inputFile:
            if line[0] == '.':
                labels[line[1:].replace('\n','')] = i
            elif line[0] == '#':
                defines = line[8:].replace('\n','').split(' ')
                definitions[defines[0]] = defines[1]
                print(definitions)
            else:
                opcode = line[:3]
                operands = line[4:].replace('\n','').split(' ')
                if opcode in ['ADD', 'SUB', 'XOR', 'NOR', 'AND', 'RSH']:
                    binary = []
                    for operand in operands:
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(format(int(definitions[operand]), '04b'))
                            print(operand, definitions[operand], format(int(definitions[operand]), '04b'))
                        elif operand in labels:
                            binary.append(format(int(labels[operand]), '010b'))
                            print(operand, labels[operand], format(int(labels[operand]), '010b'))
                        else:
                            binary.append(operand)
                    while len(binary) < 3:
                        binary.append('0000')
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode == 'NOP':
                    outputFile.write(format(0, '016b') + '\n')
                else:
                    ...
                
            i += 1