const fs = require('fs');
const path = require('path');

const mdPath = path.join(__dirname, '..', 'docs', 'PROJECT_BRIEF.md');
const outPath = path.join(__dirname, '..', 'docs', 'PROJECT_BRIEF.html');
const md = fs.readFileSync(mdPath, 'utf8');

// Convert markdown to HTML
function convert(text) {
  let h = text;
  
  // Escape HTML entities in code blocks first
  const codeBlocks = [];
  h = h.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<pre><code>${code.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</code></pre>`);
    return `%%CODEBLOCK_${idx}%%`;
  });

  // Inline code
  h = h.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold + italic
  h = h.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
  h = h.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  h = h.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Headers
  h = h.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  h = h.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  h = h.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // HR
  h = h.replace(/^---$/gm, '<hr/>');
  // Blockquotes
  h = h.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  h = h.replace(/<\/blockquote>\n<blockquote>/g, '<br/>');

  // Tables
  const lines = h.split('\n');
  let inTable = false;
  let tableHtml = '';
  let isHeader = true;
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      const cells = line.slice(1, -1).split('|').map(c => c.trim());
      if (cells.every(c => /^[-:]+$/.test(c))) {
        isHeader = false;
        continue;
      }
      if (!inTable) {
        inTable = true;
        isHeader = true;
        tableHtml = '<table>';
      }
      const tag = isHeader ? 'th' : 'td';
      tableHtml += '<tr>' + cells.map(c => `<${tag}>${c}</${tag}>`).join('') + '</tr>';
      if (isHeader) isHeader = false;
    } else {
      if (inTable) {
        tableHtml += '</table>';
        result.push(tableHtml);
        tableHtml = '';
        inTable = false;
      }
      // List items
      if (line.startsWith('- ')) {
        result.push('<li>' + line.slice(2) + '</li>');
      } else if (/^\d+\. /.test(line)) {
        result.push('<li>' + line.replace(/^\d+\. /, '') + '</li>');
      } else if (line === '' || line.startsWith('<')) {
        result.push(line);
      } else if (line.startsWith('%%CODEBLOCK_')) {
        result.push(line);
      } else {
        result.push('<p>' + line + '</p>');
      }
    }
  }
  if (inTable) result.push(tableHtml + '</table>');
  
  h = result.join('\n');

  // Wrap consecutive <li> in <ul>
  h = h.replace(/((?:<li>[\s\S]*?<\/li>\s*)+)/g, '<ul>$1</ul>');

  // Restore code blocks
  codeBlocks.forEach((block, i) => {
    h = h.replace(`%%CODEBLOCK_${i}%%`, block);
  });

  return h;
}

const html = convert(md);

const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Market Anomaly Detection — Project Brief for Jonathan Maharaj</title>
<style>
  @page { margin: 0.75in 0.9in; size: A4; }
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .no-print { display: none !important; }
    h2 { page-break-after: avoid; }
    table, pre, blockquote { page-break-inside: avoid; }
  }
  
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    line-height: 1.7;
    color: #1e293b;
    max-width: 820px;
    margin: 0 auto;
    padding: 30px 40px;
    background: #fff;
    font-size: 14px;
  }
  
  h1 { color: #0f172a; font-size: 2em; border-bottom: 3px solid #3b82f6; padding-bottom: 8px; margin-top: 35px; }
  h1:first-of-type { font-size: 2.3em; margin-top: 0; }
  h2 { color: #1e3a5f; font-size: 1.35em; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; margin-top: 30px; }
  h3 { color: #334155; font-size: 1.1em; margin-top: 20px; }
  p { margin: 6px 0; color: #334155; }
  strong { color: #0f172a; }
  em { color: #64748b; }
  
  code {
    background: #f1f5f9; color: #be185d; padding: 1px 5px;
    border-radius: 3px; font-size: 0.88em;
    font-family: 'SF Mono', 'Consolas', monospace;
  }
  
  pre {
    background: #0f172a; color: #e2e8f0;
    padding: 14px 18px; border-radius: 6px;
    font-size: 0.78em; line-height: 1.5;
    margin: 12px 0; overflow-x: auto;
  }
  pre code { background: none; color: inherit; padding: 0; font-size: 1em; }
  
  blockquote {
    border-left: 3px solid #3b82f6; margin: 12px 0;
    padding: 10px 18px; background: #eff6ff;
    color: #1e40af; border-radius: 0 6px 6px 0;
    font-style: italic; font-size: 0.95em;
  }
  
  table {
    width: 100%; border-collapse: collapse;
    margin: 12px 0; font-size: 0.88em;
  }
  th {
    background: #f1f5f9; color: #1e293b; font-weight: 700;
    text-transform: uppercase; font-size: 0.78em;
    letter-spacing: 0.04em; padding: 9px 12px;
    border: 1px solid #e2e8f0; text-align: left;
  }
  td { padding: 8px 12px; border: 1px solid #e2e8f0; color: #475569; }
  tbody tr:nth-child(even) { background: #f8fafc; }
  
  hr { border: none; border-top: 1.5px solid #e2e8f0; margin: 25px 0; }
  ul { padding-left: 22px; margin: 8px 0; }
  li { margin: 3px 0; color: #475569; }
  li strong { color: #1e293b; }
  
  .print-btn {
    position: fixed; top: 16px; right: 16px;
    background: #3b82f6; color: #fff; border: none;
    padding: 10px 24px; border-radius: 6px;
    font-size: 0.95em; font-weight: 600; cursor: pointer;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3);
  }
  .print-btn:hover { background: #2563eb; }
</style>
</head>
<body>
<button class="print-btn no-print" onclick="window.print()">Save as PDF</button>
${html}
</body>
</html>`;

fs.writeFileSync(outPath, fullHtml);
console.log('Created: PROJECT_BRIEF.html (~8 pages)');
