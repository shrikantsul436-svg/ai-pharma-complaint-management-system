import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/client';

const emptyFields = {
  complaint_source: null,
  customer_name: null,
  product_name: null,
  product_strength_grade: null,
  batch_lot_number: null,
  manufacturing_date: null,
  expiry_date: null,
  quantity_affected: null,
  quantity_unit: null,
  complaint_type: null,
  complaint_date: null,
  detailed_description: null,
  initial_severity: null,
  priority: null,
};

const initialState = {
  id: null,
  status: 'Pending Triage',
  fields: { ...emptyFields },
  analysis: null, // { completeness_score, missing_fields, summary, root_cause_suggestion, capa_recommendation, duplicate_of, duplicate_confidence }
  ingestStatus: 'idle', // idle | loading | succeeded | failed
  ingestProgress: 0,
  saveStatus: 'idle',
  error: null,
};

export const ingestDocument = createAsyncThunk('complaint/ingestDocument', async (file) => {
  return api.ingestDocument(file);
});

export const ingestText = createAsyncThunk('complaint/ingestText', async (text) => {
  return api.ingestText(text);
});

export const saveComplaint = createAsyncThunk('complaint/save', async (_, { getState }) => {
  const { id, fields } = getState().complaint;
  return api.saveComplaint(id, fields);
});

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    fieldChanged(state, action) {
      const { field, value } = action.payload;
      state.fields[field] = value;
    },
    resetForm() {
      return { ...initialState, fields: { ...emptyFields } };
    },
    setIngestProgress(state, action) {
      state.ingestProgress = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(ingestDocument.pending, (state) => {
        state.ingestStatus = 'loading';
        state.ingestProgress = 5;
        state.error = null;
      })
      .addCase(ingestText.pending, (state) => {
        state.ingestStatus = 'loading';
        state.ingestProgress = 5;
        state.error = null;
      })
      .addCase(ingestDocument.fulfilled, applyIngestResult)
      .addCase(ingestText.fulfilled, applyIngestResult)
      .addCase(ingestDocument.rejected, handleIngestError)
      .addCase(ingestText.rejected, handleIngestError)
      .addCase(saveComplaint.pending, (state) => {
        state.saveStatus = 'loading';
      })
      .addCase(saveComplaint.fulfilled, (state) => {
        state.saveStatus = 'succeeded';
        state.status = 'Under Review';
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.saveStatus = 'failed';
        state.error = action.error.message;
      });
  },
});

function applyIngestResult(state, action) {
  state.ingestStatus = 'succeeded';
  state.ingestProgress = 100;
  state.id = action.payload.complaint_id;
  state.fields = { ...state.fields, ...action.payload.extracted };
  state.analysis = action.payload.analysis;
}

function handleIngestError(state, action) {
  state.ingestStatus = 'failed';
  state.ingestProgress = 0;
  state.error = action.error.message;
}

export const { fieldChanged, resetForm, setIngestProgress } = complaintSlice.actions;
export default complaintSlice.reducer;
