import { create } from "zustand";

interface SceneState {
	isHovered: boolean;
	activeColor: string;
	rotationSpeed: number;
	// Actions
	setHovered: (hovered: boolean) => void;
	setActiveColor: (color: string) => void;
	setRotationSpeed: (speed: number) => void;
}

export const useSceneStore = create<SceneState>((set) => ({
	isHovered: false,
	activeColor: "#3b82f6", // Default Blue
	rotationSpeed: 1,

	setHovered: (hovered) => set({ isHovered: hovered }),
	setActiveColor: (color) => set({ activeColor: color }),
	setRotationSpeed: (speed) => set({ rotationSpeed: speed }),
})); // Zustand store for scene management
