import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import FormField from './FormField.jsx';
import { resetForm, saveComplaint } from '../store/complaintSlice';

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { id, status, saveStatus } = useSelector((s) => s.complaint);

  const handleSave = () => {
    if (!id) return;
    dispatch(saveComplaint());
  };

  return (
    <div className="card">
      <div className="form-header">
        <div>
          <h2 className="form-title">Log Customer Complaint</h2>
          <p className="form-subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className={`badge ${status === 'Pending Triage' ? 'pending' : 'review'}`}>{status}</span>
      </div>

      <Section title="1. Origin & Customer Details">
        <div className="field-row">
          <FormField field="complaint_source" label="Complaint Source" />
          <FormField field="customer_name" label="Customer Name" />
        </div>
      </Section>

      <Section title="2. Product & Batch Identification">
        <div className="field-row">
          <FormField field="product_name" label="Product Name" />
          <FormField field="product_strength_grade" label="Product Strength/Grade" />
        </div>
        <div className="field-row">
          <FormField field="batch_lot_number" label="Batch/Lot Number" />
          <FormField field="manufacturing_date" label="Manufacturing Date" type="date" />
        </div>
        <div className="field-row">
          <FormField field="expiry_date" label="Expiry Date" type="date" />
          <FormField field="quantity_affected" label="Quantity Affected" type="number" unit="kg" />
        </div>
      </Section>

      <Section title="3. Complaint Details">
        <div className="field-row">
          <FormField field="complaint_type" label="Complaint Type" />
          <FormField field="complaint_date" label="Complaint Date" type="date" />
        </div>
        <FormField field="detailed_description" label="Detailed Complaint Description" type="textarea" />
      </Section>

      <Section title="4. Initial Assessment & Priority">
        <div className="field-row">
          <FormField
            field="initial_severity"
            label="Initial Severity"
            type="select"
            options={['Critical', 'Major', 'Minor']}
          />
          <FormField field="priority" label="Priority" type="select" options={['High', 'Medium', 'Low']} />
        </div>
      </Section>

      <div className="form-actions">
        <button className="btn btn-secondary" onClick={() => dispatch(resetForm())}>
          ↺ Reset Form
        </button>
        <button className="btn btn-primary" disabled={!id || saveStatus === 'loading'} onClick={handleSave}>
          💾 {saveStatus === 'loading' ? 'Saving...' : 'Save Complaint'}
        </button>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="section">
      <div className="section-title">{title}</div>
      {children}
    </div>
  );
}
