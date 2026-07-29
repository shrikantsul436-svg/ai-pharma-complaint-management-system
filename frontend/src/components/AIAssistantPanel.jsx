import React from 'react';
import { useSelector } from 'react-redux';
import FileUpload from './FileUpload.jsx';
import AssistantChat from './AssistantChat.jsx';

export default function AIAssistantPanel() {
  const { ingestStatus, ingestProgress, analysis } = useSelector((s) => s.complaint);

  return (
    <div className="card">
      <div className="assistant-header">
        <div className="assistant-title">✨ AI Complaint Intake Assistant</div>
        <span className="beta-badge">BETA</span>
      </div>

      <FileUpload />

      {ingestStatus !== 'idle' && (
        <div className="progress-section">
          <div className="progress-label">Extraction Progress</div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${ingestProgress}%` }} />
          </div>
          <div className="progress-caption">
            {ingestStatus === 'loading' &&
              'Analyzing document content and extracting key details… Please wait, this may take a few moments.'}
            {ingestStatus === 'succeeded' && `Extraction complete — ${ingestProgress}%.`}
            {ingestStatus === 'failed' && 'Extraction failed. Please try again or check the backend logs.'}
          </div>
        </div>
      )}

      {analysis && <AnalysisSummary analysis={analysis} />}

      <AssistantChat />
    </div>
  );
}

function AnalysisSummary({ analysis }) {
  const {
    completeness_score,
    missing_fields = [],
    summary,
    root_cause_suggestion,
    capa_recommendation,
    duplicate_of,
    duplicate_confidence,
  } = analysis;

  return (
    <div className="analysis-block">
      <h4>AI Copilot Risk Assessment</h4>

      {summary && <p style={{ margin: '0 0 8px' }}>{summary}</p>}

      {completeness_score != null && (
        <p style={{ margin: '0 0 6px' }}>
          <strong>Completeness:</strong> {completeness_score}%
          {missing_fields.length > 0 && (
            <span style={{ color: '#b91c1c' }}> — missing: {missing_fields.join(', ')}</span>
          )}
        </p>
      )}

      {root_cause_suggestion && (
        <p style={{ margin: '0 0 6px' }}>
          <strong>Root cause (AI suggestion):</strong> {root_cause_suggestion}
        </p>
      )}

      {capa_recommendation && (
        <p style={{ margin: '0 0 6px' }}>
          <strong>CAPA recommendation:</strong> {capa_recommendation}
        </p>
      )}

      {duplicate_of && (
        <p style={{ margin: 0, color: '#b45309' }}>
          <strong>⚠ Possible duplicate</strong> of complaint {duplicate_of}
          {duplicate_confidence != null && ` (${Math.round(duplicate_confidence * 100)}% confidence)`}
        </p>
      )}
    </div>
  );
}
