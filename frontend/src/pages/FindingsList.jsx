// frontend/src/pages/FindingsList.jsx

import { useEffect } from "react";
import { useFindings } from "../context/FindingsContext";
import { getFindings } from "../services/api";

export default function FindingsList() {
  const { state, dispatch } = useFindings();
  const { findings, loading, error } = state;
  
  useEffect(() => {
    // 빈 배열 [] = "화면이 처음 열릴 때 딱 한번만 실행"
    // (리렌더링 될 때마다 서버에 매번 다시 물어보면 낭비)
    async function loadFindings() {
      dispatch({ type: "FETCH_START" });
      try {
        const data = await getFindings();
        dispatch({ type: "FETCH_SUCCESS", payload: data });
      } catch (err) {
        dispatch({ type: "FETCH_ERROR", payload: err.message });
      }  
    }
    loadFindings();
  }, []);

  if (loading) return <p>불러오는 중...</p>;
  if (error) return <p>에러: {error}</p>;

  return (
    <ul>
      {findings.map((f) => (
        <li key={f.id}>
          {f.file_path} — {f.status}   
        </li>
      ))}  
    </ul>
  );
}
