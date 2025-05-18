import sys
from bitstring import Bits
file_path = 'test CAL.dasm'
if len(sys.argv) > 1:
    file_path = sys.argv[1]
opcodes = {'NOP': '0000', 'HLT': '0001', 'ADD': '0010', 'SUB': '0011', 'NOR': '0100', 'AND': '0101', 'XOR': '0110', 'RSH': '0111', 
           'LDI': '1000', 'ADI': '1001', 'JMP': '1010', 'BRH': '1011', 'CAL': '1100', 'RET': '1101', 'LOD': '1110', 'STR': '1111'}
print(opcodes.keys(), len(opcodes))
psuedocodes = {'INC': opcodes['ADI'], 'DEC': opcodes['ADI'], 'CMP': opcodes['SUB']}
psuedocodes2 = {'INC': 1, 'DEC': 255, 'CMP': '0000'}
definitions = {'zero': '00', 'notzero': '01', 'carry': '10', 'notcarry': '11', 
               '=': '00', '!=': '01', '>=': '10', '<': '11', 
               'z': '00', 'nz': '01', 'c': '10', 'nc': '11'}
charLookup = {' ': 0, '.': 27, '!': 28, '?':29}
for i in range(26):
    charLookup['abcdefghijklmnopqrstuvwxyz'[i]] = i+1
labels = {}
with open(file_path, 'r') as inputFile:
    i = 0
    with open(file_path.rpartition('.')[0]+'.bin', 'w') as outputFile:
        for line in inputFile:
            if line[0] == '.':
                labels[line.replace('\n','')] = i
                print(labels)
            elif line[0:8] == '#define ':
                defined = line[8:].replace('\n','').split(' ')
                definitions[defined[0]] = defined[1]
                print(definitions)
            elif line[0] in ['\n', ';']:
                pass
            else:
                i += 1
        inputFile.seek(0)
        for line in inputFile:
            if line[0] in ['.', '#', ';', '\n']:
                continue
            else:
                opcode = line[:3]
                operands = []
                for op in line[4:].replace('\n','').split(' '):
                    if len(op) == 0:
                        continue
                    if op[0] == ';':
                        break
                    operands.append(op)
                if opcode in ['ADD', 'SUB', 'XOR', 'NOR', 'AND']:
                    binary = []
                    for operand in operands:
                        if operand.startswith(';'):
                            break
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
                        if operand.startswith(';'):
                            break
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
                        if operand.startswith(';'):
                            break
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            immediate = format(int(definitions[operand]), '08b')
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                            print(operand, definitions[operand], format(int(definitions[operand]), '08b'))
                        elif operand.startswith('"'):
                            immediate = format(charLookup[operand[1].lower()], '08b')
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                        elif operand.startswith('0b'):
                            immediate = format(int(operand, base=2), '08b')
                            print(immediate)
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                        else:
                            immediate = format(int(operand), '08b')
                            binary.append(immediate[:4])
                            binary.append(immediate[4:])
                    while len(binary) < 3:
                        binary.append('0000')
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['INC', 'DEC', 'CMP']:
                    binary = []
                    for operand in operands:
                        if operand.startswith(';'):
                            break
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(format(int(definitions[operand]), '04b'))
                            print(operand, definitions[operand], format(int(definitions[operand]), '04b'))
                        else:
                            binary.append(operand)
                    binary.append(format(int(psuedocodes2[opcode]), '08b' if isinstance(psuedocodes2[opcode], int) else '04b'))
                    #binary.append(format(int(operand[1:]), '04b'))
                    outputFile.write(psuedocodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['JMP', 'BRH', 'CAL']:
                    binary = []
                    if opcode in ['JMP', 'CAL']:
                        binary.append('00')
                    for operand in operands:
                        if operand.startswith(';'):
                            break
                        if operand.isnumeric():
                            binary.append(format(int(operand), '010b'))
                        elif operand in definitions:
                            binary.append(definitions[operand])
                            print(operand, definitions[operand])
                        elif operand in labels:
                            binary.append(format(int(labels[operand]), '010b'))
                            print(operand, labels[operand], format(int(labels[operand]), '010b'))
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['LOD', 'STR']:
                    binary = []
                    for operand in operands:
                        if operand.startswith(';'):
                            break
                        if operand.startswith('r') and operand[1].isnumeric():
                            binary.append(format(int(operand[1:]), '04b'))
                        elif operand in definitions:
                            binary.append(Bits(int=int(definitions[operand]), length=4).bin)
                            print(operand, definitions[operand], Bits(int=int(definitions[operand]), length=4).bin)
                        elif operand.startswith('"'):
                            binary.append(format(charLookup[operand[1].lower()], '04b'))
                        else:
                            #binary.append(format(int(operand), '04b'))
                            binary.append(Bits(int=int(operand), length=4).bin)
                    if len(binary) < 3:
                        binary.append('0000')
                    #binary.append(format(int(operand[1:]), '04b'))
                    outputFile.write(opcodes[opcode] + ''.join(binary) + '\n')
                elif opcode in ['NOP', 'HLT', 'RET']:
                    outputFile.write(opcodes[opcode] + format(0, '012b') + '\n')
                else:
                    raise ValueError(f'Opcode {opcode} Not Recognized')
                i += 1