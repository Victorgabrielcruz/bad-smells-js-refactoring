from pathlib import Path
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/relatorio-bad-smells-refatoracao-segura.pdf'
BLUE, TEAL, GRAY = HexColor('#17324D'), HexColor('#007C83'), HexColor('#475569')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleReport', fontName='Helvetica-Bold', fontSize=28, leading=34, textColor=BLUE, spaceAfter=20))
styles.add(ParagraphStyle(name='SectionReport', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=BLUE, spaceAfter=14))
styles.add(ParagraphStyle(name='SubReport', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=TEAL, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name='BodyReport', fontName='Helvetica', fontSize=10.2, leading=14.5, textColor=GRAY, spaceAfter=8))
styles.add(ParagraphStyle(name='SmallReport', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=GRAY, spaceAfter=6))
styles.add(ParagraphStyle(name='CodeReport', fontName='Courier', fontSize=8.2, leading=11, textColor=BLUE, backColor=HexColor('#F0F4F8'), borderPadding=10, spaceBefore=4, spaceAfter=12))
styles.add(ParagraphStyle(name='CellReport', fontName='Helvetica', fontSize=9.1, leading=12, textColor=GRAY))
styles.add(ParagraphStyle(name='CellHeadReport', fontName='Helvetica-Bold', fontSize=9.1, leading=12, textColor=white))
story=[]
def p(text, style='BodyReport'):
    story.append(Paragraph(text, styles[style]))
def h(text): p(text, 'SectionReport')
def sub(text): p(text,'SubReport')
def code(text): story.append(Preformatted(text,styles['CodeReport']))
def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL); canvas.setLineWidth(1)
    canvas.line(52, 43, A4[0]-52, 43)
    canvas.setFont('Helvetica',8); canvas.setFillColor(GRAY)
    canvas.drawString(52,29,'Teste de Software | Victor Gabriel Cruz Pereira')
    canvas.drawRightString(A4[0]-52,29,f'{doc.page} / 4')
    canvas.restoreState()

# 1. Capa
p('PUC MINAS', 'SubReport')
p('Engenharia de Software<br/>Unidade Lurdes', 'SmallReport')
story.append(Spacer(1,90))
p('Detecção de Bad Smells<br/>e Refatoração Segura','TitleReport')
p('Análise, refatoração e validação de um gerador de relatórios JavaScript','BodyReport')
story.append(Spacer(1,65))
p('<b>Disciplina:</b> Teste de Software')
p('<b>Aluno:</b> Victor Gabriel Cruz Pereira')
p('<b>Matrícula:</b> 861270')
story.append(Spacer(1,65))
p('<b>Projeto:</b> bad-smells-js-refactoring<br/><b>Data:</b> 1 de novembro de 2026')
p('Fork: <link href="https://github.com/Victorgabrielcruz/bad-smells-js-refactoring" color="#007C83">github.com/Victorgabrielcruz/bad-smells-js-refactoring</link>', 'SmallReport')
p('Relatório elaborado a partir do código preservado e das evidências reais das fases de análise e validação.', 'SmallReport')
story.append(PageBreak())

# 2. Análise e ferramenta
h('1. Diagnóstico do código original')
p('Os três smells abaixo foram identificados em <b>src/ReportGenerator.js</b>, no método <b>generateReport</b>. A inspeção manual e a análise estática são complementares.')
sub('Método longo e responsabilidades misturadas | linhas 11-68')
p('O método monta cabeçalho, seleciona itens, altera prioridade, formata linhas, soma valores e fecha o relatório. Essa concentração amplia o impacto de mudanças e obriga os testes a preparar e verificar o relatório completo para exercitar regras isoladas. Técnica: <b>Extract Method</b>, com auxiliares internos ao módulo.')
sub('Condicionais complexas | linhas 27-54, especialmente 43-52')
p('Papel do usuário, limite de valor e formato são decididos em ramos aninhados. A manutenção exige conferir combinações ADMIN/USER, CSV/HTML e valores de fronteira. Técnica: <b>Decompose Conditional</b> e cláusula de guarda, separando visibilidade e renderização.')
sub('Duplicação de código | linhas 35-37 e 46-48')
p('A linha CSV é repetida nos ramos ADMIN e USER; a soma também aparece nas linhas 37, 41, 48 e 51. Alterações podem divergir entre caminhos, exigindo testes redundantes para detectar inconsistências. Técnica: extrair a geração da linha e centralizar a totalização.')
sub('Resultado real do ESLint antes da refatoração')
img = PILImage.open(ROOT / 'docs/evidencias/eslint-antes-captura-editor.png')
# Recorte exclusivamente de enquadramento; texto e métricas não são alterados.
img.crop((76,90,1300,350)).save(ROOT / 'docs/evidencias/eslint-antes-captura-editor-recorte.png')
story.append(Image(str(ROOT/'docs/evidencias/eslint-antes-captura-editor-recorte.png'),width=487,height=487*260/1224))
p('Figura 1. Captura real da saída de npx eslint src/ preservada em analise-estatica-original.txt, aberta no editor nesta entrega. Recorte de enquadramento; não é uma captura histórica do terminal.', 'SmallReport')
p('O <b>SonarJS</b> quantificou a complexidade cognitiva em <b>27</b> (limite <b>15</b>, linha 11:3) e apontou uma condicional unificável (43:14). Acrescentou medida e localização precisa aos achados manuais. Não emitiu diagnóstico de funções idênticas: blocos CSV repetidos não equivalem a funções inteiras iguais.', 'BodyReport')
story.append(PageBreak())

# 3. Refatoração
h('2. Refatoração do problema prioritário')
p('A prioridade foi decompor <b>generateReport</b>, que concentrava as decisões e tarefas. O arquivo original foi preservado; a implementação está em <b>src/ReportGenerator.refactored.js</b>, com o mesmo export, construtor, propriedade db e assinatura pública.')
sub('Antes | original, linhas 43-54')
original=(ROOT/'src/ReportGenerator.js').read_text(encoding='utf8').splitlines()
code('\n'.join(line[6:] if line.startswith('      ') else line for line in original[42:54]))
sub('Depois | refatorado, linhas 14-33')
ref=(ROOT/'src/ReportGenerator.refactored.js').read_text(encoding='utf8').splitlines()
code('\n'.join(line[2:] if line.startswith('  ') else line for line in ref[13:33]))
p('<b>Extract Method:</b> createHeader, createFooter e createRow isolam a formatação; isVisibleTo nomeia a regra de acesso; applyAdminPriority mantém o efeito sobre o item. São funções internas, sem hierarquia ou novos métodos públicos.')
p('<b>Decompose Conditional e guard clause:</b> itens não visíveis são descartados no início do laço. <b>Consolidate Duplicate Conditional Fragments:</b> CSV e soma deixam de aparecer em cada ramo. <b>Replace Magic Number with Symbolic Constant:</b> 1000 e 500 recebem os nomes ADMIN_PRIORITY_THRESHOLD e USER_MAX_VISIBLE_VALUE, mantendo os operadores originais.')
p('Preservações relevantes: prioridade preexistente, mutação de item.priority, formatos desconhecidos e saída HTML ADMIN com &lt;tr &gt;. O espaço não foi corrigido porque sua remoção alteraria o texto retornado.', 'SmallReport')
story.append(PageBreak())

# 4. Resultados
h('3. Validação e rede de segurança')
p('ESLint 8.57.1 e SonarJS 0.21.0 foram executados com a mesma configuração efetiva para as duas versões. Os presets recomendados e as regras explícitas permaneceram ativos: complexidade com limite 15 e funções idênticas, ambos com severidade error. O JSON é compatível com ESLint 8; essa versão está fora de manutenção, opção registrada para compatibilidade com a base.')
rows=[['Verificação','Original','Refatorado'],['ESLint','2 erros; 0 avisos','0 erros; 0 avisos'],['Complexidade cognitiva','27 (limite 15)','Sem violação > 15*'],['Condicional unificável','1 ocorrência','Nenhuma'],['Testes com ESM temporário','4 passam; 1 falha','4 passam; 1 falha'],['npm test sem opção ESM','Falha de carregamento','Falha de carregamento']]
data=[[Paragraph(escape(c), styles['CellHeadReport' if i==0 else 'CellReport']) for c in row] for i,row in enumerate(rows)]
t=Table(data,colWidths=[195,146,146],hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#F0F4F8'),white]),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
story.append(t);story.append(Spacer(1,8))
p('* O lint não informou a complexidade exata da cópia por não haver violação. Ausência de alerta não significa complexidade zero.', 'SmallReport')
sub('O que foi comprovado')
p('O diff em relação ao HEAD está vazio para src/ReportGenerator.js e tests/ReportGenerator.test.js; os hashes coincidem com a base registrada. A suíte real está em tests/, embora o enunciado cite __tests__/. A cópia foi criada em __tests__/ReportGenerator.refactored.test.js e difere integralmente da original apenas no import.')
p('Após cada mudança significativa, os testes foram executados com ESM temporário. Resultado final real: <b>8 aprovados e 2 reprovados em 10 testes</b>. A mesma falha de HTML ADMIN ocorre em cada suíte: espera-se &lt;tr&gt;, mas recebe-se &lt;tr &gt;. A base já apresentava essa divergência. Nenhuma expectativa ou regra foi relaxada.')
p('Comparação suplementar entre versões: <b>200 cenários aprovados</b>, com duas chamadas por cenário e 400 comparações de saída e estado. Inclui limites 500/1000, prioridades preexistentes, formatos/papéis desconhecidos e itens vazios. Não constitui prova para toda entrada JavaScript possível.')
sub('Conclusão e limitação da entrega')
p('Os testes funcionam como rede de segurança quando existe uma linha de base conhecida e se verifica o comportamento após pequenas mudanças. Aqui, permitiram distinguir a falha preexistente de regressões novas, não identificadas nos casos executados. A decomposição reduz o custo de compreender e alterar as regras, e o lint confirmou a remoção dos dois alertas na cópia.')
p('<b>A exigência de 100% dos testes aprovados não foi atingida.</b> npm test também requer a opção temporária --experimental-vm-modules para carregar ESM. Essas pendências foram mantidas explícitas; a preservação do comportamento não permite alegar aprovação completa.')
p('<b>Rastreabilidade:</b> docs/analise-manual.md; docs/processo-refatoracao.md; docs/evidencias/analise-estatica-original.eslint.json; validacao-final-eslint.json; validacao-final-jest.json e validacao-final.md. Enunciado: PDF fornecido pelo aluno.', 'SmallReport')

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=48,bottomMargin=59,title='Detecção de Bad Smells e Refatoração Segura',author='Victor Gabriel Cruz Pereira',subject='Teste de Software - relatório com evidências reais')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(OUT)
assert len(reader.pages)==4, f'Página excedente: {len(reader.pages)}'
print(f'PDF criado: {OUT}; {len(reader.pages)} páginas')
