import React from 'react';
import { Note } from '../types';
import { Trash2, FileText } from 'lucide-react';

interface NoteItemProps {
  note: Note;
  isActive: boolean;
  onClick: (id: string) => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
}

export const NoteItem: React.FC<NoteItemProps> = ({ note, isActive, onClick, onDelete }) => {
  const formattedDate = new Date(note.updatedAt).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <div
      onClick={() => onClick(note.id)}
      className={`group p-4 border-b cursor-pointer transition-colors duration-200 ${
        isActive ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'hover:bg-gray-50 border-l-4 border-l-transparent'
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2 overflow-hidden">
          <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <h3 className="font-semibold text-gray-800 truncate">{note.title || 'Untitled Note'}</h3>
        </div>
        <button
          onClick={(e) => onDelete(note.id, e)}
          className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-opacity"
          aria-label="Delete note"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
      
      <p className="text-sm text-gray-500 truncate mb-3">
        {note.content.substring(0, 60) || 'No content...'}
      </p>

      <div className="flex flex-wrap gap-1">
        {note.tags.map((tag) => (
          <span
            key={tag}
            className="px-2 py-0.5 text-[10px] font-medium bg-gray-100 text-gray-600 rounded-full"
          >
            {tag}
          </span>
        ))}
        <span className="ml-auto text-[10px] text-gray-400">{formattedDate}</span>
      </div>
    </div>
  );
};