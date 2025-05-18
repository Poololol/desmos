import * as vscode from 'vscode';

const DASM_MODE: vscode.DocumentFilter = { language: 'desmosassembly', scheme: 'file' };
const opcodes = ['NOP', 'HLT', 'ADD', 'SUB', 'NOR', 'AND', 'XOR', 'RSH', 'LDI', 'ADI', 'JMP', 'BRH', 'CAL', 'RET', 'LOD', 'STR']
const operands = ['No Params', 'No Params', 
    'Reg A, Reg B, Reg C', 
    'Reg A, Reg B, Reg C', 
    'Reg A, Reg B, Reg C', 
    'Reg A, Reg B, Reg C',
    'Reg A, Reg B, Reg C',
    'Reg A, Reg C',
    'Reg A, Immediate',
    'Reg A, Immediate',
    'Address',
    'Condition Code, Address',
    'Address',
    'No Params',
    'Reg A, Reg B, Offset',
    'Reg A, Reg B, Offset'
]
const psuedos = [
    'Does nothing',
    'Stops the clock',
    'C = A + B',
    'C = A - B',
    'C = !(A | B)',
    'C = A & B',
    'C = A ^ B',
    'C = A >> 1',
    'A = Immediate',
    'A = A + Immediate',
    'PC = Address',
    'If Condition: PC = Address',
    'PC = Address, Push PC + 1',
    'PC = Pop Stack',
    'B = Mem[A + offset]',
    'Mem[A + offset] = B'
]

export function activate(ctx: vscode.ExtensionContext): void {
    ctx.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            DASM_MODE, new DasmCompletionItemProvider(), '.', '\"'));
    ctx.subscriptions.push(
        vscode.languages.registerHoverProvider(
            DASM_MODE, new DasmHoverProvider()));
    ctx.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            DASM_MODE, new DasmSignatureHelpProvider(), '(', ','));
    
}


class DasmCompletionItemProvider implements vscode.CompletionItemProvider {
    public provideCompletionItems(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken):
        vscode.CompletionItem[] {
            let competions = [new vscode.CompletionItem('#define')]
            for (let index = 0; index <= 15; index++) {
                competions.push(new vscode.CompletionItem('r' + index))
            }
            opcodes.forEach(element => {
                competions.push(new vscode.CompletionItem(element))
            });
            return competions;
    }
}

class DasmHoverProvider implements vscode.HoverProvider {
    public provideHover(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken):
        vscode.Hover {
            let selectedTokenRange = document.getWordRangeAtPosition(position, /\.?((-?\d*\d\.\w*)|([^\.\`\~\@\%\^\&\*\(\)\-\+\[\{\]\}\\\|\;\:\,\/\?\s]+))/g);
            let selectedToken = document.getText(selectedTokenRange);
            let definition = '';
            let arr: string[][] = []
            for (let index = 0; index < opcodes.length; index++) {
                arr.push([opcodes[index], operands[index] + ':\n\n' + psuedos[index]])
            }
            let opcodeDefs = new Map(arr)
            if (Array.from(opcodeDefs.keys()).some(arrStr => selectedToken === arrStr)) {
                definition = 'Opcode: ' + selectedToken + '\n\n' + opcodeDefs.get(selectedToken);
            }
            if (selectedToken.charAt(0) == '.') {
                definition = 'Label: ' + selectedToken.substring(1);
            }
            if (selectedToken.charAt(0) == 'r') {
                definition = 'Register ' + selectedToken.substring(1);
            }
            
            return new vscode.Hover(definition);
    }
}
class DasmSignatureHelpProvider implements vscode.SignatureHelpProvider {
    public provideSignatureHelp(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.SignatureHelpContext):
        vscode.SignatureHelp {
            let sigHelp = new vscode.SignatureHelp();
            sigHelp.signatures = context.triggerCharacter ? [new vscode.SignatureInformation('Test', 'this is a test: ' + context.triggerCharacter)] : []
            return sigHelp;
    }
}