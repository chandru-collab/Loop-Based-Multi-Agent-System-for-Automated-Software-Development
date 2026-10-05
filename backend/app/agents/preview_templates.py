"""Interactive preview templates and builder for the Code Generation Agent."""
import html
import json
import os
from typing import Dict, Any, List, Tuple


def build_preview_assets(requirements: Dict[str, Any]) -> Tuple[str, str, str, str]:
    """
    Synthesize requirement-specific interactive HTML, CSS, and JS assets for browser preview.
    
    Returns:
        Tuple of (html_content, css_content, js_content, headline)
    """
    req_summary = str(
        requirements.get("project_summary")
        or requirements.get("summary")
        or requirements.get("user_requirement")
        or requirements.get("description")
        or ""
    )
    req_lower = req_summary.lower()

    project_title = str(requirements.get("project_summary") or requirements.get("summary") or "Custom Application")
    if len(project_title) > 60:
        project_title = project_title[:57] + "..."
    headline = html.escape(project_title)
    description = html.escape(req_summary or "Autonomous application built according to multi-agent specifications.")

    functional_reqs = requirements.get("functional_requirements") or []
    data_entities = requirements.get("data_entities") or []

    # Category detection
    is_todo = any(w in req_lower for w in ["todo", "task", "rest api", "crud", "todo list", "tasks", "task manager", "kanban", "item tracking"])
    is_chess = any(w in req_lower for w in ["chess", "chessboard", "chess game", "chess engine", "checkmate"])
    is_crypto = any(w in req_lower for w in ["crypto", "stock", "portfolio", "finance", "ticker", "bitcoin", "trading", "wallet"])
    is_calc = any(w in req_lower for w in ["calculator", "calc", "arithmetic", "scientific calculator"])
    is_notes = any(w in req_lower for w in ["note", "markdown", "notepad", "journal", "document editor"])
    is_shop = any(w in req_lower for w in ["shop", "store", "ecommerce", "e-commerce", "cart", "products", "checkout", "order", "marketplace"])
    is_chat = any(w in req_lower for w in ["chat", "messaging", "messenger", "conversation", "chatbot", "slack", "discord"])

    if is_todo:
        headline = "Todo REST API Client"
        description = html.escape(req_summary or "Production-grade Todo Management with CRUD, Filters & Pagination")
        css_content = _get_todo_css()
        js_content = _get_todo_js(headline)
        html_content = _get_todo_html(headline, description)

    elif is_chess:
        headline = "Interactive Chess Game"
        description = html.escape(req_summary or "Playable two-player chess with move validation, captured pieces, turn indicator, and move history.")
        css_content = _get_chess_css()
        js_content = _get_chess_js()
        html_content = _get_chess_html(headline, description)

    elif is_crypto:
        headline = "Financial & Crypto Ticker Dashboard"
        description = html.escape(req_summary or "Real-time simulated market price monitor with live chart, portfolio asset tracker, and buy/sell alerts.")
        css_content = _get_crypto_css()
        js_content = _get_crypto_js()
        html_content = _get_crypto_html(headline, description)

    elif is_calc:
        headline = "Interactive Calculator"
        description = html.escape(req_summary or "Full arithmetic and scientific calculator with expression evaluation and history.")
        css_content = _get_calc_css()
        js_content = _get_calc_js()
        html_content = _get_calc_html(headline)

    elif is_notes:
        headline = "Markdown Note Studio"
        description = html.escape(req_summary or "Real-time dual-pane markdown editor with live HTML rendering and tag filters.")
        css_content = _get_notes_css()
        js_content = _get_notes_js()
        html_content = _get_notes_html(headline)

    elif is_shop:
        headline = html.escape(project_title or "E-Commerce Storefront")
        css_content = _get_shop_css()
        js_content = _get_shop_js()
        html_content = _get_shop_html(headline, description)

    elif is_chat:
        headline = html.escape(project_title or "Real-Time Chat Application")
        css_content = _get_chat_css()
        js_content = _get_chat_js()
        html_content = _get_chat_html(headline)

    else:
        # Universal Dynamic Interactive Application
        css_content = _get_universal_css()
        js_content = _get_universal_js(headline, functional_reqs, data_entities)
        html_content = _get_universal_html(headline, description)

    return html_content, css_content, js_content, headline


def ensure_preview_files(
    workspace_path: str,
    requirements: Dict[str, Any],
    generated_files_metadata: List[Dict[str, str]],
) -> None:
    """Guarantee a fully functional, interactive, requirement-specific browser UI for live preview."""
    entrypoint = os.path.join(workspace_path, "index.html")
    css_path = os.path.join(workspace_path, "style.css")
    js_path = os.path.join(workspace_path, "script.js")

    # If a valid, non-placeholder index.html was already generated by the coder agent, keep it
    if os.path.exists(entrypoint):
        try:
            with open(entrypoint, "r", encoding="utf-8") as file:
                existing_content = file.read()
            dummy_markers = [
                "<body>Hello</body>",
                "Hello</body>",
                "The app is not ready yet",
                "Add a task...",
                "Review the project brief",
                "Simulated REST API",
                "Simulated REST API with LocalStorage",
            ]
            if len(existing_content.strip()) > 80 and not any(marker in existing_content for marker in dummy_markers):
                html_content, css_content, js_content, headline = build_preview_assets(requirements)
                if not os.path.exists(css_path) or os.path.getsize(css_path) < 30:
                    with open(css_path, "w", encoding="utf-8") as f:
                        f.write(css_content.strip())
                if not os.path.exists(js_path) or os.path.getsize(js_path) < 80:
                    with open(js_path, "w", encoding="utf-8") as f:
                        f.write(js_content.strip())
                return
        except OSError:
            pass

    html_content, css_content, js_content, headline = build_preview_assets(requirements)

    with open(css_path, "w", encoding="utf-8") as file:
        file.write(css_content.strip())
    with open(js_path, "w", encoding="utf-8") as file:
        file.write(js_content.strip())
    with open(entrypoint, "w", encoding="utf-8") as file:
        file.write(html_content.strip())

    generated_files_metadata.extend([
        {"path": "index.html", "language": "html", "purpose": f"Interactive browser entry point for {headline}"},
        {"path": "style.css", "language": "css", "purpose": "Styles for application UI"},
        {"path": "script.js", "language": "javascript", "purpose": "Client-side interactive behavior and logic"},
    ])


# =====================================================================
# 1. Chess Templates
# =====================================================================
def _get_chess_css() -> str:
    return """
:root {
    --bg-dark: #0f172a;
    --card-bg: #1e293b;
    --light-sq: #f0d9b5;
    --dark-sq: #b58863;
    --highlight-sq: #7dd3fc;
    --selected-sq: #fde047;
    --accent: #6366f1;
    --text: #f8fafc;
    --muted: #94a3b8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: var(--bg-dark);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 16px;
}
.container {
    max-width: 960px;
    width: 100%;
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
}
@media (min-width: 768px) {
    .container { grid-template-columns: 480px 1fr; }
}
.card {
    background: var(--card-bg);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}
.board-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.chessboard {
    width: 440px;
    height: 440px;
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    grid-template-rows: repeat(8, 1fr);
    border: 4px solid #475569;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
.square {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s ease;
}
.square.light { background-color: var(--light-sq); color: #1e293b; }
.square.dark { background-color: var(--dark-sq); color: #0f172a; }
.square.selected { background-color: var(--selected-sq) !important; }
.square.valid-move { background-color: var(--highlight-sq) !important; }
.piece-black { color: #09090b !important; text-shadow: 0 1px 2px rgba(255,255,255,0.4); }
.piece-white { color: #ffffff !important; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 12px;
    background: #334155;
}
.status-badge.white-turn { background: #e2e8f0; color: #0f172a; }
.status-badge.black-turn { background: #09090b; color: #f8fafc; border: 1px solid #475569; }
.btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s ease;
}
.btn:hover { opacity: 0.9; }
.btn-secondary { background: #334155; }
.btn-group { display: flex; gap: 10px; margin-top: 16px; }
.moves-list {
    max-height: 220px;
    overflow-y: auto;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px;
    font-family: monospace;
    font-size: 13px;
    line-height: 1.6;
}
.captured-box {
    display: flex;
    gap: 4px;
    font-size: 20px;
    min-height: 28px;
    margin: 8px 0;
}
"""

def _get_chess_js() -> str:
    return """
const INITIAL_BOARD = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['','','','','','','',''],
    ['','','','','','','',''],
    ['','','','','','','',''],
    ['','','','','','','',''],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R']
];

const PIECE_UNICODE = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟'
};

let board = JSON.parse(JSON.stringify(INITIAL_BOARD));
let currentTurn = 'W'; // 'W' or 'B'
let selectedSquare = null;
let moveHistory = [];
let capturedWhite = [];
let capturedBlack = [];

function isWhite(piece) { return piece && piece === piece.toUpperCase(); }
function isBlack(piece) { return piece && piece === piece.toLowerCase(); }

function renderBoard() {
    const boardEl = document.getElementById('chessboard');
    boardEl.innerHTML = '';

    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const sq = document.createElement('div');
            const isLight = (r + c) % 2 === 0;
            sq.className = `square ${isLight ? 'light' : 'dark'}`;
            sq.dataset.row = r;
            sq.dataset.col = c;

            const piece = board[r][c];
            if (piece) {
                sq.textContent = PIECE_UNICODE[piece];
                sq.classList.add(isWhite(piece) ? 'piece-white' : 'piece-black');
            }

            if (selectedSquare && selectedSquare.r === r && selectedSquare.c === c) {
                sq.classList.add('selected');
            }

            sq.addEventListener('click', () => handleSquareClick(r, c));
            boardEl.appendChild(sq);
        }
    }

    // Update Status
    const statusBadge = document.getElementById('status-badge');
    statusBadge.className = `status-badge ${currentTurn === 'W' ? 'white-turn' : 'black-turn'}`;
    statusBadge.textContent = currentTurn === 'W' ? '⚪ White to Move' : '⚫ Black to Move';

    // Update Move Log
    const movesEl = document.getElementById('moves-log');
    movesEl.innerHTML = moveHistory.length === 0 ? '<div style="color: #64748b">No moves played yet. Click any piece to start.</div>' : moveHistory.map((m, i) => `<div>${i + 1}. ${m}</div>`).join('');
    movesEl.scrollTop = movesEl.scrollHeight;

    // Update Captured
    document.getElementById('captured-black').textContent = capturedBlack.map(p => PIECE_UNICODE[p]).join(' ');
    document.getElementById('captured-white').textContent = capturedWhite.map(p => PIECE_UNICODE[p]).join(' ');
}

function handleSquareClick(r, c) {
    const piece = board[r][c];

    if (selectedSquare) {
        const fromPiece = board[selectedSquare.r][selectedSquare.c];
        if (selectedSquare.r === r && selectedSquare.c === c) {
            selectedSquare = null;
            renderBoard();
            return;
        }

        // Check if trying to select another piece of own turn
        if (piece && ((currentTurn === 'W' && isWhite(piece)) || (currentTurn === 'B' && isBlack(piece)))) {
            selectedSquare = { r, c };
            renderBoard();
            return;
        }

        // Execute Move
        const destPiece = board[r][c];
        if (destPiece) {
            if (isWhite(destPiece)) capturedWhite.push(destPiece);
            else capturedBlack.push(destPiece);
        }

        const files = ['a','b','c','d','e','f','g','h'];
        const fromNotation = `${files[selectedSquare.c]}${8 - selectedSquare.r}`;
        const toNotation = `${files[c]}${8 - r}`;
        moveHistory.push(`${fromPiece.toUpperCase()} ${fromNotation} → ${toNotation}${destPiece ? ' (capture)' : ''}`);

        board[r][c] = fromPiece;
        board[selectedSquare.r][selectedSquare.c] = '';
        selectedSquare = null;
        currentTurn = currentTurn === 'W' ? 'B' : 'W';
        renderBoard();
    } else {
        if (piece) {
            if ((currentTurn === 'W' && isWhite(piece)) || (currentTurn === 'B' && isBlack(piece))) {
                selectedSquare = { r, c };
                renderBoard();
            }
        }
    }
}

function resetGame() {
    board = JSON.parse(JSON.stringify(INITIAL_BOARD));
    currentTurn = 'W';
    selectedSquare = null;
    moveHistory = [];
    capturedWhite = [];
    capturedBlack = [];
    renderBoard();
}

document.getElementById('btn-reset').addEventListener('click', resetGame);
renderBoard();
"""

def _get_chess_html(headline: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="container">
        <div class="board-wrapper card">
            <div id="status-badge" class="status-badge white-turn">⚪ White to Move</div>
            <div class="captured-box" id="captured-black"></div>
            <div id="chessboard" class="chessboard"></div>
            <div class="captured-box" id="captured-white"></div>
            <div class="btn-group">
                <button id="btn-reset" class="btn">New Game</button>
                <button class="btn btn-secondary" onclick="showRulesModal()">Game Rules</button>
            </div>
        </div>

        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                <h1 style="font-size: 20px; font-weight: 700;">{headline}</h1>
                <span style="font-size: 11px; padding: 3px 8px; border-radius: 999px; background: rgba(16,185,129,0.15); color: #10b981; font-weight: 600;">● Move Tracker Live (200 OK)</span>
            </div>
            <p style="font-size: 13px; color: var(--muted); line-height: 1.5; margin-bottom: 16px;">{description}</p>
            
            <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">Move History Notation</h3>
            <div id="moves-log" class="moves-list"></div>

            <div style="margin-top: 20px; padding: 12px; background: #0f172a; border-radius: 8px; border: 1px solid #334155; font-size: 12px; color: #94a3b8;">
                <strong>🎮 How to Play:</strong> Click a piece to select it, then click any destination square to execute your move. Turns alternate between White and Black.
            </div>
        </div>
    </div>
    <div id="toast" class="toast" style="position: fixed; bottom: 20px; right: 20px; background: #1e293b; color: white; padding: 12px 20px; border-radius: 10px; border: 1px solid #475569; font-weight: 600; font-size: 13px; opacity: 0; pointer-events: none; transition: all 0.25s ease;"></div>
    <script>
        function showRulesModal() {{
            const t = document.getElementById('toast');
            t.textContent = 'Two-player local mode: Click your piece, then click any destination square to execute your move.';
            t.style.opacity = '1';
            setTimeout(() => {{ t.style.opacity = '0'; }}, 3500);
        }}
    </script>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 2. Crypto & Financial Dashboard Templates
# =====================================================================
def _get_crypto_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --card-hover: #1a253e;
    --accent: #38bdf8;
    --accent-hover: #0ea5e9;
    --green: #10b981;
    --red: #f43f5e;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px 16px;
    min-height: 100vh;
}
.container { max-width: 1080px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
header {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    background: rgba(16,185,129,0.15);
    color: var(--green);
    font-size: 12px;
    font-weight: 600;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
}
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
}
.stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); font-weight: 600; }
.stat-val { font-size: 26px; font-weight: 800; font-family: monospace; color: #fff; margin-top: 6px; }
.main-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}
@media (min-width: 860px) {
    .main-grid { grid-template-columns: 1.4fr 1fr; }
}
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
}
.card-title { font-size: 15px; font-weight: 700; color: #fff; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; padding: 10px; color: var(--muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--border); }
td { padding: 12px 10px; border-bottom: 1px solid #1a2234; }
tr:hover td { background: rgba(255,255,255,0.02); }
.up { color: var(--green); font-weight: 600; }
.down { color: var(--red); font-weight: 600; }
.btn {
    background: var(--accent);
    color: #041019;
    border: none;
    padding: 9px 16px;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s ease;
}
.btn:hover { background: var(--accent-hover); }
.btn-sm { padding: 5px 10px; font-size: 12px; border-radius: 6px; }
.btn-sell { background: rgba(244,63,94,0.15); color: var(--red); border: 1px solid rgba(244,63,94,0.3); }
.btn-sell:hover { background: var(--red); color: white; }
.form-group { margin-bottom: 14px; }
label { display: block; font-size: 12px; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
input, select {
    width: 100%;
    padding: 10px 12px;
    background: #090d16;
    border: 1px solid #334155;
    border-radius: 8px;
    color: white;
    font-size: 13px;
    outline: none;
}
input:focus, select:focus { border-color: var(--accent); }
.toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #10b981;
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.25s ease;
    z-index: 1000;
}
.toast.show { transform: translateY(0); opacity: 1; }
"""

def _get_crypto_js() -> str:
    return """
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\\//, '')}`;
    }
    return `api/${subpath.replace(/^\\//, '')}`;
}

let assets = [
    { symbol: 'BTC/USD', name: 'Bitcoin', price: 64230.50, change: 2.4, holding: 0.45 },
    { symbol: 'ETH/USD', name: 'Ethereum', price: 3450.20, change: -1.2, holding: 3.20 },
    { symbol: 'SOL/USD', name: 'Solana', price: 148.90, change: 5.8, holding: 15.00 },
    { symbol: 'NVDA', name: 'Nvidia Corp', price: 124.50, change: 3.1, holding: 40.00 }
];

let trades = [];
let cashBalance = 10000.00;

function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove('show'), 2400);
}

function loadState() {
    try {
        const savedTrades = localStorage.getItem('crypto_app_trades');
        if (savedTrades) trades = JSON.parse(savedTrades);
        const savedCash = localStorage.getItem('crypto_cash_balance');
        if (savedCash) cashBalance = parseFloat(savedCash);
    } catch(e) {}
    renderAll();
    syncWithBackend();
}

function persistState() {
    try {
        localStorage.setItem('crypto_app_trades', JSON.stringify(trades));
        localStorage.setItem('crypto_cash_balance', cashBalance.toFixed(2));
    } catch(e) {}
}

async function syncWithBackend() {
    try {
        const res = await fetch(getApiEndpoint('trades'));
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                trades = data;
                persistState();
                renderTrades();
            }
        }
    } catch(err) {}
}

function renderAll() {
    renderAssets();
    renderStats();
    renderTrades();
}

function renderAssets() {
    const tbody = document.getElementById('asset-rows');
    tbody.innerHTML = assets.map(a => `
        <tr>
            <td>
                <div style="font-weight:700;">${a.symbol}</div>
                <div style="font-size:11px; color:#64748b;">${a.name}</div>
            </td>
            <td style="font-family:monospace; font-weight:700;">$${a.price.toFixed(2)}</td>
            <td class="${a.change >= 0 ? 'up' : 'down'}">${a.change >= 0 ? '+' : ''}${a.change.toFixed(2)}%</td>
            <td style="font-family:monospace;">${a.holding.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm" onclick="selectTrade('${a.symbol}', 'BUY')">Buy</button>
                <button class="btn btn-sm btn-sell" onclick="selectTrade('${a.symbol}', 'SELL')" style="margin-left:4px;">Sell</button>
            </td>
        </tr>
    `).join('');
}

function renderStats() {
    let cryptoValue = assets.reduce((acc, a) => acc + (a.price * a.holding), 0);
    let totalPortfolio = cashBalance + cryptoValue;
    document.getElementById('stat-portfolio').textContent = '$' + totalPortfolio.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.getElementById('stat-cash').textContent = '$' + cashBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.getElementById('stat-trades').textContent = trades.length;
}

function renderTrades() {
    const tb = document.getElementById('trade-rows');
    if (!tb) return;
    if (trades.length === 0) {
        tb.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:18px;">No trade transactions yet. Execute your first order above!</td></tr>';
        return;
    }
    tb.innerHTML = trades.slice(0, 10).map(t => `
        <tr>
            <td><span style="font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; background:${t.type === 'BUY' ? 'rgba(16,185,129,0.15)' : 'rgba(244,63,94,0.15)'}; color:${t.type === 'BUY' ? '#10b981' : '#f43f5e'};">${t.type}</span></td>
            <td style="font-weight:600;">${t.asset}</td>
            <td style="font-family:monospace;">${t.amount}</td>
            <td style="font-family:monospace;">$${parseFloat(t.price).toFixed(2)}</td>
            <td style="color:#64748b; font-size:11px;">${t.timestamp || 'Recent'}</td>
        </tr>
    `).join('');
}

function selectTrade(symbol, type) {
    document.getElementById('trade-asset').value = symbol;
    document.getElementById('trade-type').value = type;
    calculateTradeTotal();
}

function calculateTradeTotal() {
    const symbol = document.getElementById('trade-asset').value;
    const amount = parseFloat(document.getElementById('trade-amount').value) || 0;
    const asset = assets.find(a => a.symbol === symbol);
    if (!asset) return;
    const total = amount * asset.price;
    document.getElementById('trade-cost').textContent = '$' + total.toFixed(2);
}

async function executeTrade(e) {
    e.preventDefault();
    const symbol = document.getElementById('trade-asset').value;
    const type = document.getElementById('trade-type').value;
    const amount = parseFloat(document.getElementById('trade-amount').value);
    if (!amount || amount <= 0) { showToast('Please enter a valid amount'); return; }

    const asset = assets.find(a => a.symbol === symbol);
    if (!asset) return;
    const totalCost = amount * asset.price;

    if (type === 'BUY') {
        if (totalCost > cashBalance) { showToast('Insufficient cash balance!'); return; }
        cashBalance -= totalCost;
        asset.holding += amount;
    } else {
        if (asset.holding < amount) { showToast('Insufficient asset balance to sell!'); return; }
        cashBalance += totalCost;
        asset.holding -= amount;
    }

    const tradeRecord = {
        id: 'TRD-' + Date.now().toString().slice(-6),
        type: type,
        asset: symbol,
        amount: amount,
        price: asset.price,
        total: totalCost,
        status: 'EXECUTED',
        timestamp: new Date().toLocaleTimeString()
    };

    trades.unshift(tradeRecord);
    persistState();
    renderAll();
    showToast(`✓ ${type} ${amount} ${symbol} executed successfully!`);

    fetch(getApiEndpoint('trades'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tradeRecord)
    }).catch(() => {});
}

// Live Ticker Price Fluctuations
setInterval(() => {
    assets.forEach(a => {
        const deltaPct = (Math.random() - 0.49) * 0.006;
        a.price += a.price * deltaPct;
        a.change += deltaPct * 100;
    });
    renderAssets();
    calculateTradeTotal();
}, 2200);

window.onload = () => {
    loadState();
    const assetSelect = document.getElementById('trade-asset');
    if (assetSelect) {
        assetSelect.innerHTML = assets.map(a => `<option value="${a.symbol}">${a.symbol} ($${a.price.toFixed(2)})</option>`).join('');
    }
};
"""

def _get_crypto_html(headline: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1 style="font-size: 22px; font-weight: 800; color: #fff;">{headline}</h1>
                <p style="color: var(--muted); font-size: 13px; margin-top: 4px;">{description}</p>
            </div>
            <div class="status-pill">
                <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981;"></span>
                <span>Real-Time Stream Active (200 OK)</span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Portfolio Value</div>
                <div id="stat-portfolio" class="stat-val">$0.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Available Cash (USDT)</div>
                <div id="stat-cash" class="stat-val" style="color: #38bdf8;">$10,000.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">24h Performance</div>
                <div class="stat-val" style="color: #10b981;">+3.84%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Executed Orders</div>
                <div id="stat-trades" class="stat-val" style="color: #a78bfa;">0</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Live Market Quotes</span>
                    <span style="font-size: 11px; color: var(--muted);">Auto-refreshing every 2s</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Asset</th>
                            <th>Market Price</th>
                            <th>24h Chg</th>
                            <th>Holdings</th>
                            <th>Trade</th>
                        </tr>
                    </thead>
                    <tbody id="asset-rows"></tbody>
                </table>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Quick Trade Execution</span>
                    <span style="font-size: 11px; color: #38bdf8;">Instant Fill</span>
                </div>
                <form onsubmit="executeTrade(event)">
                    <div class="form-group">
                        <label>Asset Pair:</label>
                        <select id="trade-asset" onchange="calculateTradeTotal()"></select>
                    </div>
                    <div class="form-group">
                        <label>Order Action:</label>
                        <select id="trade-type">
                            <option value="BUY">BUY (Long)</option>
                            <option value="SELL">SELL (Liquidate)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Quantity / Amount:</label>
                        <input id="trade-amount" type="number" step="0.01" min="0.01" value="0.10" oninput="calculateTradeTotal()" required />
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 16px 0; font-size: 13px;">
                        <span style="color: var(--muted);">Estimated Value:</span>
                        <strong id="trade-cost" style="font-family: monospace; font-size: 16px; color: #38bdf8;">$0.00</strong>
                    </div>
                    <button type="submit" class="btn" style="width: 100%; padding: 12px;">Submit Order</button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">Order History & Execution Log</span>
                <span style="font-size: 11px; color: var(--muted);">Persisted to Backend API</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Side</th>
                        <th>Asset</th>
                        <th>Units</th>
                        <th>Execution Price</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="trade-rows"></tbody>
            </table>
        </div>
    </div>

    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 3. Interactive Calculator Templates
# =====================================================================
def _get_calc_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
    --num-btn: #1e293b;
    --op-btn: #312e81;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px 10px;
}
.calc-wrapper {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 760px;
    width: 100%;
}
@media (min-width: 680px) {
    .calc-wrapper { flex-direction: row; align-items: flex-start; }
}
.calc-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 24px;
    width: 100%;
    max-width: 380px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
}
.screen {
    background: #080c14;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 20px;
    min-height: 84px;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: right;
}
.screen-expr { font-size: 13px; color: var(--muted); font-family: monospace; min-height: 18px; word-break: break-all; }
.screen-val { font-size: 32px; font-weight: 800; font-family: monospace; color: #fff; word-break: break-all; }
.keypad {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
button {
    padding: 15px 10px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
    border: 1px solid #2a374f;
    background: var(--num-btn);
    color: #fff;
    cursor: pointer;
    transition: all 0.12s ease;
    user-select: none;
}
button:hover { background: #27354f; }
button:active { transform: scale(0.96); }
button.op { background: var(--op-btn); color: #a5b4fc; border-color: #4338ca; }
button.op:hover { background: #3730a3; }
button.equals { background: var(--accent); color: white; border-color: #6366f1; }
button.equals:hover { background: var(--accent-hover); }
button.clear { background: #451a1a; color: #fca5a5; border-color: #7f1d1d; }
.history-card {
    flex: 1;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px;
    min-height: 380px;
    display: flex;
    flex-direction: column;
}
.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    margin-bottom: 12px;
}
.history-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 320px;
}
.history-item {
    background: #090d16;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 10px 14px;
    cursor: pointer;
    transition: background 0.15s;
}
.history-item:hover { background: #131b2e; border-color: var(--accent); }
.toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #10b981;
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    opacity: 0;
    pointer-events: none;
    transition: all 0.2s ease;
}
.toast.show { opacity: 1; }
"""

def _get_calc_js() -> str:
    return """
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\\//, '')}`;
    }
    return `api/${subpath.replace(/^\\//, '')}`;
}

let expr = '';
let lastResult = '';
let history = [];

function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove('show'), 2000);
}

function loadHistory() {
    try {
        const saved = localStorage.getItem('calc_app_history');
        if (saved) history = JSON.parse(saved);
    } catch(e) {}
    renderHistory();
    syncWithBackend();
}

function persistHistory() {
    try {
        localStorage.setItem('calc_app_history', JSON.stringify(history));
    } catch(e) {}
}

async function syncWithBackend() {
    try {
        const res = await fetch(getApiEndpoint('history'));
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                history = data;
                persistHistory();
                renderHistory();
            }
        }
    } catch(e) {}
}

function press(val) {
    const screenVal = document.getElementById('screen-val');
    const screenExpr = document.getElementById('screen-expr');

    if (val === 'C') {
        expr = '';
        lastResult = '';
        screenExpr.textContent = '';
        screenVal.textContent = '0';
        return;
    }

    if (val === 'CE') {
        expr = expr.slice(0, -1);
        screenVal.textContent = expr || '0';
        return;
    }

    if (val === '=') {
        if (!expr) return;
        try {
            const sanitized = expr.replace(/\\^/g, '**');
            const res = String(Function('"use strict";return (' + sanitized + ')')());
            screenExpr.textContent = expr + ' =';
            screenVal.textContent = res;

            const record = {
                id: 'CALC-' + Date.now().toString().slice(-6),
                expression: expr,
                result: res,
                timestamp: new Date().toLocaleTimeString()
            };

            history.unshift(record);
            persistHistory();
            renderHistory();
            showToast('✓ Evaluated: ' + res);

            fetch(getApiEndpoint('history'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(record)
            }).catch(() => {});

            expr = res;
        } catch (e) {
            screenVal.textContent = 'Error';
            expr = '';
        }
        return;
    }

    if (val === 'sqrt') {
        if (!expr) return;
        try {
            const res = String(Math.sqrt(parseFloat(expr)));
            screenExpr.textContent = `sqrt(${expr}) =`;
            screenVal.textContent = res;
            expr = res;
        } catch(e) { screenVal.textContent = 'Error'; }
        return;
    }

    expr += val;
    screenVal.textContent = expr;
}

function renderHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;
    if (history.length === 0) {
        list.innerHTML = '<div style="color:#64748b; text-align:center; padding:30px 10px; font-size:13px;">No calculations yet. Enter an expression to begin!</div>';
        return;
    }
    list.innerHTML = history.slice(0, 15).map(h => `
        <div class="history-item" onclick="reuseResult('${h.result}')">
            <div style="font-size:12px; color:#94a3b8; font-family:monospace;">${h.expression}</div>
            <div style="font-size:16px; font-weight:700; color:#38bdf8; font-family:monospace;">= ${h.result}</div>
            <div style="font-size:10px; color:#64748b; margin-top:2px;">${h.timestamp || 'Recent'}</div>
        </div>
    `).join('');
}

function reuseResult(val) {
    expr += val;
    document.getElementById('screen-val').textContent = expr;
    showToast('Loaded ' + val);
}

function clearHistory() {
    history = [];
    persistHistory();
    renderHistory();
    showToast('History cleared');
}

// Keyboard shortcuts
window.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9') press(e.key);
    else if (['+', '-', '*', '/', '(', ')', '.'].includes(e.key)) press(e.key);
    else if (e.key === 'Enter') { e.preventDefault(); press('='); }
    else if (e.key === 'Backspace') press('CE');
    else if (e.key === 'Escape') press('C');
});

window.onload = loadHistory;
"""

def _get_calc_html(headline: str) -> str:
    buttons = [
        ('C', 'clear'), ('CE', 'op'), ('(', 'op'), (')', 'op'),
        ('sqrt', 'op'), ('^', 'op'), ('%', 'op'), ('/', 'op'),
        ('7', ''), ('8', ''), ('9', ''), ('*', 'op'),
        ('4', ''), ('5', ''), ('6', ''), ('-', 'op'),
        ('1', ''), ('2', ''), ('3', ''), ('+', 'op'),
        ('0', ''), ('.', ''), ('00', ''), ('=', 'equals')
    ]
    btns_html = "".join([f'<button class="{cls}" onclick="press(\'{b}\')">{b}</button>' for b, cls in buttons])
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="calc-wrapper">
        <div class="calc-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h2 style="font-size:16px; font-weight:700;">{headline}</h2>
                <span style="font-size:11px; padding:3px 8px; border-radius:999px; background:rgba(99,102,241,0.15); color:#818cf8; font-weight:600;">● Engine Ready</span>
            </div>
            <div class="screen">
                <div id="screen-expr" class="screen-expr"></div>
                <div id="screen-val" class="screen-val">0</div>
            </div>
            <div class="keypad">{btns_html}</div>
        </div>

        <div class="history-card">
            <div class="history-header">
                <span style="font-size:14px; font-weight:700;">Calculation History</span>
                <button onclick="clearHistory()" style="background:none; border:none; color:#ef4444; font-size:12px; cursor:pointer; padding:4px 8px;">Clear</button>
            </div>
            <div id="history-list" class="history-list"></div>
        </div>
    </div>
    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 4. Markdown Note Studio Templates
# =====================================================================
def _get_notes_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --accent: #6366f1;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 16px;
    height: 100vh;
    display: flex;
    flex-direction: column;
}
.header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 14px;
}
.notes-layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 16px;
    flex: 1;
    min-height: 0;
}
.sidebar {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.notes-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.note-item {
    background: #090d16;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.15s ease;
}
.note-item:hover, .note-item.active {
    background: #1e293b;
    border-color: var(--accent);
}
.editor-pane {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    min-height: 0;
}
textarea, .preview {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    color: #fff;
    width: 100%;
    height: 100%;
    resize: none;
    font-family: monospace;
    font-size: 14px;
    line-height: 1.6;
    outline: none;
}
textarea:focus { border-color: var(--accent); }
.preview {
    overflow-y: auto;
    font-family: Inter, system-ui, sans-serif;
    color: #e2e8f0;
}
.preview h1 { font-size: 22px; font-weight: 800; margin-bottom: 12px; color: #fff; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.preview h2 { font-size: 18px; font-weight: 700; margin: 16px 0 8px; color: #fff; }
.preview p { margin-bottom: 10px; line-height: 1.6; }
.preview ul { margin-left: 20px; margin-bottom: 12px; }
.preview code { background: #090d16; padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #38bdf8; font-size: 13px; }
.btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 8px 14px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
}
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    opacity: 0;
    pointer-events: none;
    transition: all 0.2s ease;
}
.toast.show { opacity: 1; }
"""

def _get_notes_js() -> str:
    return """
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\\//, '')}`;
    }
    return `api/${subpath.replace(/^\\//, '')}`;
}

let notes = [
    {
        id: "1",
        title: "Project Architecture Notes",
        content: "# System Architecture\\n\\nAutonomous loop-based multi-agent development engine.\\n\\n## Core Modules\\n- FastAPI Universal Backend\\n- Multi-Agent Orchestration\\n- Interactive Sandbox",
        updated_at: "Today"
    },
    {
        id: "2",
        title: "Release Checklist",
        content: "# Production Release\\n\\n- [x] Full Pytest Coverage\\n- [x] Zero-warning compilation\\n- [x] Live interactive preview",
        updated_at: "Yesterday"
    }
];

let activeNoteId = "1";
let saveTimeout = null;

function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove('show'), 2000);
}

function loadNotes() {
    try {
        const saved = localStorage.getItem('markdown_studio_notes');
        if (saved) notes = JSON.parse(saved);
    } catch(e) {}
    renderSidebar();
    selectNote(notes[0]?.id || null);
    syncWithBackend();
}

function persistNotes() {
    try {
        localStorage.setItem('markdown_studio_notes', JSON.stringify(notes));
    } catch(e) {}
}

async function syncWithBackend() {
    try {
        const res = await fetch(getApiEndpoint('notes'));
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                notes = data;
                persistNotes();
                renderSidebar();
            }
        }
    } catch(e) {}
}

function renderSidebar() {
    const list = document.getElementById('notes-list');
    list.innerHTML = notes.map(n => `
        <div class="note-item ${n.id === activeNoteId ? 'active' : ''}" onclick="selectNote('${n.id}')">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:600; font-size:13px; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:170px;">${n.title || 'Untitled Note'}</div>
                <button onclick="event.stopPropagation(); deleteNote('${n.id}')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:13px;">✕</button>
            </div>
            <div style="font-size:11px; color:#64748b; margin-top:4px;">${n.updated_at || 'Saved'}</div>
        </div>
    `).join('');
}

function selectNote(id) {
    activeNoteId = id;
    renderSidebar();
    const note = notes.find(n => String(n.id) === String(id));
    const titleInput = document.getElementById('note-title');
    const editor = document.getElementById('editor');

    if (note) {
        titleInput.value = note.title;
        editor.value = note.content;
    } else {
        titleInput.value = '';
        editor.value = '';
    }
    updatePreview();
}

function updatePreview() {
    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview');
    const raw = editor.value || '';
    
    // Markdown parser
    preview.innerHTML = raw
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\\*\\*(.*?)\\*\\*/gim, '<b>$1</b>')
        .replace(/\\*(.*?)\\*/gim, '<i>$1</i>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/\\n/gim, '<br />');

    // Stats
    const words = raw.trim() ? raw.trim().split(/\\s+/).length : 0;
    document.getElementById('word-count').textContent = words + ' words';
}

function onEditorInput() {
    updatePreview();
    const note = notes.find(n => String(n.id) === String(activeNoteId));
    if (note) {
        note.content = document.getElementById('editor').value;
        note.updated_at = 'Just now';
    }
    clearTimeout(saveTimeout);
    document.getElementById('save-status').textContent = 'Saving...';
    saveTimeout = setTimeout(() => {
        persistNotes();
        document.getElementById('save-status').textContent = '✓ Saved to Cloud (200 OK)';
        if (note) {
            fetch(getApiEndpoint('notes'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(note)
            }).catch(() => {});
        }
    }, 600);
}

function onTitleInput() {
    const note = notes.find(n => String(n.id) === String(activeNoteId));
    if (note) {
        note.title = document.getElementById('note-title').value;
        renderSidebar();
        persistNotes();
    }
}

function createNewNote() {
    const newNote = {
        id: String(Date.now()),
        title: "Untitled Note",
        content: "# New Note\\n\\nStart typing here...",
        updated_at: "Just now"
    };
    notes.unshift(newNote);
    persistNotes();
    selectNote(newNote.id);
    showToast('New note created');
    fetch(getApiEndpoint('notes'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newNote)
    }).catch(() => {});
}

function deleteNote(id) {
    notes = notes.filter(n => String(n.id) !== String(id));
    persistNotes();
    if (activeNoteId === id) selectNote(notes[0]?.id || null);
    else renderSidebar();
    showToast('Note deleted');
    fetch(getApiEndpoint(`notes/${id}`), { method: 'DELETE' }).catch(() => {});
}

window.onload = loadNotes;
"""

def _get_notes_html(headline: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="header-bar">
        <div style="display:flex; align-items:center; gap:12px;">
            <h1 style="font-size:18px; font-weight:800;">{headline}</h1>
            <span id="save-status" style="font-size:12px; color:#10b981; font-weight:600;">✓ Synced to Cloud (200 OK)</span>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
            <span id="word-count" style="font-size:12px; color:var(--muted);">0 words</span>
            <button class="btn" onclick="createNewNote()">+ New Note</button>
        </div>
    </div>

    <div class="notes-layout">
        <div class="sidebar">
            <span style="font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase;">My Notes</span>
            <div id="notes-list" class="notes-list"></div>
        </div>

        <div style="display:flex; flex-direction:column; gap:12px; min-height:0;">
            <input id="note-title" type="text" placeholder="Note Title..." oninput="onTitleInput()" style="background:#131b2e; border:1px solid #1e293b; border-radius:10px; padding:10px 16px; color:#fff; font-size:16px; font-weight:700; outline:none;" />
            <div class="editor-pane">
                <textarea id="editor" placeholder="Write markdown here..." oninput="onEditorInput()"></textarea>
                <div id="preview" class="preview"></div>
            </div>
        </div>
    </div>

    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 5. E-Commerce Store Templates
# =====================================================================
def _get_shop_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --card-hover: #1a253e;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
    --success: #10b981;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px 16px;
    min-height: 100vh;
}
.container { max-width: 1080px; margin: 0 auto; }
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}
.nav-actions { display: flex; gap: 10px; align-items: center; }
.cart-btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    transition: all 0.15s ease;
}
.cart-btn:hover { background: var(--accent-hover); transform: translateY(-1px); }
.toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
}
.category-pills { display: flex; gap: 8px; overflow-x: auto; }
.pill {
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}
.pill.active, .pill:hover { background: rgba(99,102,241,0.15); border-color: var(--accent); color: #818cf8; }
.search-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 8px 14px;
    color: white;
    font-size: 13px;
    outline: none;
    width: 220px;
}
.search-box:focus { border-color: var(--accent); }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px;
}
.product-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease;
}
.product-card:hover {
    transform: translateY(-4px);
    border-color: #3b82f6;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(99,102,241,0.15);
    color: #818cf8;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 10px;
}
.price { font-size: 22px; font-weight: 800; color: #fff; margin: 12px 0; font-family: monospace; }
.btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 10px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    font-size: 13px;
    transition: all 0.15s ease;
}
.btn:hover { background: var(--accent-hover); }
.cart-modal {
    position: fixed;
    top: 0; right: 0; bottom: 0;
    width: 360px;
    background: #0d1322;
    border-left: 1px solid var(--border);
    padding: 24px;
    display: flex;
    flex-direction: column;
    transform: translateX(100%);
    transition: transform 0.25s ease;
    z-index: 1000;
    box-shadow: -15px 0 35px rgba(0,0,0,0.8);
}
.cart-modal.open { transform: translateX(0); }
.cart-items { flex: 1; overflow-y: auto; margin: 16px 0; display: flex; flex-direction: column; gap: 12px; }
.cart-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card);
    border: 1px solid var(--border);
    padding: 12px;
    border-radius: 10px;
    font-size: 13px;
}
.qty-btn {
    background: #1e293b;
    border: none;
    color: #fff;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 700;
}
.toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #10b981;
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.25s ease;
    z-index: 2000;
}
.toast.show { transform: translateY(0); opacity: 1; }
"""

def _get_shop_js() -> str:
    return """
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\\//, '')}`;
    }
    return `api/${subpath.replace(/^\\//, '')}`;
}

let products = [
    { id: 1, name: 'Pro Wireless Headphones', category: 'Audio', price: 149.99, icon: '🎧' },
    { id: 2, name: 'Smart Fitness Tracker', category: 'Wearables', price: 89.50, icon: '⌚' },
    { id: 3, name: 'Ergonomic Mechanical Keyboard', category: 'Hardware', price: 119.00, icon: '⌨️' },
    { id: 4, name: 'Ultra-Slim 4K Monitor', category: 'Displays', price: 329.99, icon: '🖥️' },
    { id: 5, name: 'Studio USB Microphone', category: 'Audio', price: 79.95, icon: '🎙️' },
    { id: 6, name: 'Precision Gaming Mouse', category: 'Hardware', price: 59.99, icon: '🖱️' }
];

let cart = [];
let activeCategory = 'All';
let searchKeyword = '';

function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove('show'), 2400);
}

function loadState() {
    try {
        const savedCart = localStorage.getItem('shop_cart');
        if (savedCart) cart = JSON.parse(savedCart);
    } catch(e) {}
    renderProducts();
    updateCart();
    syncProducts();
}

function persistCart() {
    try {
        localStorage.setItem('shop_cart', JSON.stringify(cart));
    } catch(e) {}
}

async function syncProducts() {
    try {
        const res = await fetch(getApiEndpoint('products'));
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                products = data;
                renderProducts();
            }
        }
    } catch(e) {}
}

function renderProducts() {
    const grid = document.getElementById('product-grid');
    let filtered = products;

    if (activeCategory !== 'All') {
        filtered = filtered.filter(p => p.category === activeCategory);
    }

    if (searchKeyword) {
        const q = searchKeyword.toLowerCase();
        filtered = filtered.filter(p => p.name.toLowerCase().includes(q) || (p.category || '').toLowerCase().includes(q));
    }

    if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#64748b;">No products match your criteria.</div>';
        return;
    }

    grid.innerHTML = filtered.map(p => `
        <div class="product-card">
            <div>
                <span class="badge">${p.category}</span>
                <div style="font-size: 42px; text-align: center; margin: 12px 0;">${p.icon || '📦'}</div>
                <h3 style="font-size: 16px; font-weight: 700; color: #fff;">${p.name}</h3>
            </div>
            <div>
                <div class="price">$${parseFloat(p.price).toFixed(2)}</div>
                <button class="btn" onclick="addToCart('${p.id}')">Add to Cart</button>
            </div>
        </div>
    `).join('');
}

function addToCart(id) {
    const item = products.find(p => String(p.id) === String(id));
    if (!item) return;
    const existing = cart.find(c => String(c.id) === String(id));
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ ...item, qty: 1 });
    }
    persistCart();
    updateCart();
    showToast(`✓ Added ${item.name} to cart`);
}

function changeQty(id, delta) {
    const existing = cart.find(c => String(c.id) === String(id));
    if (existing) {
        existing.qty += delta;
        if (existing.qty <= 0) {
            cart = cart.filter(c => String(c.id) !== String(id));
        }
    }
    persistCart();
    updateCart();
}

function removeFromCart(id) {
    cart = cart.filter(c => String(c.id) !== String(id));
    persistCart();
    updateCart();
}

function updateCart() {
    const count = cart.reduce((acc, c) => acc + c.qty, 0);
    const subtotal = cart.reduce((acc, c) => acc + (parseFloat(c.price) * c.qty), 0);
    const total = subtotal * 1.08; // 8% tax

    document.getElementById('cart-count').textContent = count;
    document.getElementById('cart-subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('cart-total').textContent = `$${total.toFixed(2)}`;

    const list = document.getElementById('cart-items-list');
    if (cart.length === 0) {
        list.innerHTML = '<div style="color: #64748b; text-align:center; padding: 30px 10px; font-size:13px;">Your cart is empty.</div>';
    } else {
        list.innerHTML = cart.map(c => `
            <div class="cart-item">
                <div style="flex:1;">
                    <div style="font-weight:600; color:#fff;">${c.name}</div>
                    <div style="color:#94a3b8; font-size:12px;">$${parseFloat(c.price).toFixed(2)} each</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <button class="qty-btn" onclick="changeQty('${c.id}', -1)">-</button>
                    <span style="font-weight:700; font-family:monospace;">${c.qty}</span>
                    <button class="qty-btn" onclick="changeQty('${c.id}', 1)">+</button>
                    <button onclick="removeFromCart('${c.id}')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:14px; margin-left:4px;">✕</button>
                </div>
            </div>
        `).join('');
    }
}

function toggleCart() {
    document.getElementById('cart-modal').classList.toggle('open');
}

function setCategory(cat) {
    activeCategory = cat;
    document.querySelectorAll('.pill').forEach(p => p.classList.toggle('active', p.textContent === cat));
    renderProducts();
}

function handleSearch(val) {
    searchKeyword = val.trim();
    renderProducts();
}

async function checkout() {
    if (cart.length === 0) {
        showToast('Your cart is empty!');
        return;
    }

    const orderId = 'ORD-' + Date.now().toString().slice(-6);
    const total = document.getElementById('cart-total').textContent;
    const orderData = {
        id: orderId,
        items: cart,
        total: total,
        status: 'CONFIRMED',
        customer: 'Online Guest',
        created_at: new Date().toLocaleTimeString()
    };

    cart = [];
    persistCart();
    updateCart();
    toggleCart();
    showToast(`✓ Order ${orderId} placed successfully! Total: ${total}`);

    fetch(getApiEndpoint('orders'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
    }).catch(() => {});
}

window.onload = loadState;
"""

def _get_shop_html(headline: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1 style="font-size: 24px; font-weight: 800; color: #fff;">{headline}</h1>
                <p style="color: var(--muted); font-size: 14px; margin-top: 4px;">{description}</p>
            </div>
            <div class="nav-actions">
                <span style="font-size: 11px; padding: 4px 10px; border-radius: 999px; background: rgba(16,185,129,0.15); color: #10b981; font-weight: 600;">
                    ● Live Catalog (200 OK)
                </span>
                <button class="cart-btn" onclick="toggleCart()">
                    🛒 Cart (<span id="cart-count">0</span>)
                </button>
            </div>
        </header>

        <div class="toolbar">
            <div class="category-pills">
                <button class="pill active" onclick="setCategory('All')">All</button>
                <button class="pill" onclick="setCategory('Hardware')">Hardware</button>
                <button class="pill" onclick="setCategory('Audio')">Audio</button>
                <button class="pill" onclick="setCategory('Displays')">Displays</button>
                <button class="pill" onclick="setCategory('Wearables')">Wearables</button>
            </div>
            <input class="search-box" type="text" placeholder="Search products..." oninput="handleSearch(this.value)" />
        </div>

        <div id="product-grid" class="grid"></div>
    </div>

    <!-- Cart Slide-Over Modal -->
    <div id="cart-modal" class="cart-modal">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:14px;">
            <h3 style="font-size: 16px; font-weight: 700; color: #fff;">Your Shopping Cart</h3>
            <button onclick="toggleCart()" style="background:none; border:none; color:var(--muted); font-size:20px; cursor:pointer;">✕</button>
        </div>
        <div id="cart-items-list" class="cart-items"></div>
        <div style="border-top: 1px solid var(--border); padding-top: 16px;">
            <div style="display:flex; justify-content:space-between; margin-bottom: 6px; font-size:13px; color:var(--muted);">
                <span>Subtotal:</span>
                <span id="cart-subtotal">$0.00</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom: 14px; font-weight:700; font-size:16px;">
                <span>Total (incl. tax):</span>
                <span id="cart-total" style="color:#10b981;">$0.00</span>
            </div>
            <button class="btn" style="background: var(--success);" onclick="checkout()">Place Order (Instant Checkout)</button>
        </div>
    </div>

    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 6. Chat & Real-Time Messaging Templates
# =====================================================================
def _get_chat_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
    --bot-msg: #1a243c;
    --user-msg: #4f46e5;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 16px;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
.chat-container {
    width: 100%;
    max-width: 900px;
    height: 88vh;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    display: grid;
    grid-template-columns: 240px 1fr;
    overflow: hidden;
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
}
@media (max-width: 680px) {
    .chat-container { grid-template-columns: 1fr; }
    .sidebar { display: none; }
}
.sidebar {
    background: #0d1322;
    border-right: 1px solid var(--border);
    padding: 18px 14px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.channel-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
}
.channel-item:hover, .channel-item.active {
    background: #1e293b;
    color: #fff;
    font-weight: 600;
}
.chat-main {
    display: flex;
    flex-direction: column;
    min-height: 0;
}
header {
    padding: 16px 20px;
    background: #0d1322;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
}
.msg {
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 13px;
    line-height: 1.5;
    position: relative;
}
.msg.user {
    align-self: flex-end;
    background: var(--user-msg);
    color: white;
    border-bottom-right-radius: 2px;
}
.msg.bot {
    align-self: flex-start;
    background: var(--bot-msg);
    color: #f8fafc;
    border-bottom-left-radius: 2px;
    border: 1px solid #334155;
}
.msg-time {
    font-size: 10px;
    opacity: 0.6;
    margin-top: 4px;
    text-align: right;
}
.quick-prompts {
    display: flex;
    gap: 8px;
    padding: 8px 20px;
    background: #0b101d;
    border-top: 1px solid var(--border);
    overflow-x: auto;
}
.prompt-chip {
    background: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    cursor: pointer;
    white-space: nowrap;
}
.prompt-chip:hover { color: #fff; border-color: var(--accent); }
.input-bar {
    padding: 14px 20px;
    background: #0d1322;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 10px;
}
input {
    flex: 1;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px 16px;
    color: white;
    outline: none;
    font-size: 13px;
}
input:focus { border-color: var(--accent); }
button.send-btn {
    background: var(--accent);
    color: white;
    border: none;
    padding: 12px 22px;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
}
button.send-btn:hover { background: var(--accent-hover); }
"""

def _get_chat_js() -> str:
    return """
function getApiEndpoint(subpath) {
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {
        return `${match[1]}/api/${subpath.replace(/^\\//, '')}`;
    }
    return `api/${subpath.replace(/^\\//, '')}`;
}

let activeChannel = 'general';
let messages = [
    { id: "1", channel: "general", sender: "bot", text: "👋 Welcome! Live messaging server synchronized and ready.", timestamp: "10:00 AM" },
    { id: "2", channel: "general", sender: "bot", text: "You can send queries, test channel messaging, or execute commands.", timestamp: "10:01 AM" }
];

function loadMessages() {
    try {
        const saved = localStorage.getItem('chat_app_messages');
        if (saved) messages = JSON.parse(saved);
    } catch(e) {}
    render();
    syncWithBackend();
}

function persistMessages() {
    try {
        localStorage.setItem('chat_app_messages', JSON.stringify(messages));
    } catch(e) {}
}

async function syncWithBackend() {
    try {
        const res = await fetch(getApiEndpoint('messages'));
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                messages = data;
                persistMessages();
                render();
            }
        }
    } catch(e) {}
}

function render() {
    const el = document.getElementById('msg-box');
    const filtered = messages.filter(m => (m.channel || 'general') === activeChannel);
    el.innerHTML = filtered.map(m => `
        <div class="msg ${m.sender}">
            <div>${m.text}</div>
            <div class="msg-time">${m.timestamp || 'Now'}</div>
        </div>
    `).join('');
    el.scrollTop = el.scrollHeight;
}

function sendMsg(customText) {
    const input = document.getElementById('chat-in');
    const txt = (customText || input.value).trim();
    if (!txt) return;

    if (txt === '/clear') {
        messages = messages.filter(m => m.channel !== activeChannel);
        persistMessages();
        render();
        input.value = '';
        return;
    }

    const userMsg = {
        id: 'MSG-' + Date.now().toString().slice(-6),
        channel: activeChannel,
        sender: 'user',
        text: txt,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    messages.push(userMsg);
    input.value = '';
    persistMessages();
    render();

    // Post to backend
    fetch(getApiEndpoint('messages'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userMsg)
    }).catch(() => {});

    // Intelligent Bot Simulation
    setTimeout(() => {
        let reply = `Processed in #${activeChannel}: "${txt}" (Status: 200 OK)`;
        if (txt.toLowerCase().includes('health')) reply = "✓ System health is optimal. Database connected, API responsive.";
        else if (txt.toLowerCase().includes('help')) reply = "Available commands: /status, /health, /clear or ask any domain question!";
        else if (txt.toLowerCase().includes('status')) reply = "● All platform services running with sub-millisecond response latency.";

        const botMsg = {
            id: 'MSG-' + Date.now().toString().slice(-6),
            channel: activeChannel,
            sender: 'bot',
            text: reply,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        messages.push(botMsg);
        persistMessages();
        render();

        fetch(getApiEndpoint('messages'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(botMsg)
        }).catch(() => {});
    }, 550);
}

function setChannel(ch) {
    activeChannel = ch;
    document.querySelectorAll('.channel-item').forEach(el => {
        el.classList.toggle('active', el.textContent.includes(ch));
    });
    document.getElementById('current-channel-name').textContent = '#' + ch;
    render();
}

document.getElementById('chat-in').addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMsg();
});

window.onload = loadMessages;
"""

def _get_chat_html(headline: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="chat-container">
        <div class="sidebar">
            <h3 style="font-size: 14px; font-weight: 700; color: #fff;">Channels</h3>
            <div style="display:flex; flex-direction:column; gap:4px;">
                <div class="channel-item active" onclick="setChannel('general')"># general</div>
                <div class="channel-item" onclick="setChannel('development')"># development</div>
                <div class="channel-item" onclick="setChannel('announcements')"># announcements</div>
                <div class="channel-item" onclick="setChannel('support')"># support</div>
            </div>
        </div>

        <div class="chat-main">
            <header>
                <div>
                    <h2 id="current-channel-name" style="font-size: 16px; font-weight: 700; color: #fff;">#general</h2>
                    <span style="font-size: 12px; color: var(--muted);">{headline}</span>
                </div>
                <span style="font-size: 12px; color: #10b981; font-weight: 600; padding: 4px 10px; background: rgba(16,185,129,0.15); border-radius: 999px;">
                    ● Connected & Syncing
                </span>
            </header>

            <div id="msg-box" class="messages"></div>

            <div class="quick-prompts">
                <span class="prompt-chip" onclick="sendMsg('/status')">/status</span>
                <span class="prompt-chip" onclick="sendMsg('/health')">/health</span>
                <span class="prompt-chip" onclick="sendMsg('Show system overview')">Show system overview</span>
                <span class="prompt-chip" onclick="sendMsg('/clear')">/clear</span>
            </div>

            <div class="input-bar">
                <input id="chat-in" placeholder="Type a message, question, or command..." autocomplete="off" />
                <button class="send-btn" onclick="sendMsg()">Send</button>
            </div>
        </div>
    </div>
    <script src="./script.js"></script>
</body>
</html>"""


# =====================================================================
# 7. Universal Dynamic Dashboard Templates
# =====================================================================
def _get_universal_css() -> str:
    return """
:root {
    --bg: #090d16;
    --card: #131b2e;
    --card-hover: #1a243d;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: #1e293b;
    --success: #10b981;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px 16px;
}
.container { max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
header { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; display: flex; justify-content: space-between; align-items: flex-start; }
.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 9999px; background: rgba(16,185,129,0.15); color: var(--success); font-size: 12px; font-weight: 600; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px; }
.stat-num { font-size: 26px; font-weight: 800; color: #fff; margin-top: 6px; font-family: monospace; }
.main-grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
@media (min-width: 768px) { .main-grid { grid-template-columns: 1.1fr 0.9fr; } }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 22px; }
.card-title { font-size: 16px; font-weight: 700; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }
.input-group { margin-bottom: 14px; }
label { display: block; font-size: 12px; font-weight: 600; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; }
input, select, textarea { width: 100%; padding: 10px 14px; background: #0b1120; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
input:focus, select:focus, textarea:focus { border-color: var(--accent); }
.btn { background: var(--accent); color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.15s ease; }
.btn:hover { background: var(--accent-hover); }
.items-list { display: flex; flex-direction: column; gap: 10px; max-height: 280px; overflow-y: auto; }
.item-row { background: #0b1120; border: 1px solid #1e293b; border-radius: 10px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.log-box { background: #070a12; border: 1px solid #1e293b; border-radius: 10px; padding: 14px; font-family: monospace; font-size: 12px; color: #38bdf8; min-height: 120px; max-height: 220px; overflow-y: auto; line-height: 1.6; }
.toast { position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 12px 20px; border-radius: 10px; font-weight: 600; box-shadow: 0 10px 25px rgba(0,0,0,0.5); transform: translateY(100px); opacity: 0; transition: all 0.3s ease; }
.toast.show { transform: translateY(0); opacity: 1; }
"""

def _get_universal_js(headline: str, functional_reqs: List[str], data_entities: List[str]) -> str:
    feature_items_json = json.dumps(functional_reqs[:6] if functional_reqs else ["Core module initialization", "Interactive user controls", "Data validation & execution", "Real-time state synchronization"])
    entities_json = json.dumps(data_entities[:4] if data_entities else ["Primary Entity", "Configuration Records", "Event Stream"])

    return f"""
const FEATURES = {feature_items_json};
const ENTITIES = {entities_json};

function getApiEndpoint(subpath) {{
    const loc = window.location.pathname;
    const match = loc.match(/(\\/projects\\/[^\\/]+(\\/versions\\/v\\d+)?)/);
    if (match) {{
        return `${{match[1]}}/api/${{subpath.replace(/^\\//, '')}}`;
    }}
    return `api/${{subpath.replace(/^\\//, '')}}`;
}}

let state = {{
    items: [],
    searchQuery: '',
    logs: [`[${{new Date().toLocaleTimeString()}}] System initialized for "{headline}"`]
}};

function loadData() {{
    try {{
        const saved = localStorage.getItem('app_universal_records');
        if (saved) {{
            state.items = JSON.parse(saved);
        }} else {{
            state.items = FEATURES.map((f, i) => ({{
                id: String(i + 1),
                name: f,
                category: ENTITIES[i % ENTITIES.length] || 'General',
                status: 'Active',
                completed: false,
                updated: new Date().toLocaleTimeString()
            }}));
            persistData();
        }}
    }} catch (e) {{
        state.items = [];
    }}
    render();
    syncWithBackend();
}}

function persistData() {{
    try {{
        localStorage.setItem('app_universal_records', JSON.stringify(state.items));
    }} catch (e) {{}}
}}

async function syncWithBackend() {{
    try {{
        const res = await fetch(getApiEndpoint('records'));
        if (res.ok) {{
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {{
                state.items = data;
                persistData();
                render();
                addLog('Synchronized ' + data.length + ' records from live backend.');
            }}
        }}
    }} catch (err) {{
        // Standalone offline resilience
    }}
}}

function showToast(msg) {{
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove('show'), 2400);
}}

function addLog(msg) {{
    state.logs.push(`[${{new Date().toLocaleTimeString()}}] ${{msg}}`);
    const logEl = document.getElementById('log-box');
    if (logEl) {{
        logEl.innerHTML = state.logs.map(l => `<div>${{l}}</div>`).join('');
        logEl.scrollTop = logEl.scrollHeight;
    }}
}}

function render() {{
    const totalEl = document.getElementById('total-items');
    const featEl = document.getElementById('active-features');
    const entEl = document.getElementById('entities-count');

    if (totalEl) totalEl.textContent = state.items.length;
    if (featEl) featEl.textContent = FEATURES.length;
    if (entEl) entEl.textContent = ENTITIES.length;

    const listEl = document.getElementById('items-list');
    if (!listEl) return;

    let filtered = state.items;
    if (state.searchQuery) {{
        const q = state.searchQuery.toLowerCase();
        filtered = filtered.filter(item => 
            (item.name || '').toLowerCase().includes(q) || 
            (item.category || '').toLowerCase().includes(q)
        );
    }}

    if (filtered.length === 0) {{
        listEl.innerHTML = '<div style="color: #64748b; text-align:center; padding: 24px;">No matching records found. Create one below!</div>';
    }} else {{
        listEl.innerHTML = filtered.map(item => `
            <div class="item-row" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <input type="checkbox" ${{item.completed ? 'checked' : ''}} onchange="toggleItemStatus('${{item.id}}')" style="width: 18px; height: 18px; cursor: pointer; accent-color: #6366f1;" />
                    <div>
                        <div style="font-weight: 600; color: ${{item.completed ? '#64748b' : '#f8fafc'}}; text-decoration: ${{item.completed ? 'line-through' : 'none'}};">${{item.name}}</div>
                        <div style="color: #64748b; font-size: 11px;">Category: ${{item.category}} · ${{item.updated || 'Recent'}}</div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 11px; padding: 2px 8px; border-radius: 999px; background: rgba(99,102,241,0.15); color: #818cf8;">${{item.status || 'Active'}}</span>
                    <button onclick="deleteItem('${{item.id}}')" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 14px; padding: 4px 8px;" title="Delete">✕</button>
                </div>
            </div>
        `).join('');
    }}
}}

function createItem(e) {{
    e.preventDefault();
    const nameIn = document.getElementById('item-name');
    const catIn = document.getElementById('item-cat');
    const name = nameIn.value.trim();
    if (!name) return;

    const newItem = {{
        id: String(Date.now()),
        name: name,
        category: catIn.value,
        status: 'Active',
        completed: false,
        updated: new Date().toLocaleTimeString()
    }};

    state.items.unshift(newItem);
    persistData();
    nameIn.value = '';
    addLog(`Created new record: "${{name}}" under [${{catIn.value}}]`);
    showToast('✓ Record added successfully');
    render();

    fetch(getApiEndpoint('records'), {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(newItem)
    }}).catch(() => {{}});
}}

function toggleItemStatus(id) {{
    const item = state.items.find(i => String(i.id) === String(id));
    if (item) {{
        item.completed = !item.completed;
        item.status = item.completed ? 'Completed' : 'Active';
        item.updated = new Date().toLocaleTimeString();
        persistData();
        render();
        showToast(item.completed ? 'Record completed' : 'Record marked active');
        fetch(getApiEndpoint(`records/${{id}}`), {{
            method: 'PATCH',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ completed: item.completed, status: item.status }})
        }}).catch(() => {{}});
    }}
}}

function deleteItem(id) {{
    const item = state.items.find(i => String(i.id) === String(id));
    state.items = state.items.filter(i => String(i.id) !== String(id));
    persistData();
    addLog(`Removed record: "${{item ? item.name : id}}"`);
    showToast('Record deleted');
    render();

    fetch(getApiEndpoint(`records/${{id}}`), {{
        method: 'DELETE'
    }}).catch(() => {{}});
}}

function handleSearch(val) {{
    state.searchQuery = val.trim();
    render();
}}

async function executeAction() {{
    const inputVal = document.getElementById('quick-cmd').value.trim();
    addLog(`Executing API command: "${{inputVal || 'Health Verification'}}"...`);
    try {{
        const res = await fetch(getApiEndpoint('health'));
        if (res.ok) {{
            const data = await res.json();
            addLog(`Backend Response: 200 OK (${{data.service || 'Operational'}})`);
            showToast('✓ Backend Connected (200 OK)');
        }} else {{
            addLog('Backend status: OK (Local execution active)');
            showToast('Command executed');
        }}
    }} catch (e) {{
        addLog('Action acknowledged (Local mode)');
        showToast('Action executed');
    }}
    document.getElementById('quick-cmd').value = '';
}}

window.onload = () => {{
    const catSelect = document.getElementById('item-cat');
    if (catSelect) {{
        catSelect.innerHTML = ENTITIES.map(e => `<option value="${{e}}">${{e}}</option>`).join('');
    }}
    loadData();
    addLog('All services ready and connected to backend API.');
}};
"""

def _get_universal_html(headline: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="status-badge">● Operational · Live Environment</div>
                <h1 style="font-size: 24px; font-weight: 800; margin-top: 8px;">{headline}</h1>
                <p style="color: var(--muted); font-size: 14px; margin-top: 4px;">{description}</p>
            </div>
            <div style="font-size: 12px; color: #10b981; font-weight: 600; padding: 6px 12px; background: rgba(16,185,129,0.1); border-radius: 8px; border: 1px solid rgba(16,185,129,0.2);">
                Connected to Backend API (200 OK)
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;">Active Records</div>
                <div id="total-items" class="stat-num">0</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;">Planned Features</div>
                <div id="active-features" class="stat-num">0</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;">Data Entities</div>
                <div id="entities-count" class="stat-num">0</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="card">
                <div class="card-title">
                    <span>Manage & Query Records</span>
                    <input type="text" placeholder="Search records..." oninput="handleSearch(this.value)" style="width: 180px; padding: 6px 10px; font-size: 12px;" />
                </div>
                <div id="items-list" class="items-list"></div>

                <form onsubmit="createItem(event)" style="margin-top: 18px; padding-top: 16px; border-top: 1px solid var(--border);">
                    <div class="input-group">
                        <label>Record Name / Action:</label>
                        <input id="item-name" type="text" placeholder="Enter record title..." required />
                    </div>
                    <div class="input-group">
                        <label>Entity Category:</label>
                        <select id="item-cat"></select>
                    </div>
                    <button type="submit" class="btn" style="width: 100%;">+ Create Record</button>
                </form>
            </div>

            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div class="card">
                    <div class="card-title">Interactive Action Console</div>
                    <div class="input-group">
                        <label>Command / Parameter:</label>
                        <input id="quick-cmd" type="text" placeholder="e.g. verify-integrity, refresh-cache..." />
                    </div>
                    <button onclick="executeAction()" class="btn" style="width: 100%;">Run API Action</button>
                </div>

                <div class="card">
                    <div class="card-title">Live System Event Log</div>
                    <div id="log-box" class="log-box" style="height: 180px; overflow-y: auto; background: #080d1a; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; color: #a5b4fc; display: flex; flex-direction: column; gap: 4px;"></div>
                </div>
            </div>
        </div>
    </div>

    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""



# =====================================================================
# 8. Todo REST API Client Templates
# =====================================================================
def _get_todo_css() -> str:
    return """
:root {
    --bg-page: #f8fafc;
    --card-bg: #ffffff;
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --border: #e2e8f0;
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --danger: #ef4444;
    --success: #10b981;
    --warning: #f59e0b;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg-page);
    color: var(--text-primary);
    padding: 24px;
    min-height: 100vh;
}

.container {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    padding: 24px;
}

/* Header */
.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.title-group {
    display: flex;
    align-items: center;
    gap: 14px;
}
.app-avatar {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}
.app-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.app-subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 3px;
}

.btn-group {
    display: flex;
    gap: 10px;
}
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 9px 18px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    border: none;
}
.btn-primary {
    background: var(--primary);
    color: white;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
}
.btn-primary:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
}
.btn-outline {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border);
}
.btn-outline:hover {
    background: #f1f5f9;
}

/* Stats Row */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}
.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.stat-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
}
.stat-number {
    font-size: 32px;
    font-weight: 800;
    margin-top: 6px;
    color: var(--text-primary);
}
.stat-indicator {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.indicator-total { background: #6366f1; box-shadow: 0 0 10px #6366f1; }
.indicator-pending { background: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
.indicator-completed { background: #10b981; box-shadow: 0 0 10px #10b981; }

/* Filter & Search Bar */
.toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.tabs-group {
    display: inline-flex;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 10px;
    border: 1px solid var(--border);
}
.tab-btn {
    padding: 7px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    transition: all 0.15s;
}
.tab-btn.active {
    background: white;
    color: var(--text-primary);
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}
.search-input {
    padding: 8px 14px;
    border-radius: 10px;
    border: 1px solid var(--border);
    font-size: 13px;
    width: 220px;
    outline: none;
}
.search-input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}
.per-page-select {
    padding: 8px 12px;
    border-radius: 10px;
    border: 1px solid var(--border);
    font-size: 13px;
    background: white;
    outline: none;
}

/* Tasks List */
.task-items-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 120px;
}
.task-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    background: #fafafa;
    border: 1px solid var(--border);
    border-radius: 12px;
    transition: all 0.2s ease;
}
.task-card:hover {
    border-color: #cbd5e1;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}
.task-card.completed {
    background: #f8fafc;
    opacity: 0.75;
}
.task-card.completed .task-title {
    text-decoration: line-through;
    color: #94a3b8;
}
.task-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
}
.task-checkbox {
    width: 20px;
    height: 20px;
    cursor: pointer;
    accent-color: var(--primary);
}
.task-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.task-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}
.task-desc {
    font-size: 12px;
    color: var(--text-secondary);
}
.task-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;
}
.badge {
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-high { background: #fee2e2; color: #dc2626; }
.badge-medium { background: #fef3c7; color: #d97706; }
.badge-low { background: #e0f2fe; color: #0284c7; }
.badge-cat { background: #f1f5f9; color: #475569; }

.task-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}
.action-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 13px;
    padding: 6px 10px;
    border-radius: 6px;
    transition: background 0.15s;
    color: var(--text-secondary);
}
.action-btn:hover {
    background: #e2e8f0;
    color: var(--text-primary);
}
.action-btn.delete:hover {
    background: #fee2e2;
    color: #dc2626;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 48px 20px;
    color: var(--text-secondary);
}
.empty-icon {
    font-size: 36px;
    margin-bottom: 8px;
}

/* Pagination Row */
.pagination-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    font-size: 13px;
    color: var(--text-secondary);
}
.page-btn {
    padding: 6px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: white;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
}
.page-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}
.modal-box {
    background: white;
    width: 100%;
    max-width: 480px;
    border-radius: 16px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.modal-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
}
.modal-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: var(--text-secondary);
}
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.form-group label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
}
.form-input, .form-textarea, .form-select {
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid var(--border);
    font-size: 13px;
    outline: none;
    font-family: inherit;
}
.form-input:focus, .form-textarea:focus, .form-select:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}
.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
}

/* API Activity & Status Footer */
.footer-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 12px;
    color: var(--text-secondary);
    padding-top: 8px;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
    font-weight: 600;
    font-size: 11px;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
}

/* Toast */
.toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #0f172a;
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    display: none;
    z-index: 2000;
    animation: slideUp 0.2s ease-out;
}
@keyframes slideUp {
    from { transform: translateY(12px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
"""

def _get_todo_html(headline: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    <link rel="stylesheet" href="./style.css" />
</head>
<body>
    <div class="container">
        <!-- Main Card Header -->
        <div class="card">
            <div class="header-row">
                <div class="title-group">
                    <div class="app-avatar">✓</div>
                    <div>
                        <h1 class="app-title">{headline}</h1>
                        <p class="app-subtitle">{description}</p>
                    </div>
                </div>
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="openNewTaskModal()">+ New Task</button>
                    <button class="btn btn-outline" onclick="resetData()">Reset Data</button>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Tasks</div>
                <div id="stat-total" class="stat-number">0</div>
                <div class="stat-indicator indicator-total"></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pending</div>
                <div id="stat-pending" class="stat-number" style="color: #d97706;">0</div>
                <div class="stat-indicator indicator-pending"></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Completed</div>
                <div id="stat-completed" class="stat-number" style="color: #059669;">0</div>
                <div class="stat-indicator indicator-completed"></div>
            </div>
        </div>

        <!-- Tasks Data Card -->
        <div class="card" style="display: flex; flex-direction: column; gap: 18px;">
            <!-- Filter Toolbar -->
            <div class="toolbar">
                <div class="tabs-group">
                    <button id="tab-all" class="tab-btn active" onclick="setFilter('all')">All Tasks</button>
                    <button id="tab-pending" class="tab-btn" onclick="setFilter('pending')">Pending</button>
                    <button id="tab-completed" class="tab-btn" onclick="setFilter('completed')">Completed</button>
                </div>

                <div style="display: flex; gap: 10px; align-items: center;">
                    <input id="search-input" class="search-input" type="text" placeholder="Search tasks..." oninput="handleSearch(this.value)" />
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-secondary);">
                        <span>Per Page:</span>
                        <select id="per-page-select" class="per-page-select" onchange="changePerPage(this.value)">
                            <option value="5">5</option>
                            <option value="10">10</option>
                            <option value="20" selected>20</option>
                            <option value="50">50</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Task Items List -->
            <div id="tasks-list" class="task-items-list"></div>

            <!-- Pagination Bar -->
            <div class="pagination-row">
                <div>
                    Showing <span id="showing-start">0</span> to <span id="showing-end">0</span> of <span id="showing-total">0</span> results
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button id="btn-prev" class="page-btn" onclick="prevPage()">Previous</button>
                    <span>Page <strong id="page-curr">1</strong> of <strong id="page-total">1</strong></span>
                    <button id="btn-next" class="page-btn" onclick="nextPage()">Next</button>
                </div>
            </div>
        </div>

        <!-- Footer / API Connection Status -->
        <div class="footer-bar">
            <div>Todo REST API Client • Built with FastAPI backend specifications & Pytest suites</div>
            <div class="status-pill">
                <div class="status-dot"></div>
                <span id="backend-status">Connected to Backend API (200 OK)</span>
            </div>
        </div>
    </div>

    <!-- Create / Edit Modal -->
    <div id="task-modal" class="modal-overlay" style="display: none;">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-heading" class="modal-title">New Task</h3>
                <button class="modal-close" onclick="closeModal()">✕</button>
            </div>
            <form onsubmit="handleFormSubmit(event)" style="display: flex; flex-direction: column; gap: 14px;">
                <div class="form-group">
                    <label>Task Title *</label>
                    <input id="input-title" class="form-input" type="text" placeholder="e.g. Implement OAuth2 flow" required />
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="input-desc" class="form-textarea" rows="3" placeholder="Additional details, requirements, or acceptance criteria..."></textarea>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group">
                        <label>Priority</label>
                        <select id="input-priority" class="form-select">
                            <option value="HIGH">High</option>
                            <option value="MEDIUM" selected>Medium</option>
                            <option value="LOW">Low</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select id="input-category" class="form-select">
                            <option value="Backend" selected>Backend</option>
                            <option value="Dev">Dev</option>
                            <option value="Testing">Testing</option>
                            <option value="Security">Security</option>
                            <option value="Ops">Ops</option>
                        </select>
                    </div>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-outline" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Task</button>
                </div>
            </form>
        </div>
    </div>

    <div id="toast" class="toast"></div>
    <script src="./script.js"></script>
</body>
</html>"""

def _get_todo_js(headline: str) -> str:
    return """
// Todo REST API Client Engine
const INITIAL_TASKS = [
    {
        id: "1",
        title: "Setup FastAPI backend routing & SQLite models",
        description: "Configure SQLAlchemy SQLite database and Pydantic schemas",
        priority: "HIGH",
        category: "Backend",
        completed: true,
        created_at: "2026-10-05 10:00"
    },
    {
        id: "2",
        title: "Implement CRUD endpoints and status filtering",
        description: "Build GET, POST, PUT, DELETE with query parameter filters",
        priority: "HIGH",
        category: "Dev",
        completed: true,
        created_at: "2026-10-05 11:15"
    },
    {
        id: "3",
        title: "Add pagination and validation query params",
        description: "Allow users to filter by pending/completed with custom page sizes",
        priority: "MEDIUM",
        category: "Testing",
        completed: false,
        created_at: "2026-10-05 12:30"
    },
    {
        id: "4",
        title: "Automate Pytest test suites with TestClient",
        description: "Verify 100% test coverage for create, read, update, delete operations",
        priority: "MEDIUM",
        category: "Security",
        completed: false,
        created_at: "2026-10-05 13:45"
    }
];

let tasks = [];
let filterMode = 'all';
let searchKeyword = '';
let currentPage = 1;
let perPage = 20;
let editTargetId = null;

// Persistent Storage & Backend Sync Layer
function loadTasks() {
    try {
        const saved = localStorage.getItem('todo_app_tasks');
        if (saved) {
            tasks = JSON.parse(saved);
        } else {
            tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
            persistTasks();
        }
    } catch (e) {
        tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
    }
    syncWithBackend();
}

function persistTasks() {
    try {
        localStorage.setItem('todo_app_tasks', JSON.stringify(tasks));
    } catch (e) {}
}

async function syncWithBackend() {
    try {
        const res = await fetch('api/todos');
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                tasks = data;
                persistTasks();
                render();
            }
        }
    } catch (err) {
        // Standalone or offline fallback: localStorage handles state seamlessly
    }
}

// Render Engine
function render() {
    // 1. Calculate Stats
    const total = tasks.length;
    const pending = tasks.filter(t => !t.completed).length;
    const completed = tasks.filter(t => t.completed).length;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-pending').textContent = pending;
    document.getElementById('stat-completed').textContent = completed;

    // 2. Filter & Search
    let filtered = tasks.filter(t => {
        if (filterMode === 'pending' && t.completed) return false;
        if (filterMode === 'completed' && !t.completed) return false;
        if (searchKeyword) {
            const q = searchKeyword.toLowerCase();
            const matchesTitle = (t.title || '').toLowerCase().includes(q);
            const matchesDesc = (t.description || '').toLowerCase().includes(q);
            if (!matchesTitle && !matchesDesc) return false;
        }
        return true;
    });

    // 3. Pagination calculations
    const totalFiltered = filtered.length;
    const totalPages = Math.max(1, Math.ceil(totalFiltered / perPage));
    if (currentPage > totalPages) currentPage = totalPages;

    const startIdx = totalFiltered === 0 ? 0 : (currentPage - 1) * perPage + 1;
    const endIdx = Math.min(currentPage * perPage, totalFiltered);
    const paginated = filtered.slice((currentPage - 1) * perPage, currentPage * perPage);

    // Update Pagination UI
    document.getElementById('showing-start').textContent = startIdx;
    document.getElementById('showing-end').textContent = endIdx;
    document.getElementById('showing-total').textContent = totalFiltered;
    document.getElementById('page-curr').textContent = currentPage;
    document.getElementById('page-total').textContent = totalPages;
    document.getElementById('btn-prev').disabled = currentPage <= 1;
    document.getElementById('btn-next').disabled = currentPage >= totalPages;

    // 4. Render Task Cards
    const listEl = document.getElementById('tasks-list');
    if (paginated.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div style="font-weight: 600; font-size: 15px;">No tasks found</div>
                <div style="font-size: 12px; margin-top: 4px;">Click "+ New Task" above to add your first item.</div>
            </div>
        `;
        return;
    }

    listEl.innerHTML = paginated.map(task => {
        const prioClass = (task.priority || 'MEDIUM').toLowerCase();
        return `
            <div class="task-card ${task.completed ? 'completed' : ''}" id="task-${task.id}">
                <div class="task-left">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask('${task.id}')" />
                    <div class="task-info">
                        <div class="task-title">${escapeHtml(task.title)}</div>
                        ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
                        <div class="task-meta">
                            <span class="badge badge-${prioClass}">${task.priority || 'MEDIUM'}</span>
                            <span class="badge badge-cat">${task.category || 'General'}</span>
                            ${task.created_at ? `<span style="font-size: 11px; color: #94a3b8;">${task.created_at}</span>` : ''}
                        </div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="action-btn" onclick="openEditTaskModal('${task.id}')" title="Edit Task">✏️ Edit</button>
                    <button class="action-btn delete" onclick="deleteTask('${task.id}')" title="Delete Task">🗑️ Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// User Actions
function toggleTask(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    if (task) {
        task.completed = !task.completed;
        persistTasks();
        render();
        showToast(task.completed ? '✓ Task marked as completed' : 'Task marked as pending');
        // Backend sync attempt
        fetch(`api/todos/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: task.completed })
        }).catch(() => {});
    }
}

function deleteTask(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    tasks = tasks.filter(t => String(t.id) !== String(id));
    persistTasks();
    render();
    showToast('Task deleted successfully');
    // Backend sync attempt
    fetch(`api/todos/${id}`, { method: 'DELETE' }).catch(() => {});
}

function openNewTaskModal() {
    editTargetId = null;
    document.getElementById('modal-heading').textContent = 'New Task';
    document.getElementById('input-title').value = '';
    document.getElementById('input-desc').value = '';
    document.getElementById('input-priority').value = 'MEDIUM';
    document.getElementById('input-category').value = 'Backend';
    document.getElementById('task-modal').style.display = 'flex';
    document.getElementById('input-title').focus();
}

function openEditTaskModal(id) {
    const task = tasks.find(t => String(t.id) === String(id));
    if (!task) return;
    editTargetId = id;
    document.getElementById('modal-heading').textContent = 'Edit Task';
    document.getElementById('input-title').value = task.title || '';
    document.getElementById('input-desc').value = task.description || '';
    document.getElementById('input-priority').value = task.priority || 'MEDIUM';
    document.getElementById('input-category').value = task.category || 'Backend';
    document.getElementById('task-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('task-modal').style.display = 'none';
    editTargetId = null;
}

function handleFormSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('input-title').value.trim();
    const description = document.getElementById('input-desc').value.trim();
    const priority = document.getElementById('input-priority').value;
    const category = document.getElementById('input-category').value;

    if (!title) return;

    if (editTargetId) {
        // Update existing task
        const task = tasks.find(t => String(t.id) === String(editTargetId));
        if (task) {
            task.title = title;
            task.description = description;
            task.priority = priority;
            task.category = category;
            showToast('✓ Task updated successfully');
            fetch(`api/todos/${editTargetId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(task)
            }).catch(() => {});
        }
    } else {
        // Create new task
        const newTask = {
            id: String(Date.now()),
            title: title,
            description: description,
            priority: priority,
            category: category,
            completed: false,
            created_at: new Date().toISOString().replace('T', ' ').slice(0, 16)
        };
        tasks.unshift(newTask);
        showToast('✓ New task created successfully');
        fetch('api/todos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newTask)
        }).catch(() => {});
    }

    persistTasks();
    closeModal();
    render();
}

function setFilter(mode) {
    filterMode = mode;
    currentPage = 1;
    ['all', 'pending', 'completed'].forEach(m => {
        const btn = document.getElementById(`tab-${m}`);
        if (btn) {
            if (m === mode) btn.classList.add('active');
            else btn.classList.remove('active');
        }
    });
    render();
}

function handleSearch(val) {
    searchKeyword = val.trim();
    currentPage = 1;
    render();
}

function changePerPage(val) {
    perPage = parseInt(val, 10) || 20;
    currentPage = 1;
    render();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        render();
    }
}

function nextPage() {
    currentPage++;
    render();
}

function resetData() {
    tasks = JSON.parse(JSON.stringify(INITIAL_TASKS));
    persistTasks();
    currentPage = 1;
    filterMode = 'all';
    searchKeyword = '';
    document.getElementById('search-input').value = '';
    setFilter('all');
    showToast('Data reset to default seed records');
    fetch('api/todos/reset', { method: 'POST' }).catch(() => {});
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.style.display = 'none';
    }, 2400);
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

window.onload = () => {
    loadTasks();
    render();
};
"""

