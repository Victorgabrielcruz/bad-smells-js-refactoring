const ADMIN_PRIORITY_THRESHOLD = 1000;
const USER_MAX_VISIBLE_VALUE = 500;

export class ReportGenerator {
  constructor(database) {
    this.db = database;
  }

  /**
   * Gera um relatório de itens baseado no tipo e no usuário.
   * - Admins veem tudo.
   * - Users comuns só veem itens com valor <= 500.
   */
  generateReport(reportType, user, items) {
    let report = createHeader(reportType, user);
    let total = 0;

    for (const item of items) {
      if (!isVisibleTo(user, item)) {
        continue;
      }

      applyAdminPriority(user, item);
      if (reportType === 'CSV' || reportType === 'HTML') {
        report += createRow(reportType, user, item);
        total += item.value;
      }
    }

    report += createFooter(reportType, total);

    return report.trim();
  }
}

function createHeader(reportType, user) {
  let report = '';
  if (reportType === 'CSV') {
    report += 'ID,NOME,VALOR,USUARIO\n';
  } else if (reportType === 'HTML') {
    report += '<html><body>\n';
    report += '<h1>Relatório</h1>\n';
    report += `<h2>Usuário: ${user.name}</h2>\n`;
    report += '<table>\n';
    report += '<tr><th>ID</th><th>Nome</th><th>Valor</th></tr>\n';
  }

  return report;
}

function createFooter(reportType, total) {
  let report = '';
  if (reportType === 'CSV') {
    report += '\nTotal,,\n';
    report += `${total},,\n`;
  } else if (reportType === 'HTML') {
    report += '</table>\n';
    report += `<h3>Total: ${total}</h3>\n`;
    report += '</body></html>\n';
  }

  return report;
}

function isVisibleTo(user, item) {
  return user.role === 'ADMIN' ||
    (user.role === 'USER' && item.value <= USER_MAX_VISIBLE_VALUE);
}

function applyAdminPriority(user, item) {
  if (user.role === 'ADMIN' && item.value > ADMIN_PRIORITY_THRESHOLD) {
    item.priority = true;
  }
}

function createRow(reportType, user, item) {
  if (reportType === 'CSV') {
    return `${item.id},${item.name},${item.value},${user.name}\n`;
  }

  let openingTag = '<tr>';
  if (user.role === 'ADMIN') {
    const style = item.priority ? 'style="font-weight:bold;"' : '';
    openingTag = `<tr ${style}>`;
  }
  return `${openingTag}<td>${item.id}</td><td>${item.name}</td><td>${item.value}</td></tr>\n`;
}
