import { useEffect, useState } from 'react';
import { api } from '../api/client';

export function useTeams() {
  const [teams, setTeams] = useState([]);
  useEffect(() => {
    api.get('/teams').then((res) => setTeams(res.data.teams || []));
  }, []);
  return teams;
}

export async function predictMatch(payload) {
  const { data } = await api.post('/predict', payload);
  return data;
}
