import React from 'react';
import { Note, Tag } from '../types';
import { NoteItem } from './NoteItem';
import { FileText, Plus } from 'lucide-react';

interface NoteListProps {
  notes: Note[];
  tags: Tag[];
  selectedNoteId: string | null;
  onSelectNote: (noteId: string) => void;
  onCreateNote: () => void;
  onDeleteNote: (noteId: string, e: React.MouseEvent) => void;
}

export const NoteList: React.FC<NoteListProps> = ({
  notes,
  tags,
  selectedNoteId,
  onSelectNote,
  onCreateNote,
  onDeleteNote,
}) => {
  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      {/* Header with New Note button */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-slate-100">Notes</h2>
          <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
            {notes.length}
          </span>
        </div>
        <button
          onClick={onCreateNote}
          className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900"
          title="Create new note"
        >
          <Plus className="w-4 h-4" />
          <span>New Note</span>
        </button>
      </div>

      {/* Note items scrollable container */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
        {notes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center px-4">
            <FileText className="w-12 h-12 text-slate-600 mb-2 stroke-1" />
            <p className="text-slate-400 text-sm font-medium">No notes found</p>
            <p className="text-slate-500 text-xs mt-1">
              Create a new note or adjust your search filter.
            </p>
          </div>
        ) : (
          notes.map((note) => (
            <NoteItem
              key={note.id}
              note={note}
              tags={tags}
              isSelected={note.id === selectedNoteId}
              onSelect={() => onSelectNote(note.id)}
              onDelete={(e) => onDeleteNote(note.id, e)}
            />
          ))
        )}
      </div>
    </div>
  );
};
