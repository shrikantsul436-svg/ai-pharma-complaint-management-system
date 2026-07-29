import React from 'react';
import ComplaintForm from './components/ComplaintForm.jsx';
import AIAssistantPanel from './components/AIAssistantPanel.jsx';

export default function App() {
  return (
    <div className="app-shell">
      
      <div className="layout">
        <ComplaintForm />
        <AIAssistantPanel />
      </div>
    </div>
  );
}
