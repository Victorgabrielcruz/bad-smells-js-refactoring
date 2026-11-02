from pathlib import Path
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/relatorio-bad-smells-abnt.pdf'
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Consolas','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
W=A4[0]-5*cm
body=ParagraphStyle('Body',fontName='Arial',fontSize=12,leading=18,alignment=TA_JUSTIFY,firstLineIndent=1.25*cm,spaceAfter=0)
heading=ParagraphStyle('Heading',fontName='Arial-Bold',fontSize=12,leading=18,spaceBefore=0,spaceAfter=18,keepWithNext=True)
sub=ParagraphStyle('Sub',parent=heading,spaceBefore=12,spaceAfter=6)
caption=ParagraphStyle('Caption',fontName='Arial',fontSize=10,leading=12,alignment=TA_LEFT,spaceAfter=4)
source=ParagraphStyle('Source',parent=caption,spaceBefore=3,spaceAfter=9)
cover=ParagraphStyle('Cover',fontName='Arial',fontSize=12,leading=18,alignment=TA_CENTER)
coverbold=ParagraphStyle('CoverBold',parent=cover,fontName='Arial-Bold')
codeStyle=ParagraphStyle('Code',fontName='Consolas',fontSize=9,leading=11,spaceAfter=4)
refStyle=ParagraphStyle('Ref',fontName='Arial',fontSize=12,leading=12,alignment=TA_LEFT,spaceAfter=12,splitLongWords=True)
cell=ParagraphStyle('Cell',fontName='Arial',fontSize=10,leading=12)
cellbold=ParagraphStyle('CellBold',parent=cell,fontName='Arial-Bold')
story=[]
def p(t,style=body):story.append(Paragraph(t,style))
def h(t):p(t,heading)
def s(t):p(t,sub)
def code(t):story.append(Preformatted(t,codeStyle))
def number(canvas,doc):
    if doc.page>1:
        canvas.saveState();canvas.setFont('Arial',10)
        canvas.drawRightString(A4[0]-2*cm,A4[1]-2*cm,str(doc.page-1));canvas.restoreState()

# Capa: estrutura solicitada no enunciado, sem paginação.
p('PONTIFÍCIA UNIVERSIDADE CATÓLICA DE MINAS GERAIS',coverbold)
p('Engenharia de Software',cover)
story.append(Spacer(1,48))
p('VICTOR GABRIEL CRUZ PEREIRA',cover)
p('Matrícula: 861270',cover)
story.append(Spacer(1,118))
p('DETECÇÃO DE BAD SMELLS E REFATORAÇÃO SEGURA',coverbold)
p('Análise e validação de um gerador de relatórios JavaScript',cover)
story.append(Spacer(1,90))
p('Disciplina: Teste de Software',cover)
story.append(Spacer(1,140))
p('Belo Horizonte',cover)
p('2026',cover)
story.append(PageBreak())

# Conteúdo 1
h('1 ANÁLISE DO CÓDIGO ORIGINAL')
p('Foram analisados o método generateReport e suas regras em src/ReportGenerator.js. A inspeção manual foi complementada pelo ESLint com SonarJS. Os três principais smells e seus impactos são apresentados a seguir.')
s('1.1 Método longo e responsabilidades misturadas')
p('Nas linhas 11-68, o método reúne seleção, prioridade, formatação e soma. Alterar uma regra exige compreender todo o fluxo; testá-la isoladamente requer verificar o relatório completo. A técnica Extract Method separa essas responsabilidades.')
s('1.2 Condicionais complexas')
p('Nas linhas 27-54, papel do usuário, valor e formato aparecem em decisões aninhadas. Isso dificulta a manutenção e multiplica as combinações de teste. Decompose Conditional e cláusulas de guarda simplificam o fluxo.')
s('1.3 Duplicação de código')
p('As linhas 35-37 e 46-48 repetem a geração CSV. A soma aparece em quatro ramos. Uma mudança pode produzir divergências entre ADMIN e USER, exigindo verificações repetidas. Extrair a linha e centralizar a soma reduz esse risco.')
story.append(Spacer(1,12))
p('Figura 1 - Resultado do ESLint no código original',caption)
story.append(Image(str(ROOT/'docs/evidencias/eslint-antes-captura-editor-recorte.png'),width=W,height=W*260/1224))
p('Fonte: captura do autor (2026), da saída anterior preservada em analise-estatica-original.txt, aberta no editor. Não é captura histórica do terminal.',source)
p('O SonarJS mediu complexidade cognitiva 27, acima do limite 15 (11:3), e indicou uma condição unificável (43:14). Acrescentou métrica e precisão aos achados manuais; não reportou funções idênticas. Blocos repetidos não equivalem a funções inteiras iguais.')
story.append(PageBreak())

# Conteúdo 2
h('2 PROCESSO DE REFATORAÇÃO')
p('A prioridade foi decompor generateReport. O original foi preservado e a cópia foi criada em src/ReportGenerator.refactored.js, mantendo o export ReportGenerator, o construtor, a propriedade db e a assinatura pública.')
story.append(Spacer(1,12))
p('Figura 2 - Trecho original: decisões aninhadas (linhas 43-48)',caption)
original=(ROOT/'src/ReportGenerator.js').read_text(encoding='utf8').splitlines()
# Trecho literal; apenas remoção do recuo externo e quebra visual da linha longa.
before='\n'.join(line[6:] if line.startswith('      ') else line for line in original[42:48])
# O bloco usa fonte monoespaçada menor, como ilustração do código.
code(before)
p('Fonte: código original do projeto (2026). Trecho parcial do ramo USER.',source)
p('Figura 3 - Trecho refatorado: coordenação do processamento (linhas 18-28)',caption)
ref=(ROOT/'src/ReportGenerator.refactored.js').read_text(encoding='utf8').splitlines()
code('\n'.join(line[4:] if line.startswith('    ') else line for line in ref[17:28]))
p('Fonte: elaboração do autor (2026), em ReportGenerator.refactored.js.',source)
p('Aplicou-se Extract Method para cabeçalho, rodapé, linha, visibilidade e prioridade. O predicado isVisibleTo expressa a seleção, e a cláusula de guarda evita o aninhamento. A geração CSV e a totalização passaram a ter um único ponto de implementação.')
p('Os limites 1000 e 500 foram substituídos por constantes nomeadas, preservando os operadores &gt; e &lt;=. Os auxiliares são internos ao módulo: não foram criadas novas classes ou interfaces públicas.')
p('Foram mantidos a prioridade preexistente, a mutação de item.priority, os formatos desconhecidos e a saída HTML de ADMIN com &lt;tr &gt;. Remover esse espaço alteraria o texto retornado. A suíte foi copiada para __tests__/ReportGenerator.refactored.test.js, mudando apenas o import; a original permanece em tests/.')
story.append(PageBreak())

# Conteúdo 3
h('3 VALIDAÇÃO E CONCLUSÃO')
p('A mesma configuração efetiva foi usada: ESLint 8.57.1, SonarJS 0.21.0, presets recomendados e limite 15 com severidade error. Não houve supressões. O Quadro 1 resume as execuções reais.')
story.append(Spacer(1,12))
p('Quadro 1 - Comparação das versões',caption)
rows=[['Verificação','Original','Refatorado'],['Alertas do ESLint','2 erros; 0 avisos','0 erros; 0 avisos'],['Complexidade cognitiva','27; limite 15','Sem violação > 15*'],['Condição unificável','1 ocorrência','Nenhuma'],['Testes com ESM temporário','4 passam; 1 falha','4 passam; 1 falha']]
t=Table([[Paragraph(escape(c),cellbold if i==0 else cell) for c in row] for i,row in enumerate(rows)],colWidths=[W*.43,W*.285,W*.285],hAlign='LEFT')
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story.append(t)
p('Fonte: evidências do projeto (2026). * O valor exato da cópia não foi emitido; ausência de alerta não significa complexidade zero.',source)
p('O resultado global foi de 8 aprovações e 2 falhas em 10 testes. A mesma falha de HTML ADMIN já existia na base: espera-se &lt;tr&gt;, mas recebe-se &lt;tr &gt;. O comando npm test sem a opção temporária --experimental-vm-modules falha no carregamento ESM. Portanto, o requisito de 100% de aprovação não foi atingido.')
p('O diff e os hashes confirmaram os originais intactos; o teste copiado difere somente no import. Uma verificação suplementar aprovou 200 cenários, com 400 comparações de saída e estado. Não foram identificadas regressões nesses casos, o que não prova equivalência para todas as entradas possíveis.')
p('Os testes foram uma rede de segurança para comparar o comportamento após cada mudança significativa e distinguir falhas anteriores de regressões. A refatoração tornou as regras mais claras e eliminou os dois alertas na cópia, mantendo explícitas as limitações da validação.')
story.append(Spacer(1,12))
p('REFERÊNCIAS',ParagraphStyle('RefsTitle',parent=heading,alignment=TA_CENTER,spaceAfter=12))
p('PEREIRA, Victor Gabriel Cruz. <b>Bad-smells-js-refactoring: código e evidências de análise e validação</b>. 2026. Disponível em: https://github.com/Victorgabrielcruz/bad-smells-js-refactoring. Acesso em: 1 nov. 2026.',refStyle)
p('PUC MINAS. Sistema Integrado de Bibliotecas. <b>Orientações para elaboração de projetos de pesquisa, trabalhos acadêmicos, relatórios técnicos e/ou científicos e artigos científicos</b>. 6. ed. Belo Horizonte: PUC Minas, 2025. Disponível em: https://www.pucminas.br/biblioteca. Acesso em: 1 nov. 2026.',refStyle)

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=3*cm,rightMargin=2*cm,topMargin=3*cm,bottomMargin=2*cm,title='Detecção de Bad Smells e Refatoração Segura - ABNT',author='Victor Gabriel Cruz Pereira')
doc.build(story,onFirstPage=number,onLaterPages=number)
pdf=PdfReader(OUT)
assert len(pdf.pages)==4, f'Esperadas 4 páginas; obtidas {len(pdf.pages)}'
print(f'{OUT}: {len(pdf.pages)} páginas')
