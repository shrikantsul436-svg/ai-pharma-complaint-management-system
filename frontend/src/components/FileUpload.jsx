import React, { useRef, useState } from 'react';
import { useDispatch } from 'react-redux';
import { ingestDocument, ingestText } from '../store/complaintSlice';

export default function FileUpload() {
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [showPaste, setShowPaste] = useState(false);
  const [pastedText, setPastedText] = useState('');

  const handleFiles = (files) => {
    const file = files?.[0];
    if (!file) return;
    dispatch(ingestDocument(file));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const handlePasteSubmit = () => {
    if (!pastedText.trim()) return;
    dispatch(ingestText(pastedText));
    setShowPaste(false);
  };

  return (
    <div>
      <div
        className={`dropzone ${dragOver ? 'dragover' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div style={{ fontSize: 22, marginBottom: 6 }}>☁️</div>
        Drag &amp; drop complaint document here
        <br />
        or <a>click to browse</a>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.eml"
          style={{ display: 'none' }}
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      <div className="or-divider">OR</div>

      <button className="paste-btn" onClick={() => setShowPaste((s) => !s)}>
        📄 Paste Complaint Text / Email
      </button>

      {showPaste && (
        <>
          <textarea
            className="paste-textarea"
            placeholder="Paste the complaint email or text here..."
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
          />
          <button className="btn btn-primary" style={{ marginTop: 8, width: '100%' }} onClick={handlePasteSubmit}>
            Analyze Text
          </button>
        </>
      )}

      <div className="hint-box">ⓘ Supported formats: PDF, DOCX, TXT, EML — Max file size: 10MB</div>
    </div>
  );
}
