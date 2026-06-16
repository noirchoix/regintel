const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1').replace(/\/$/, '');

async function parseResponse(res: Response) {
  const text = await res.text();

  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const message =
      (typeof data === 'object' && data?.detail) ||
      (typeof data === 'object' && data?.message) ||
      (typeof data === 'string' && data) ||
      `Request failed with status ${res.status}`;

    throw new Error(message);
  }

  return data;
}

export async function createAssessment(payload: unknown) {
  const res = await fetch(`${API_BASE}/assessments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  return parseResponse(res);
}

export async function generateReport(assessment_id: string) {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ assessment_id })
  });

  return parseResponse(res);
}