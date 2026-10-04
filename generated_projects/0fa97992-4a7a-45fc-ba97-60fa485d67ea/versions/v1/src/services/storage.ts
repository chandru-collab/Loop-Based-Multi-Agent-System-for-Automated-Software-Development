export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: number;
  updatedAt: number;
}

const STORAGE_KEY = 'notes';

export const getNotes = (): Note[] => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

export const saveNotes = (notes: Note[]): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
};

export const addNote = (note: Note): void => {
  const notes = getNotes();
  saveNotes([...notes, note]);
};

export const updateNote = (updatedNote: Note): void => {
  const notes = getNotes();
  saveNotes(notes.map(n => n.id === updatedNote.id ? updatedNote : n));
};

export const deleteNote = (id: string): void => {
  const notes = getNotes();
  saveNotes(notes.filter(n => n.id !== id));
};