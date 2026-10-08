const fs = require('fs');
const path = require('path');

const mdPath = path.join(__dirname, '..', 'docs', 'PROJECT_DOCUMENTATION.md');
const outPath = path.join(__dirname, '..', 'docs', 'PROJECT_DOCUMENTATION.html');

const md = fs.readFileSync(mdPath, 'utf8');

// Simple markdown to HTML
let html = md
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  // Code blocks (must be before other transforms)
  .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code class="lang-${lang}">${code}</code></pre>`;
  })
  // Inline code
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  // Bold
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // Italic (single *)
  .replace(/\*([^*]+)\*/g, '<em>$1</em>')
  // H3
  .replace(/^### (.+)$/gm, '<h3>$1</h3>')
  // H2
  .replace(/^## (.+)$/gm, '<h2>$1</h2>')
  // H1 
  .replace(/^# (.+)$/gm, '<h1>$1</h1>')
  // Horizontal rules
  .replace(/^---$/gm, '<hr/>')
  // Blockquotes (multi-line)
  .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
  // Fix consecutive blockquotes
  .replace(/<\/blockquote>\n<blockquote>/g, '<br/>')
  // Tables - detect header rows
  .replace(/^\|(.+)\|$/gm, (match, content) => {
    const cells = content.split('|').map(c => c.trim());
    // Skip separator rows
    if (cells.every(c => /^[-:]+$/.test(c))) return '<tr class="sep"></tr>';
    const cellHtml = cells.map(c => `<td>${c}</td>`).join('');
    return `<tr>${cellHtml}</tr>`;
  })
  // Wrap table rows in <table>
  .replace(/((?:<tr>[\s\S]*?<\/tr>\s*)+)/g, (match) => {
    // Make first row header
    let table = match.replace('<tr class="sep"></tr>', '');
    table = table.replace(/<tr>(.*?)<\/tr>/, (m, cells) => {
      return '<thead><tr>' + cells.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>') + '</tr></thead><tbody>';
    });
    return `<table>${table}</tbody></table>`;
  })
  // Unordered list items
  .replace(/^- (.+)$/gm, '<li>$1</li>')
  // Ordered list items
  .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  // Wrap consecutive <li> in <ul>
  .replace(/((?:<li>.*<\/li>\s*)+)/g, '<ul>$1</ul>')
  // Paragraphs - non-empty lines that aren't already HTML
  .replace(/^([^<\s].+)$/gm, (match) => {
    if (match.startsWith('<')) return match;
    return `<p>${match}</p>`;
  })
  // Clean up empty paragraphs
  .replace(/<p><\/p>/g, '')
  // Fix nested HTML issues
  .replace(/<p>(<h[123]>)/g, '$1')
  .replace(/(<\/h[123]>)<\/p>/g, '$1');

const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Market Anomaly & Fraud Detection System — Project Documentation</title>
<style>
  @page { 
    margin: 0.8in 1in; 
    size: A4;
  }
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    h2 { page-break-before: auto; page-break-after: avoid; }
    pre, table, blockquote { page-break-inside: avoid; }
    .no-print { display: none; }
  }
  
  * { box-sizing: border-box; }
  
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', sans-serif;
    line-height: 1.75;
    color: #1e293b;
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 50px;
    background: #ffffff;
  }
  
  /* Cover / Title */
  h1:first-of-type {
    font-size: 2.4em;
    color: #0f172a;
    border-bottom: 4px solid #3b82f6;
    padding-bottom: 12px;
    margin-bottom: 5px;
  }
  
  h1 {
    color: #0f172a;
    font-size: 1.9em;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 10px;
    margin-top: 45px;
  }
  
  h2 {
    color: #1e3a5f;
    font-size: 1.5em;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 35px;
  }
  
  h3 {
    color: #334155;
    font-size: 1.2em;
    margin-top: 25px;
    margin-bottom: 10px;
  }
  
  p {
    margin: 8px 0;
    color: #334155;
  }
  
  strong {
    color: #0f172a;
  }
  
  code {
    background: #f1f5f9;
    color: #be185d;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.88em;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  }
  
  pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 18px 22px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.82em;
    line-height: 1.55;
    margin: 16px 0;
    border: 1px solid #1e293b;
  }
  
  pre code {
    background: none;
    color: #e2e8f0;
    padding: 0;
    font-size: 1em;
  }
  
  blockquote {
    border-left: 4px solid #3b82f6;
    margin: 16px 0;
    padding: 14px 22px;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 0 8px 8px 0;
    font-style: italic;
  }
  
  blockquote strong {
    color: #1e3a5f;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 0.9em;
  }
  
  thead th {
    background: #f1f5f9;
    color: #1e293b;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.8em;
    letter-spacing: 0.05em;
    padding: 12px 14px;
    border: 1px solid #e2e8f0;
    text-align: left;
  }
  
  td {
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
    color: #475569;
  }
  
  tbody tr:nth-child(even) {
    background: #f8fafc;
  }
  
  hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 35px 0;
  }
  
  ul, ol {
    padding-left: 24px;
    margin: 10px 0;
  }
  
  li {
    margin: 5px 0;
    color: #475569;
  }
  
  li strong {
    color: #1e293b;
  }
  
  /* Print button */
  .print-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-size: 1em;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    z-index: 100;
    transition: all 0.2s;
  }
  .print-btn:hover {
    background: #2563eb;
    transform: translateY(-1px);
  }
</style>
</head>
<body>

<button class="print-btn no-print" onclick="window.print()">Save as PDF</button>

${html}

</body>
</html>`;

fs.writeFileSync(outPath, fullHtml);
console.log('Created: PROJECT_DOCUMENTATION.html');
console.log('Open in browser and click "Save as PDF" or use Cmd+P → Save as PDF');
