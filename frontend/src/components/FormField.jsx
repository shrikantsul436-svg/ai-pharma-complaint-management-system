import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fieldChanged } from '../store/complaintSlice';

/**
 * One labeled input in the complaint form. Renders "Awaiting AI extraction..."
 * as a placeholder until the AI Assistant fills it in, at which point it gets
 * a light-blue background so the reviewer can see at a glance what the AI
 * populated vs what's still empty.
 */
export default function FormField({ field, label, type = 'text', options, unit }) {
  const dispatch = useDispatch();
  const value = useSelector((state) => state.complaint.fields[field]);
  const isFilled = value !== null && value !== undefined && value !== '';

  const handleChange = (e) => {
    dispatch(fieldChanged({ field, value: e.target.value }));
  };

  return (
    <div className="field">
      <label>{label}</label>
      {type === 'select' ? (
        <select className={isFilled ? 'ai-filled' : ''} value={value ?? ''} onChange={handleChange}>
          <option value="" disabled>
            Awaiting AI extraction...
          </option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea
          className={isFilled ? 'ai-filled' : ''}
          placeholder="Awaiting AI extraction..."
          value={value ?? ''}
          onChange={handleChange}
        />
      ) : (
        <div style={{ position: 'relative' }}>
          <input
            className={isFilled ? 'ai-filled' : ''}
            type={type}
            placeholder="Awaiting AI extraction..."
            value={value ?? ''}
            onChange={handleChange}
          />
          {unit && (
            <span style={{ position: 'absolute', right: 12, top: 9, fontSize: 12, color: '#9ca3af' }}>
              {unit}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
