import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface WorkspaceState {
  qualityMode?: 'fast' | 'hd';
  resolution: string;
  frameRate: number;
  compression: string;
  maskExpansion: Record<string, number>;
  maskErosion: Record<string, number>;
}

interface UndoRedoState {
  past: WorkspaceState[];
  present: WorkspaceState;
  future: WorkspaceState[];
  setSetting: (key: keyof WorkspaceState, value: any, faceId?: string) => void;
  undo: () => void;
  redo: () => void;
  reset: () => void;
  loadState: (state: WorkspaceState) => void;
}

const initialState: WorkspaceState = {
  qualityMode: 'hd',
  resolution: '1920x1080',
  frameRate: 60,
  compression: 'lossless',
  maskExpansion: {},
  maskErosion: {},
};

export const useWorkspaceStore = create<UndoRedoState>()(
  persist(
    (set) => ({
      past: [],
      present: initialState,
      future: [],
      setSetting: (key, value, faceId) => set((state) => {
        let newPresent = { ...state.present };
        
        if (key === 'maskExpansion' || key === 'maskErosion') {
          if (!faceId) return state; // Need faceId for masks
          newPresent[key] = {
            ...newPresent[key],
            [faceId]: value
          };
        } else {
          (newPresent as any)[key] = value;
        }
        return {
          past: [...state.past, state.present],
          present: newPresent,
          future: [],
        };
      }),
      undo: () => set((state) => {
        if (state.past.length === 0) return state;
        const previous = state.past[state.past.length - 1];
        const newPast = state.past.slice(0, state.past.length - 1);
        
        return {
          past: newPast,
          present: previous,
          future: [state.present, ...state.future],
        };
      }),
      redo: () => set((state) => {
        if (state.future.length === 0) return state;
        const next = state.future[0];
        const newFuture = state.future.slice(1);
        
        return {
          past: [...state.past, state.present],
          present: next,
          future: newFuture,
        };
      }),
      reset: () => set(() => ({
        past: [],
        present: initialState,
        future: [],
      })),
      loadState: (newState) => set(() => ({
        past: [],
        present: newState,
        future: []
      }))
    }),
    {
      name: 'neoface-workspace-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
