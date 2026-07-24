// frontend/src/services/api.js

// 이 파일은 "백엔드에 전화를 거는 창구"
// 컴포넌트마다 fetch를 따로따로 쓰면 나중에 API 주소가 하나 바뀔 때 마다 여기저기 다 뒤져야 함.
// 따라서, 창구를 하나로 모아둠.

const API_BASE = "http://127.0.0.1:8000";

export async function getFindings(status = null) {
  const url = status
    ? `${API_BASE}/findings?status=${status}`
    : `${API_BASE}/findings`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    // 응답은 왔는데 내용이 에러인 상황 (404, 500 등)
    // → 택배는 도착했는데 상자 안에 "파손됨" 쪽지가 들어있는 경우
    throw new Error(`findings 불러오기 실패: ${response.status}`);
  }

  return response.json();
}
