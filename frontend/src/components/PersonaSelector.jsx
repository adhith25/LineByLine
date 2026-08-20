import React from 'react';

const PERSONAS = [
  {
    id: 'academic',
    name: 'Academic',
    icon: '🎓',
    description: 'Structured CS study notes',
  },
  {
    id: 'story',
    name: 'Story',
    icon: '📖',
    description: 'Vivid narrative & characters',
  },
  {
    id: 'interview',
    name: 'Interview',
    icon: '🎯',
    description: 'Complexity & algorithmic edge',
  },
  {
    id: 'toddler',
    name: 'Toddler',
    icon: '🧸',
    description: 'Playground & ELI5 analogies',
  },
];

export default function PersonaSelector({ selectedPersona, onSelectPersona }) {
  return (
    <div className="persona-grid">
      {PERSONAS.map((p) => {
        const isActive = selectedPersona === p.id;
        return (
          <div
            key={p.id}
            className={`persona-card ${isActive ? 'active' : ''}`}
            onClick={() => onSelectPersona(p.id)}
          >
            <span className="persona-icon">{p.icon}</span>
            <span className="persona-name">{p.name}</span>
            <span className="persona-desc">{p.description}</span>
          </div>
        );
      })}
    </div>
  );
}
