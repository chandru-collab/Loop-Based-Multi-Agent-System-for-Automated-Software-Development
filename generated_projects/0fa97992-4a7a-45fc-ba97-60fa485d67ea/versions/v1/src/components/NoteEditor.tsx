import React from 'react';
import { Note } from '../types';

interface NoteEditorProps {
  note: Note;
  onChange: (updatedNote: Note) => void;
}

/**
 * NoteEditor component provides a controlled textarea for markdown input.
 * It triggers updates on every keystroke to enable live preview functionality.
 */
export const NoteEditor: React.FC<NoteEditorProps> = ({ note, onChange }) => {
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...note,
      title: e.target.value,
      updatedAt: Date.now(),
    });
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange({
      ...note,
      content: e.target.value,
      updatedAt: Date.now(),
    });
  };

  return (
    <div className="flex flex-col h-full w-full p-4 space-y-4">
      <input
        type="text"
        value={note.title}
        onChange={handleTitleChange}
        placeholder="Note Title"
        className="w-full text-2xl font-bold p-2 border-b border-gray-300 focus:outline-none focus:border-blue-500 transition-colors"
        aria-label="Note Title"
      />
      <textarea
        value={note.content}
        onChange={handleContentChange}
        placeholder="Start writing your markdown note here..."
        className="flex-grow w-full p-4 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
        aria-label="Markdown Content"
      />
      <div className="text-xs text-gray-400 text-right">
        Last updated: {new Date(note.updatedAt).toLocaleString()}
      </div>
    </div>
  );
};
