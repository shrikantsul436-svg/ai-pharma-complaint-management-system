import { configureStore } from '@reduxjs/toolkit';
import complaintReducer from './complaintSlice';
import assistantReducer from './assistantSlice';

export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
    assistant: assistantReducer,
  },
});
