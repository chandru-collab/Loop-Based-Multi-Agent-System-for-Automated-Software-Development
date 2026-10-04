import { useState, useEffect, useMemo, useCallback } from 'react';
import { Note, Tag } from '../types';
import { storageService } from '../services/storage';

export function useNotes() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [activeNoteId, setActiveNoteId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTagId, setSelectedTagId] = useState<string | null>(null);

  // Load initial notes and tags from storage on mount
  useEffect(() => {
    const loadedNotes = storageService.getNotes();
    const loadedTags = storageService.getTags();

    setNotes(loadedNotes);
    setTags(loadedTags);

    // Automatically select the first note if available and none selected
    if (loadedNotes.length > 0 && !activeNoteId) {
      setActiveNoteId(loadedNotes[0].id);
    }
  }, []);

  // Currently active note object
  const activeNote = useMemo(() => {
    return notes.find((note) => note.id === activeNoteId) || null;
  }, [notes, activeNoteId]);

  // Filtered notes based on search query and selected tag
  const filteredNotes = useMemo(() => {
    return notes.filter((note) => {
      // Tag filter
      if (selectedTagId) {
        const tagObj = tags.find((t) => t.id === selectedTagId);
        if (tagObj && !note.tags.includes(tagObj.name)) {
          return false;
        }
      }

      // Search filter
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        const matchesTitle = note.title.toLowerCase().includes(query);
        const matchesContent = note.content.toLowerCase().includes(query);
        const matchesTags = note.tags.some((t) => t.toLowerCase().includes(query));
        return matchesTitle || matchesContent || matchesTags;
      }

      return true;
    });
  }, [notes, tags, selectedTagId, searchQuery]);

  // Create a new note
  const createNote = useCallback(() => {
    const newNote: Note = {
      id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
      title: 'Untitled Note',
      content: '# Untitled Note\n\nStart writing your markdown here...',
      tags: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    const updatedNotes = [newNote, ...notes];
    setNotes(updatedNotes);
    storageService.saveNotes(updatedNotes);
    setActiveNoteId(newNote.id);
    return newNote;
  }, [notes]);

  // Update an existing note
  const updateNote = useCallback((id: string, updates: Partial<Pick<Note, 'title' | 'content' | 'tags'>>) => {
    const updatedNotes = notes.map((note) => {
      if (note.id === id) {
        return {
          ...note,
          ...updates,
          updatedAt: Date.now(),
        };
      }
      return note;
    });

    setNotes(updatedNotes);
    storageService.saveNotes(updatedNotes);
  }, [notes]);

  // Delete a note
  const deleteNote = useCallback((id: string) => {
    const updatedNotes = notes.filter((note) => note.id !== id);
    setNotes(updatedNotes);
    storageService.saveNotes(updatedNotes);

    // If deleted note was active, select another one
    if (activeNoteId === id) {
      setActiveNoteId(updatedNotes.length > 0 ? updatedNotes[0].id : null);
    }
  }, [notes, activeNoteId]);

  // Create a new tag
  const createTag = useCallback((name: string, color: string = '#3b82f6') => {
    // Check if tag already exists (case-insensitive)
    const normalized = name.trim().toLowerCase();
    if (!normalized) return;

    const existing = tags.find((t) => t.name.toLowerCase() === normalized);
    if (existing) return;

    const newTag: Tag = {
      id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
      name: name.trim(),
      color,
    };

    const updatedTags = [...tags, newTag];
    setTags(updatedTags);
    storageService.saveTags(updatedTags);
  }, [tags]);

  // Delete a tag and remove it from all notes
  const deleteTag = useCallback((tagId: string) => {
    const tagToDelete = tags.find((t) => t.id === tagId);
    if (!tagToDelete) return;

    const updatedTags = tags.filter((t) => t.id !== tagId);
    setTags(updatedTags);
    storageService.saveTags(updatedTags);

    // Remove tag from notes
    const updatedNotes = notes.map((note) => {
      if (note.tags.includes(tagToDelete.name)) {
        return {
          ...note,
          tags: note.tags.filter((t) => t !== tagToDelete.name),
          updatedAt: Date.now(),
        };
      }
      return note;
    });

    setNotes(updatedNotes);
    storageService.saveNotes(updatedNotes);

    if (selectedTagId === tagId) {
      setSelectedTagId(null);
    }
  }, [tags, notes, selectedTagId]);

  return {
    notes,
    tags,
    activeNote,
    activeNoteId,
    filteredNotes,
    searchQuery,
    selectedTagId,
    setActiveNoteId,
    setSearchQuery,
    setSelectedTagId,
    createNote,
    updateNote,
    deleteNote,
    createTag,
    deleteTag,
  };
}
