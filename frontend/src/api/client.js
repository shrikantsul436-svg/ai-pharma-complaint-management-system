const BASE = import.meta.env.VITE_API_URL;

async function handle(res) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  ingestDocument: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/ai/ingest/document`, { method: 'POST', body: form }).then(handle);
  },

  ingestText: (text) => {
    const form = new FormData();
    form.append('text', text);
    return fetch(`${BASE}/ai/ingest/text`, { method: 'POST', body: form }).then(handle);
  },

  chat: (complaintId, message) =>
    fetch(`${BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ complaint_id: complaintId, message }),
    }).then(handle),

  saveComplaint: (complaintId, fields) =>
    fetch(`${BASE}/complaints/${complaintId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fields),
    }).then(handle),

  listComplaints: () => fetch(`${BASE}/complaints`).then(handle),
};
