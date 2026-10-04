import React, { useState, useEffect } from 'react';
import { getNotes, saveNotes, Note } from './services/storage';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Plus, Trash2, Search } from 'lucide-react';

export default function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    setNotes(getNotes());
  }, []);

  const activeNote = notes.find(n => n.id === selectedId);

  const handleSave = (updated: Note) => {
    const newNotes = notes.map(n => n.id === updated.id ? updated : n);
    setNotes(newNotes);
    saveNotes(newNotes);
  };

  const filteredNotes = notes.filter(n => 
    n.title.toLowerCase().includes(search.toLowerCase()) || 
    n.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 bg-white border-r p-4">
        <div className="flex items-center mb-4">
          <Search className="w-4 h-4 mr-2" />
          <input 
            className="border p-1 w-full" 
            placeholder="Search..." 
            value={search} 
            onChange={(e) => setSearch(e.target.value)} 
          />
        </div>
        {filteredNotes.map(n => (
          <div key={n.id} onClick={() => setSelectedId(n.id)} className="cursor-pointer p-2 hover:bg-gray-200">
            {n.title}
          </div>
        ))}
      </div>
      <div className="flex-1 p-8">
        {activeNote ? (
          <div className="flex flex-col gap-4">
            <input 
              className="text-2xl font-bold p-2" 
              value={activeNote.title} 
              onChange={(e) => handleSave({...activeNote, title: e.target.value, updatedAt: Date.now()})} 
            />
            <textarea 
              className="h-64 p-2" 
              value={activeNote.content} 
              onChange={(e) => handleSave({...activeNote, content: e.target.value, updatedAt: Date.now()})} 
            />
            <div 
              className="prose" 
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(activeNote.content)) }} 
            />
          </div>
        ) : (
          <p>Select a note</p>
        )}
      </div>
    </div>
  );
}