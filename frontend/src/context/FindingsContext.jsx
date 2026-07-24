// frontend/src/context/FindingsContext.jsx

import { createContext, useContext, useReducer } from "react";

// 처음 전원을 켰을 때 자판기 재고 상태
const initialState = {
  findings: [],
  loading: false,
  error: null,  
};

// useReducer = 규칙이 정해진 자판기.
// 재고 칸을 아무나 바꾸지 못하고, 반드시 정해진 "버튼(action)"을 눌러야만
// 정해진 규칙대로 상태가 바뀜 → 나중에 "왜 이렇게 바뀌었지?" 추적이 쉬워짐
function findingsReducer(state, action) {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, loading: true, error: null };
      
    case "FETCH_SUCCESS":
      return { ...state, loading: false, findings: action.payload };
      
    case "FETCH_ERROR":
      return { ...state, loading: false, error: action.payload };
      
    case "UPDATE_FINDING_STATUS":
      // 승인/거부를 눌렀을 때 목록 전체를 다시 불러오지 않고,
      // 그 finding 하나만 콕 집어서 그 자리에서 바로 교체 (화면 즉각 반응용)
      return {
        ...state,
        findings: state.findings.map((f) =>
          f.id === action.payload.id
            ? { ...f, status: action.payload.status }
            : f  
        ),
      };
    
    default:
      return state;    
  }  
}

const FindingsContext = createContext(null);

// Provider = 방송국. Provider로 감싼 하위 트리 전체가
// "findings 상태"라는 채널을 동시에 들을 수 있게 됨
export function FindingsProvider({children}) {
  const [state, dispatch] = useReducer(findingsReducer, initialState);
  
  return (
    <FindingsContext.Provider value={{ state, dispatch }}>
      {children}  
    </FindingsContext.Provider>
  );
}

// Provider 밖에서 실수로 쓰는 걸 막기 위한 안전장치용 커스텀 훅
export function useFindings() {
  const context = useContext(FindingsContext);
  if (!context) {
    throw new Error("useFindings는 FindingsProvider 안에서만 쓸 수 있습니다.")
  }
  return context;  
}
