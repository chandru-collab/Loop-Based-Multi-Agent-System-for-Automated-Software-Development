import React from 'react';
import { Tag } from '../types';
import { Folder, Tag as TagIcon, Plus, Settings, Trash2 } from 'lucide-react';

interface SidebarProps {
  tags: Tag[];
  selectedTag: string | null;
  onSelectTag: (tagId: string | null) => void;
  onOpenTagManager: () => void;
  onNewNote: () => void;
  noteCount: number;
  untaggedCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  tags,
  selectedTag,
  onSelectTag,
  onOpenTagManager,
  onNewNote,
  noteCount,
  untaggedCount,
}) => {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen border-r border-slate-800 select-none">
      {/* App Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="bg-indigo-600 text-white p-2 rounded-lg font-bold shadow-md">
            <Folder className="w-5 h-5" />
          </div>
          <span className="font-bold text-lg text-white tracking-wide">MarkNote</span>
        </div>
      </div>

      {/* Action Button */}
      <div className="p-4">
        <button
          onClick={onNewNote}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center space-x-2 transition shadow-lg shadow-indigo-600/30"
        >
          <Plus className="w-5 h-5" />
          <span>New Note</span>
        </button>
      </div>

      {/* Navigation & Filters */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-6">
        {/* Views */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Library
          </h3>
          <div className="space-y-1">
            <button
              onClick={() => onSelectTag(null)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition ${
                selectedTag === null
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-250'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Folder className="w-4 h-4 text-indigo-400" />
                <span>All Notes</span>
              </div>
              <span className="bg-slate-800 text-slate-400 text-xs px-2 py-0.5 rounded-full">
                {noteCount}
              </span>
            </button>

            <button
              onClick={() => onSelectTag('untagged')}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition ${
                selectedTag === 'untagged'
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-250'
              }`}
            >
              <div className="flex items-center space-x-2">
                <TagIcon className="w-4 h-4 text-slate-400" />
                <span>Untagged</span>
              </div>
              <span className="bg-slate-800 text-slate-400 text-xs px-2 py-0.5 rounded-full">
                {untaggedCount}
              </span>
            </button>
          </div>
        </div>

        {/* Tags Section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Tags
            </h3>
            <button
              onClick={onOpenTagManager}
              className="text-slate-400 hover:text-white transition p-1 rounded"
              title="Manage Tags"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-1">
            {tags.length === 0 ? (
              <p className="text-xs text-slate-500 italic px-3 py-1">
                No tags created yet.
              </p>
            ) : (
              tags.map((tag) => (
                <button
                  key={tag.id}
                  onClick={() => onSelectTag(tag.id)}
                  className={`w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                    selectedTag === tag.id
                      ? 'bg-slate-800 text-white'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center space-x-2 overflow-hidden">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: tag.color }}
                    />
                    <span className="truncate">{tag.name}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        <span>Local Storage Persistence</span>
      </div>
    </aside>
  );
};
