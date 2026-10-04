let notes = [
    {
        id: '1',
        title: 'Welcome to MarkNote',
        content: '# 🚀 Welcome to MarkNote!\n\nThis is a real-time **Markdown Notes** application.\n\n### ✨ Features\n- Live Markdown Parsing\n- Instant Preview\n- Responsive Layout\n\n```javascript\nconst note = "Happy writing!";\nconsole.log(note);\n```\n\n> "Simplicity is the soul of efficiency."'
    },
    {
        id: '2',
        title: 'Project Roadmap',
        content: '# 📌 Project Roadmap\n\n- [x] Initial agent loop setup\n- [x] Requirement analysis\n- [x] Live interactive preview\n- [ ] Release zip download'
    }
];

let activeNoteId = '1';

function renderNotesList() {
    const listEl = document.getElementById('notes-list');
    listEl.innerHTML = notes.map(n => `
        <div class="note-item ${n.id === activeNoteId ? 'active' : ''}" onclick="selectNote('${n.id}')">
            <h4>${n.title || 'Untitled Note'}</h4>
            <p>${n.content.slice(0, 40) || 'Empty note...'}</p>
        </div>
    `).join('');
}

function parseMarkdown(md) {
    if (!md) return '';
    return md
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
        .replace(/\*(.*)\*/gim, '<i>$1</i>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/\n\n/gim, '<br/><br/>')
        .replace(/\n/gim, '<br/>');
}

function selectNote(id) {
    activeNoteId = id;
    const note = notes.find(n => n.id === id);
    if (note) {
        document.getElementById('note-title').value = note.title;
        document.getElementById('note-content').value = note.content;
        document.getElementById('preview-output').innerHTML = parseMarkdown(note.content);
    }
    renderNotesList();
}

function createNote() {
    const newNote = {
        id: String(Date.now()),
        title: 'New Note',
        content: '# New Note\n\nStart typing your content here...'
    };
    notes.unshift(newNote);
    selectNote(newNote.id);
}

function updateCurrentNote() {
    const note = notes.find(n => n.id === activeNoteId);
    if (note) {
        note.title = document.getElementById('note-title').value;
        note.content = document.getElementById('note-content').value;
        document.getElementById('preview-output').innerHTML = parseMarkdown(note.content);
        renderNotesList();
    }
}

function deleteCurrentNote() {
    if (notes.length <= 1) {
        alert('Cannot delete the last note.');
        return;
    }
    notes = notes.filter(n => n.id !== activeNoteId);
    selectNote(notes[0].id);
}

window.onload = () => {
    selectNote(activeNoteId);
};