import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendChatMessage, userMessageSent } from '../store/assistantSlice';

export default function AssistantChat() {
  const dispatch = useDispatch();
  const { messages, chatStatus } = useSelector((s) => s.assistant);
  const complaintId = useSelector((s) => s.complaint.id);
  const [text, setText] = useState('');

  const handleSend = () => {
    if (!text.trim()) return;
    dispatch(userMessageSent(text));
    dispatch(sendChatMessage({ complaintId, message: text }));
    setText('');
  };

  return (
    <div className="chat-section">
      <div className="chat-title">AI Assistant</div>
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        {chatStatus === 'loading' && <div className="chat-bubble assistant">Thinking…</div>}
      </div>
      <div className="chat-input-row">
        <input
          placeholder={complaintId ? 'Ask me anything about this complaint...' : 'Upload a document first...'}
          value={text}
          disabled={!complaintId}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="chat-send-btn" onClick={handleSend} disabled={!complaintId}>
          ➤
        </button>
      </div>
      <div className="chat-disclaimer">AI responses may contain errors. Please verify information.</div>
    </div>
  );
}
