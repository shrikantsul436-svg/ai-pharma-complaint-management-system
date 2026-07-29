import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../api/client';

const initialState = {
  messages: [
    {
      role: 'assistant',
      text: 'Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.',
    },
  ],
  chatStatus: 'idle',
};

export const sendChatMessage = createAsyncThunk(
  'assistant/sendChatMessage',
  async ({ complaintId, message }) => {
    const res = await api.chat(complaintId, message);
    return res.reply;
  }
);

const assistantSlice = createSlice({
  name: 'assistant',
  initialState,
  reducers: {
    userMessageSent(state, action) {
      state.messages.push({ role: 'user', text: action.payload });
    },
    assistantMessageAdded(state, action) {
      state.messages.push({ role: 'assistant', text: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.chatStatus = 'loading';
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.chatStatus = 'idle';
        state.messages.push({ role: 'assistant', text: action.payload });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.chatStatus = 'idle';
        state.messages.push({
          role: 'assistant',
          text: `Sorry, I ran into an error: ${action.error.message}`,
        });
      });
  },
});

export const { userMessageSent, assistantMessageAdded } = assistantSlice.actions;
export default assistantSlice.reducer;
