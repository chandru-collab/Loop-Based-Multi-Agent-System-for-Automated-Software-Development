import React, { useState } from 'react';
import { Tag } from '../types';
import { Plus, Trash2, Tag as TagIcon, X } from 'lucide-react';

interface TagManagerProps {
  tags: Tag[];
  onAddTag: (name: string, color: string) => void;
  onDeleteTag: (id: string) => void;
  selectedTagId: string | null;
  onSelectTag: (id: string | null) => void;
}

const PRESET_COLORS = [
  '#EF4444', // Red
  '#F97316', // Orange
  '#F59E0B', // Amber
  '#10B981', // Emerald
  '#06B6D4', // Cyan
  '#3B82F6', // Blue
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#6B7280', // Gray
];

export const TagManager: React.FC<TagManagerProps> = ({
  tags,
  onAddTag,
  onDeleteTag,
  selectedTagId,
  onSelectTag,
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [selectedColor, setSelectedColor] = useState(PRESET_COLORS[0]);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagName.trim()) return;
    onAddTag(newTagName.trim(), selectedColor);
    setNewTagName('');
    setIsCreating(false);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
          <TagIcon className="w-3.5 h-3.5" />
          Tags
        </h3>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="p-1 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded transition-colors"
          title="Add Tag"
        >
          {isCreating ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="p-2 bg-gray-50 dark:bg-gray-800/55 rounded-lg space-y-2 border border-gray-200 dark:border-gray-700">
          <input
            type="text"
            placeholder="Tag name..."
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            className="w-full px-2.5 py-1 text-xs bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
            autoFocus
          />
          <div className="flex items-center gap-1 flex-wrap">
            {PRESET_COLORS.map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => setSelectedColor(color)}
                className={`w-4 h-4 rounded-full transition-transform ${
                  selectedColor === color ? 'scale-125 ring-2 ring-offset-1 ring-blue-500' : 'opacity-75 hover:opacity-100'
                }`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
          <button
            type="submit"
            className="w-full py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors"
          >
            Create Tag
          </button>
        </form>
      )}

      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => onSelectTag(null)}
          className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
            selectedTagId === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
          }`}
        >
          All Notes
        </button>
        {tags.map((tag) => {
          const isSelected = selectedTagId === tag.id;
          return (
            <div
              key={tag.id}
              className={`group flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                isSelected
                  ? 'ring-2 ring-offset-1 ring-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
              }`}
              style={isSelected ? { backgroundColor: tag.color } : {}}
            >
              <span
                onClick={() => onSelectTag(tag.id)}
                className="cursor-pointer flex items-center gap-1.5"
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: isSelected ? '#FFFFFF' : tag.color }}
                />
                {tag.name}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteTag(tag.id);
                }}
                className={`opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded ${
                  isSelected ? 'hover:bg-black/20 text-white' : 'hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-500 dark:text-gray-400'
                }`}
                title="Delete tag"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
